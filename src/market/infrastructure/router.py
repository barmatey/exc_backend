from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from loguru import logger

from src import db

from .schema import *
from .bootstrap import Bootstrap
from ...base.repo.repository import OrderBy


async def get_market(ticker: Ticker) -> domain.Market:
    async with db.get_as() as session:
        boot = Bootstrap(session)
        market = await boot.get_command_factory().get_market_by_ticker(ticker).execute()
        return market


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, key, websocket: WebSocket):
        await websocket.accept()
        if self.active_connections.get(key) is None:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)
        logger.debug(f'current connections: {len(self.active_connections[key])}')

    def disconnect(self, key, websocket: WebSocket):
        self.active_connections[key].remove(websocket)

    async def broadcast(self, key, message: dict):
        if self.active_connections.get(key) is not None:
            for connection in self.active_connections[key]:
                await connection.send_json(message)

    @staticmethod
    async def send_personal_message(message: dict, websocket: WebSocket):
        await websocket.send_json(message)


market_manager = ConnectionManager()
trs_manager = ConnectionManager()
order_manager = ConnectionManager()
position_manager = ConnectionManager()

router_market = APIRouter(
    prefix='/market',
    tags=['Market'],
)


@router_market.websocket("/ws/{ticker}")
async def market_websocket_endpoint(websocket: WebSocket, ticker: str):
    market = MarketSchema.from_entity(await get_market(ticker))
    await market_manager.connect(ticker, websocket)
    await market_manager.send_personal_message(market.model_dump(), websocket)
    try:
        while True:
            _data = await websocket.receive_text()
    except WebSocketDisconnect:
        market_manager.disconnect(ticker, websocket)


router_position = APIRouter(
    prefix='/position',
    tags=['Position'],
)


@router_position.websocket("/ws/{account_uuid}")
async def account_websocket_endpoint(websocket: WebSocket, account_uuid: str):
    await position_manager.connect(account_uuid, websocket)
    try:
        while True:
            _data = await websocket.receive_text()
    except WebSocketDisconnect:
        position_manager.disconnect(account_uuid, websocket)


@router_position.get("/{account_uuid}")
async def get_account_positions(account_uuid: UUID, get_as=Depends(db.get_as)) -> list[PositionSchema]:
    async with get_as as session:
        boot = Bootstrap(session)
        positions = await boot.get_command_factory().get_account_positions(account_uuid).execute()
        return [PositionSchema.from_entity(x) for x in positions]


router_order = APIRouter(
    prefix='/order',
    tags=['Order'],
)


@router_order.websocket("/ws/{account_uuid}")
async def order_websocket_endpoint(websocket: WebSocket, account_uuid: str):
    await order_manager.connect(account_uuid, websocket)
    try:
        while True:
            _data = await websocket.receive_text()
    except WebSocketDisconnect:
        order_manager.disconnect(account_uuid, websocket)


@router_order.post("/")
async def create_order(order: OrderSchema, get_as=Depends(db.get_as)) -> OrderSchema:
    async with get_as as session:
        boot = Bootstrap(session)
        cmd = boot.get_command_factory().send_order(order.to_entity())
        market = await cmd.execute()
        await boot.get_eventbus().run()
        await session.commit()

        await market_manager.broadcast(order.ticker, MarketSchema.from_entity(market).model_dump())
        for trs in market.transactions:
            data = TransactionSchema.from_entity(trs).model_dump()
            await trs_manager.broadcast(order.ticker, data)
            await position_manager.broadcast(trs.buyer, data)
            await position_manager.broadcast(trs.seller, data)
        for order in market.orders:
            await order_manager.broadcast(str(order.account), OrderSchema.from_entity(order).model_dump())
        return order


@router_order.get("/{account_uuid}")
async def get_account_orders(account_uuid: UUID, get_as=Depends(db.get_as)) -> list[OrderSchema]:
    async with get_as as session:
        boot = Bootstrap(session)
        cmd = boot.get_command_factory().get_many_orders({"account.uuid": str(account_uuid)})
        orders = await cmd.execute()
        return [OrderSchema.from_entity(x) for x in orders]


@router_order.patch("/cancel")
async def cancel_order(order: OrderSchema):
    async with db.get_as() as session:
        order.status = 'CANCELED'
        boot = Bootstrap(session)
        market = await boot.get_command_factory().cancel_order(order.to_entity()).execute()
        await boot.get_eventbus().run()
        await session.commit()
        await market_manager.broadcast(order.ticker, MarketSchema.from_entity(market).model_dump())
        await order_manager.broadcast(str(order.account), order.model_dump())


router_transaction = APIRouter(
    prefix='/transaction',
    tags=['Transaction'],
)


@router_transaction.websocket("/ws/{ticker}")
async def trs_websocket_endpoint(websocket: WebSocket, ticker: str):
    await trs_manager.connect(ticker, websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        trs_manager.disconnect(ticker, websocket)


@router_transaction.get("/{account_uuid}")
async def get_account_transactions(account_uuid: UUID, get_as=Depends(db.get_as)) -> list[TransactionSchema]:
    async with get_as as session:
        boot = Bootstrap(session)
        one = await boot.get_command_factory().get_many_transactions({'buyer.uuid': str(account_uuid)}).execute()
        two = await boot.get_command_factory().get_many_transactions({'seller.uuid': str(account_uuid)}).execute()
        transactions = one + two
        return [TransactionSchema.from_entity(x) for x in transactions]


@router_transaction.get("/")
async def get_many_transactions(
        ticker: Ticker = None,
        slice_from: int = None,
        slice_to: int = None,
        order_by: str = None,
        asc: bool = True,
        get_as=Depends(db.get_as),
):
    filter_by = {'ticker': ticker} if ticker else None
    order_by = OrderBy(order_by, asc) if order_by else None

    async with get_as as session:
        boot = Bootstrap(session)
        cmd = boot.get_command_factory().get_many_transactions(filter_by, order_by, slice_from, slice_to)
        transactions = await cmd.execute()
        return [TransactionSchema.from_entity(x) for x in transactions]

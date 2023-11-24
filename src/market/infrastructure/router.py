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


async def send_order(order: domain.Order) -> MarketSchema:
    async with db.get_as() as session:
        boot = Bootstrap(session)
        market = await boot.get_command_factory().send_order(order).execute()
        await boot.get_eventbus().run()
        await session.commit()
        return MarketSchema.from_entity(market)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug(f'current connections: {len(self.active_connections)}')

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

    @staticmethod
    async def send_personal_message(message: dict, websocket: WebSocket):
        await websocket.send_json(message)


def manager():
    data = {}

    def get(key: str) -> ConnectionManager:
        if data.get(key) is None:
            data[key] = ConnectionManager()
        return data[key]

    return get


market_manager = manager()
trs_manager = manager()

router_market = APIRouter(
    prefix='/market',
    tags=['Market'],
)


@router_market.websocket("/ws/{ticker}")
async def websocket_endpoint(websocket: WebSocket, ticker: str):
    market = MarketSchema.from_entity(await get_market(ticker))
    await market_manager(ticker).connect(websocket)
    await market_manager(ticker).send_personal_message(market.model_dump(), websocket)
    try:
        while True:
            _data = await websocket.receive_text()
    except WebSocketDisconnect:
        market_manager(ticker).disconnect(websocket)


router_order = APIRouter(
    prefix='/order',
    tags=['Order'],
)

order_manager = manager()


@router_order.websocket("/ws/{account_uuid}")
async def order_websocket_endpoint(websocket: WebSocket, account_uuid: str):
    await market_manager(account_uuid).connect(websocket)
    try:
        while True:
            _data = await websocket.receive_text()
    except WebSocketDisconnect:
        market_manager(account_uuid).disconnect(websocket)


@router_order.post("/")
async def create_order(order: OrderSchema, get_as=Depends(db.get_as)) -> OrderSchema:
    async with get_as as session:
        boot = Bootstrap(session)
        cmd = boot.get_command_factory().send_order(order.to_entity())
        market = await cmd.execute()
        await boot.get_eventbus().run()
        await session.commit()
        await market_manager(order.ticker).broadcast(MarketSchema.from_entity(market).model_dump())
        for trs in market.transactions:
            await trs_manager(order.ticker).broadcast(TransactionSchema.from_entity(trs).model_dump())
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
        boot = Bootstrap(session)
        market = await boot.get_command_factory().cancel_order(order.to_entity()).execute()
        await boot.get_eventbus().run()
        await session.commit()
        await market_manager(order.ticker).broadcast(MarketSchema.from_entity(market).model_dump())


router_transaction = APIRouter(
    prefix='/transaction',
    tags=['Transaction'],
)


@router_transaction.websocket("/ws/{ticker}")
async def trs_websocket_endpoint(websocket: WebSocket, ticker: str):
    mng = trs_manager(ticker)
    await mng.connect(websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        mng.disconnect(websocket)


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

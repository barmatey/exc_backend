from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from loguru import logger

from src import db

from .schema import *
from .bootstrap import Bootstrap


async def get_market(ticker: Ticker) -> domain.Market:
    async with db.get_as() as session:
        boot = Bootstrap(session)
        market = await boot.get_command_factory().get_market_by_ticker(ticker).execute()
        return market


async def send_order(order: domain.Order) -> domain.Market:
    async with db.get_as() as session:
        boot = Bootstrap(session)
        market = await boot.get_command_factory().send_order(order).execute()
        await boot.get_eventbus().run()
        await session.commit()
        return market


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


manager = ConnectionManager()

router_market = APIRouter(
    prefix='/market',
    tags=['Market'],
)


@router_market.websocket("/ws/{ticker}")
async def websocket_endpoint(websocket: WebSocket, ticker: str):
    market = MarketSchema.from_entity(await get_market(ticker))
    await manager.connect(websocket)
    await manager.send_personal_message(market.model_dump(), websocket)
    try:
        while True:
            data = await websocket.receive_json()
            market = await send_order(order=domain.Order(**data))
            await manager.broadcast(MarketSchema.from_entity(market).model_dump())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    # except Exception as err:
    #     logger.error(f'{err}')


router_order = APIRouter(
    prefix='/order',
    tags=['Order'],
)


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
        await manager.broadcast(MarketSchema.from_entity(market).model_dump())


router_transaction = APIRouter(
    prefix='/transaction',
    tags=['Transaction'],
)


@router_transaction.get("/")
async def get_account_transactions(account_uuid: UUID, get_as=Depends(db.get_as)) -> list[TransactionSchema]:
    async with get_as as session:
        boot = Bootstrap(session)
        one = await boot.get_command_factory().get_many_transactions({'buyer.uuid': str(account_uuid)}).execute()
        two = await boot.get_command_factory().get_many_transactions({'seller.uuid': str(account_uuid)}).execute()
        transactions = one + two
        return [TransactionSchema.from_entity(x) for x in transactions]

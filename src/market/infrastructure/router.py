from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Request

from src import db
from src.core import Ticker

from .schema import *
from .bootstrap import Bootstrap

router_market = APIRouter(
    prefix='/market',
    tags=['Market'],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

    @staticmethod
    async def send_personal_message(message: dict, websocket: WebSocket):
        await websocket.send_json(message)


manager = ConnectionManager()


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

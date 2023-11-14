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

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


async def get_market(ticker: Ticker) -> MarketSchema:
    async with db.get_as() as session:
        boot = Bootstrap(session)
        market_service = boot.get_market_service()
        market = await market_service.get_market_by_ticker(ticker)
        return MarketSchema.from_market(market)


async def send_order(order: domain.Order) -> domain.Market:
    async with db.get_as() as session:
        boot = Bootstrap(session)
        market_service = boot.get_market_service()
        market = await market_service.get_market_by_ticker(order.ticker)
        market.send_order(order)

        queue = boot.get_queue()
        queue.extend(market.events.parse_events())

        bus = boot.get_eventbus()
        await bus.run()

        await session.commit()
        return market


@router_market.websocket("/ws/{ticker}")
async def websocket_endpoint(websocket: WebSocket, ticker: str):
    market = await get_market('string')
    await manager.connect(websocket)
    await manager.broadcast(market.model_dump())
    try:
        while True:
            data = await websocket.receive_json()
            market = await send_order(order=domain.Order(**data))
            await manager.broadcast(MarketSchema.from_market(market).model_dump())
    except WebSocketDisconnect:
        manager.disconnect(websocket)

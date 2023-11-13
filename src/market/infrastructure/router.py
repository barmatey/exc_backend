from pathlib import Path

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from src import db
from src.core import Ticker

from .schema import *
from .bootstrap import Bootstrap

router_order = APIRouter(
    prefix='/order',
    tags=['Order'],
)


@router_order.post('/')
async def create_order(data: OrderSchema, get_as=Depends(db.get_as)) -> OrderSchema:
    async with get_as as session:
        boot = Bootstrap(session)
        order_service = boot.get_order_service()
        result = await order_service.create_order(data.to_entity())
        await session.commit()
        return result


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

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

templates = Jinja2Templates(directory=Path("D:/Projects/Python/Exchange/backend/src/temp"))


# @router_market.get('/{ticker}')
# async def get_market(ticker: Ticker, get_as=Depends(db.get_as)) -> MarketSchema:
#     async with get_as as session:
#         boot = Bootstrap(session)
#         market_service = boot.get_market_service()
#         market = await market_service.get_market_by_ticker(ticker)
#         return MarketSchema.from_market(market)


@router_market.get("/")
async def get(request: Request):
    return templates.TemplateResponse("template.html", {'request': request})


@router_market.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            print(data, type(data))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

from fastapi import APIRouter, Depends

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


@router_market.post('/')
async def create_market(ticker: Ticker, get_as=Depends(db.get_as)) -> MarketSchema:
    raise NotImplemented


@router_market.get('/{ticker}')
async def get_market(ticker: Ticker, get_as=Depends(db.get_as)) -> MarketSchema:
    async with get_as as session:
        boot = Bootstrap(session)
        market_service = boot.get_market_service()
        market = await market_service.get_market_by_ticker(ticker)
        return MarketSchema.from_market(market)

from abc import ABC
from typing import Optional

from src.base.repo import Repository
from ..base.repo.repository import OrderBy

from ..core import Ticker
from . import domain


class OrderService:
    def __init__(self, repo: Repository[domain.Order]):
        self._repo = repo

    async def get_orders(self, filter_by: dict, order_by: OrderBy = None) -> list[domain.Order]:
        return await self._repo.get_many(filter_by, order_by)

    async def create_order(self, order: domain.Order) -> domain.Order:
        await self._repo.add_many([order])
        return order


class MarketService:
    def __init__(self, order_repo: Repository[domain.Order]):
        self._order_repo = order_repo

    async def get_market_by_ticker(self, ticker: Ticker) -> domain.Market:
        orders = await self._order_repo.get_many(filter_by={'ticker': ticker, 'status': 'PENDING'})
        market = domain.Market(ticker=ticker, orders=orders)
        return market

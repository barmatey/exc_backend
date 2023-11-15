from abc import ABC
from typing import Optional

from src.base.repo import Repository
from ..base.repo.repository import OrderBy

from ..core import Ticker
from . import domain


class MarketService:
    def __init__(self, order_repo: Repository[domain.Order], transaction_repo: Repository[domain.Transaction]):
        self._order_repo = order_repo
        self._transaction_repo = transaction_repo

    async def get_market_by_ticker(self, ticker: Ticker) -> domain.Market:
        orders = await self._order_repo.get_many(filter_by={'ticker': ticker, 'status': 'PENDING'})
        transactions = await self._transaction_repo.get_many({'ticker': ticker}, OrderBy('date', asc=True), 0, 100)
        market = domain.Market(ticker=ticker, orders=orders, transactions=transactions)
        return market

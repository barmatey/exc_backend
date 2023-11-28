from typing import Literal, TypedDict
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.base.model import Entity
from src.core import Ticker

DealStatus = Literal['PROCESSING', 'CLOSED']
DealDirection = Literal['BUY', 'SELL']


class InnerTransaction(BaseModel):
    direction: DealDirection
    price: float
    quantity: int
    model_config = ConfigDict(frozen=True)


class Deal:
    def __init__(
            self,
            account: UUID,
            ticker: Ticker,
            status: DealStatus,
            transactions: list[InnerTransaction],
    ):
        self._account = account
        self._ticker = ticker
        self._status = status
        self._transactions = transactions

    @property
    def average_price(self) -> float:
        price = 0
        quantity = 0
        for trs in self._transactions:
            if trs.direction == 'BUY':
                price += trs.price
                quantity += trs.quantity
            else:
                price -= trs.price
                quantity -= trs.quantity
        return price / quantity

    @property
    def quantity(self) -> int:
        result = 0
        for trs in self._transactions:
            result = result + trs.quantity if trs.direction == 'BUY' else result - trs.quantity
        return result

    def append_transaction(self, trs: InnerTransaction):
        self._transactions.append(trs)

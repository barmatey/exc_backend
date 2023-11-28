from typing import Literal, TypedDict
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, PrivateAttr

from src.base.model import Entity
from src.core import Ticker

DealStatus = Literal['PROCESSING', 'CLOSED']
DealDirection = Literal['BUY', 'SELL']


class InnerTransaction(BaseModel):
    direction: DealDirection
    price: float
    quantity: int
    model_config = ConfigDict(frozen=True)


class Deal(Entity):
    account: UUID
    ticker: Ticker
    status: DealStatus
    _transactions = PrivateAttr(default_factory=list)

    def __init__(self, transactions: list[InnerTransaction] = None, **data):
        super().__init__(**data)
        self._transactions = transactions if transactions is not None else []

    @property
    def transactions(self) -> list[InnerTransaction]:
        return self._transactions

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

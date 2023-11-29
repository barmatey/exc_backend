from typing import Literal, TypedDict
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, PrivateAttr, Field

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
    weighted_price: float
    total_quantity: int

    def append_transaction(self, trs: InnerTransaction):
        self.weighted_price += trs.price * trs.quantity
        self.total_quantity += trs.quantity

    @property
    def avg_price(self) -> float:
        return self.weighted_price / self.total_quantity

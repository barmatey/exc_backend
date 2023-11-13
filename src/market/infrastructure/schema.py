from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core import Ticker
from .. import domain


class OrderSchema(BaseModel):
    uuid: UUID
    account: UUID
    ticker: Ticker
    dtype: domain.OrderType
    direction: domain.OrderDirection
    price: float
    quantity: int
    created: datetime

    def to_entity(self) -> domain.Order:
        return domain.Order(
            uuid=self.uuid,
            account=self.account,
            ticker=self.ticker,
            dtype=self.dtype,
            direction=self.direction,
            price=self.price,
            quantity=self.quantity,
            created=self.created,
        )


class MarketSchema(BaseModel):
    ticker: Ticker
    buy_level: list[tuple[float, int]]
    sell_level: list[tuple[float, int]]

    @classmethod
    def from_market(cls, market: domain.Market):
        buy_level = [(price, quantity) for price, quantity in market.buy_level.items()]
        sell_level = [(price, quantity) for price, quantity in market.sell_level.items()]
        return cls(
            ticker=market.ticker,
            buy_level=buy_level,
            sell_level=sell_level,
        )

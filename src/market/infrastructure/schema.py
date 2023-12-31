from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, field_serializer, Field

from src.core import Ticker
from .. import domain


class OrderSchema(BaseModel):
    account: UUID
    ticker: Ticker
    dtype: domain.OrderType
    direction: domain.OrderDirection
    price: float
    quantity: int
    status: domain.OrderStatus = 'PENDING'
    created: datetime = Field(default_factory=datetime.now)
    uuid: UUID = Field(default_factory=uuid4)

    @classmethod
    def from_entity(cls, entity: domain.Order) -> 'OrderSchema':
        return cls(
            account=entity.account,
            ticker=entity.ticker,
            dtype=entity.dtype,
            direction=entity.direction,
            price=entity.price,
            quantity=entity.quantity,
            uuid=entity.uuid,
            status=entity.status,
        )

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
            status=self.status,
        )

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID):
        return str(uuid)

    @field_serializer('account')
    def serialize_account(self, acc: UUID):
        return str(acc)

    @field_serializer('created')
    def serialize_dt(self, date: datetime) -> str:
        return str(date)


class TransactionSchema(BaseModel):
    uuid: UUID
    ticker: Ticker
    date: datetime
    price: float
    quantity: int
    buyer: UUID
    seller: UUID

    @classmethod
    def from_entity(cls, trs: domain.Transaction):
        return cls(
            uuid=trs.uuid,
            ticker=trs.ticker,
            date=trs.date,
            price=trs.price,
            quantity=trs.quantity,
            buyer=trs.buyer,
            seller=trs.seller,
        )

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID) -> str:
        return str(uuid)

    @field_serializer('buyer')
    def serialize_buyer(self, buyer: UUID) -> str:
        return str(buyer)

    @field_serializer('seller')
    def serialize_seller(self, seller: UUID) -> str:
        return str(seller)

    @field_serializer('date')
    def serialize_dt(self, date: datetime) -> str:
        return str(date)


class PositionSchema(BaseModel):
    account_uuid: UUID
    ticker: Ticker
    avg_price: float
    total_quantity: int

    @classmethod
    def from_entity(cls, entity: domain.Position):
        return cls(
            account_uuid=entity.account_uuid,
            ticker=entity.ticker,
            avg_price=entity.avg_price,
            total_quantity=entity.total_quantity,
        )


class MarketSchema(BaseModel):
    ticker: Ticker
    buy_level: list[tuple[float, int]]
    sell_level: list[tuple[float, int]]

    @classmethod
    def from_entity(cls, market: domain.Market):
        buy_level = [(price, quantity) for price, quantity in market.buy_level.items()]
        sell_level = [(price, quantity) for price, quantity in market.sell_level.items()]
        return cls(
            ticker=market.ticker,
            buy_level=buy_level,
            sell_level=sell_level,
        )

from uuid import UUID

from sqlalchemy import String, TIMESTAMP, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.base.repo.postgres import Base
from src.market import domain


class OrderModel(Base):
    __tablename__ = 'order'
    account: Mapped[UUID] = mapped_column(String(64), nullable=False)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    dtype: Mapped[str] = mapped_column(String(16), nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    @staticmethod
    def key_converter(key: str):
        key = 'id' if key == 'uuid' else key
        return key

    def to_entity(self) -> domain.Order:
        return domain.Order(
            uuid=self.id,
            account=self.account,
            ticker=self.ticker,
            dtype=self.dtype,
            direction=self.direction,
            price=self.price,
            quantity=self.quantity,
            created=self.created,
            status=self.status,
        )

    @classmethod
    def from_entity(cls, entity: domain.Order):
        return cls(
            id=str(entity.uuid),
            account=str(entity.account),
            ticker=entity.ticker,
            dtype=entity.dtype,
            direction=entity.direction,
            price=entity.price,
            quantity=entity.quantity,
            created=entity.created,
            status=entity.status,
        )


class TransactionModel(Base):
    __tablename__ = 'transaction'
    ticker: Mapped[str] = mapped_column(String(16), nullable=False)
    date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True))
    price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer)
    buyer: Mapped[str] = mapped_column(String(64))
    seller: Mapped[str] = mapped_column(String(64))

    @staticmethod
    def key_converter(key: str):
        key = 'id' if key == 'uuid' else key
        return key

    def to_entity(self) -> domain.Transaction:
        return domain.Transaction(
            uuid=self.id,
            ticker=self.ticker,
            date=self.date,
            price=self.price,
            quantity=self.quantity,
            buyer=self.buyer,
            seller=self.seller,
        )

    @classmethod
    def from_entity(cls, entity: domain.Transaction):
        return cls(
            id=entity.uuid,
            ticker=entity.ticker,
            date=entity.date,
            price=entity.price,
            quantity=entity.quantity,
            buyer=str(entity.buyer),
            seller=str(entity.seller),
        )

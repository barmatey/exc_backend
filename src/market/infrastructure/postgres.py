from uuid import UUID

from sqlalchemy import String, TIMESTAMP, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.base.repo.postgres import Base
from src.market import domain


class OrderModel(Base):
    __tablename__ = "order"
    account: Mapped[UUID] = mapped_column(String(64), nullable=False)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    dtype: Mapped[str] = mapped_column(String(16), nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    price: Mapped[float] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    @staticmethod
    def key_converter(key: str):
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

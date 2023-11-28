from uuid import UUID, uuid4

from sqlalchemy import String, TIMESTAMP, Integer, Float, JSON, ForeignKey, select, Table, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.base.repo.postgres import Base, PostgresRepo, association_table
from src.base.repo.repository import OrderBy
from src.deal import domain


class DealModel(Base):
    __tablename__ = 'deal_table'
    account: Mapped[UUID] = mapped_column(UUID, nullable=False)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    weighted_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    transactions = relationship('TransactionModel', secondary=association_table, back_populates="deals")

    @staticmethod
    def key_converter(key: str):
        key = key.replace('.', '_')
        key = 'id' if key == 'uuid' else key
        return key

    def to_entity(self) -> domain.Deal:
        return domain.Deal(
            uuid=self.id,
            account=self.account,
            ticker=self.ticker,
            status=self.status,
            weighted_price=self.weighted_price,
            total_quantity=self.total_quantity,
            transactions=self.transactions,
        )

    @classmethod
    def from_entity(cls, entity: domain.Deal):
        return cls(
            id=entity.uuid,
            account=entity.account,
            ticker=entity.ticker,
            status=entity.status,
            weighted_price=entity.weighted_price,
            total_quantity=entity.total_quantity,
            transactions=entity.transactions,
        )

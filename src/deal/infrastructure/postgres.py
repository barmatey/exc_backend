from uuid import UUID

from sqlalchemy import String, TIMESTAMP, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


from src.base.repo.postgres import Base
from src.deal import domain


class InnerTransactionModel(Base):
    __tablename__ = 'deal_transaction'
    price: Mapped[Float] = mapped_column(Float, nullable=False)
    quantity: Mapped[Integer] = mapped_column(Integer, nullable=False)
    direction: Mapped[String] = mapped_column(String(8), nullable=False)


class DealModel(Base):
    __tablename__ = 'deal'
    account: Mapped[UUID] = mapped_column(UUID, nullable=False)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    transaction: Mapped[UUID] = ForeignKey('InnerTransactionModel')

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
            transaction=self.transaction,
            documents=self.documents,
        )

    @classmethod
    def from_entity(cls, entity: domain.Deal):
        return cls(
            id=entity.uuid,
            account=str(entity.account),
            ticker=entity.ticker,
            status=entity.status,
            transaction=str(entity.transaction),
            documents=entity.documents,
        )

from uuid import UUID, uuid4

from sqlalchemy import String, TIMESTAMP, Integer, Float, JSON, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


from src.base.repo.postgres import Base, PostgresRepo
from src.base.repo.repository import OrderBy
from src.deal import domain


class DealModel(Base):
    __tablename__ = 'deal_table'
    account: Mapped[UUID] = mapped_column(UUID, nullable=False)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    transactions = relationship('InnerTransactionModel', back_populates='deal', lazy='joined')

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
            account=entity.account,
            ticker=entity.ticker,
            status=entity.status,
            transactions=[InnerTransactionModel.from_entity(x) for x in entity.transactions]
        )


class InnerTransactionModel(Base):
    __tablename__ = 'deal_transaction_table'
    price: Mapped[Float] = mapped_column(Float, nullable=False)
    quantity: Mapped[Integer] = mapped_column(Integer, nullable=False)
    direction: Mapped[String] = mapped_column(String(8), nullable=False)
    deal_id: Mapped[UUID] = mapped_column(ForeignKey(DealModel.id))
    deal = relationship('DealModel', back_populates='transactions')

    @classmethod
    def from_entity(cls, entity: domain.InnerTransaction):
        return cls(
            id=uuid4(),
            price=entity.price,
            quantity=entity.quantity,
            direction=entity.direction,
        )


class DealRepo(PostgresRepo):
    def __init__(self, session: AsyncSession, model=DealModel):
        super().__init__(session, model)

    async def get_one_by_id(self, uuid: UUID) -> domain.Deal:
        raise NotImplemented

    async def get_many_by_id(self, ids: list[UUID], order_by: OrderBy = None) -> list[domain.Deal]:
        raise NotImplemented

    async def get_many(self, filter_by: dict = None, order_by: OrderBy = None,
                       slice_from=None, slice_to=None) -> list[domain.Deal]:
        stmt = select(DealModel)
        stmt = self._expand_statement(stmt, filter_by, order_by, slice_from, slice_to)
        result = list(await self._session.execute(stmt))
        print(result)
        return result

from uuid import UUID

from sqlalchemy import String, TIMESTAMP, Integer, Float, JSON, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


from src.base.repo.postgres import Base, PostgresRepo
from src.base.repo.repository import OrderBy
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
        print()
        print(result)
        raise Exception

from uuid import UUID

from sqlalchemy import String, TIMESTAMP, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.base.repo.postgres import Base
from src.account import domain


class AccountModel(Base):
    __tablename__ = 'account'
    buy_deals_amount: Mapped[Float] = mapped_column(Float, nullable=False)
    sell_deals_amount: Mapped[Float] = mapped_column(Float, nullable=False)
    cash: Mapped[Float] = mapped_column(Float, nullable=False)

    @staticmethod
    def key_converter(key: str):
        key = 'id' if key == 'uuid' else key
        return key

    def to_entity(self) -> domain.Account:
        return domain.Account(
            uuid=self.id,
            bda=self.buy_deals_amount,
            sda=self.sell_deals_amount,
            cash=self.cash
        )

    @classmethod
    def from_entity(cls, entity: domain.Account):
        return cls(
            id=entity.uuid,
            buy_deals_amount=entity.buy_deals_amount,
            sell_deals_amount=entity.sell_deals_amount,
            cash=entity.cash,
        )

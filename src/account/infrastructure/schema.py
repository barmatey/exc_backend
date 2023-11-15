from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .. import domain


class AccountSchema(BaseModel):
    cash: float
    buy_deals_amount: float
    sell_deals_amount: float
    uuid: UUID = Field(default_factory=uuid4)

    @classmethod
    def from_entity(cls, entity: domain.Account):
        return cls(
            uuid=entity.uuid,
            cash=entity.cash,
            buy_deals_amount=entity.buy_deals_amount,
            sell_deals_amount=entity.sell_deals_amount,
        )

    def to_entity(self) -> domain.Account:
        return domain.Account(
            uuid=self.uuid,
            bda=self.buy_deals_amount,
            sda=self.sell_deals_amount,
            cash=self.cash,
        )

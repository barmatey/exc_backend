from uuid import UUID

from pydantic import BaseModel

from src.core import Ticker
from src.deal import domain
from src.deal.domain import DealStatus


class DealSchema(BaseModel):
    account: UUID
    ticker: Ticker
    status: DealStatus
    avg_price: float
    total_quantity: int

    @classmethod
    def from_entity(cls, entity: domain.Deal):
        return cls(
            account=entity.account,
            ticker=entity.ticker,
            status=entity.status,
            avg_price=entity.avg_price,
            total_quantity=entity.total_quantity,
        )

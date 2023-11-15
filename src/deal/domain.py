from typing import Literal
from uuid import UUID

from pydantic import Field

from src.base.model import Entity
from src.core import Ticker

DealStatus = Literal['PROCESSING', 'CLOSED']


class Deal(Entity):
    account: UUID
    transaction: UUID
    ticker: Ticker
    status: DealStatus
    documents: list[str] = Field(default_factory=list)

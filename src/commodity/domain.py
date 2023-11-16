from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.core import Ticker


Specification = str


class Commodity(BaseModel):
    ticker: Ticker
    description: str
    specification: Specification
    uuid: UUID = Field(default_factory=uuid4)

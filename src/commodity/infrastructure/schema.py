from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.core import Ticker
from src.commodity  import domain


class CommoditySchema(BaseModel):
    ticker: Ticker
    description: str
    specification: domain.Specification
    uuid: UUID = Field(default_factory=uuid4)

    @classmethod
    def from_entity(cls, entity: domain.Commodity):
        return cls(
            ticker=entity.ticker,
            description=entity.description,
            specification=entity.specification,
            uuid=entity.uuid,
        )

    def to_entity(self) -> domain.Commodity:
        return domain.Commodity(
            ticker=self.ticker,
            description=self.description,
            specification=self.specification,
            uuid=self.uuid,
        )

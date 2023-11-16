from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.base.repo.postgres import Base
from src.commodity import domain


class CommodityModel(Base):
    __tablename__ = 'commodity'
    ticker: Mapped[str] = mapped_column(String(16), unique=True)
    description: Mapped[str] = mapped_column(String(2048), default="")
    specification: Mapped[str] = mapped_column(String(2048), default="")

    def to_entity(self) -> domain.Commodity:
        return domain.Commodity(
            uuid=self.id,
            ticker=self.ticker,
            description=self.description,
            specification=self.specification,
        )

    @classmethod
    def from_entity(cls, entity: domain.Commodity):
        return cls(
            id=entity.uuid,
            ticker=entity.ticker,
            description=entity.description,
            specification=entity.specification,
        )

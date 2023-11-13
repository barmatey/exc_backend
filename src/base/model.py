from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Entity(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)

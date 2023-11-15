from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Iterable, Sequence, NamedTuple, Union
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T")


class OrderBy(NamedTuple):
    fields: Union[str, list[str]]
    asc: bool


class Repository(ABC, Generic[T]):
    @abstractmethod
    async def add_many(self, data: Iterable[T]):
        raise NotImplemented

    @abstractmethod
    async def get_one_by_id(self, uuid: UUID) -> T:
        raise NotImplemented

    @abstractmethod
    async def get_many(self, filter_by: dict = None, order_by: OrderBy = None, slice_from=None,
                       slice_to=None) -> list[T]:
        raise NotImplemented

    @abstractmethod
    async def get_uniques(self, columns_by: list[str], filter_by: dict = None, order_by: OrderBy = None) -> list[T]:
        raise NotImplemented

    @abstractmethod
    async def get_many_by_id(self, ids: Iterable[UUID], order_by: OrderBy = None) -> list[T]:
        raise NotImplemented

    @abstractmethod
    async def update_many(self, data: list[T]):
        raise NotImplemented

    @abstractmethod
    async def update_one(self, data: T):
        raise NotImplemented

    @abstractmethod
    async def remove_many(self, filter_by: dict):
        raise NotImplemented

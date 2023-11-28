from src.base.repo import Repository
from . import domain
from ..base.repo.repository import OrderBy


class CreateDeal:
    def __init__(self, deal: domain.Deal, repo: Repository[domain.Deal]):
        self._deal = deal
        self._repo = repo

    async def execute(self):
        await self._repo.add_many([self._deal])

    async def rollback(self):
        raise NotImplemented


class GetManyDeals:
    def __init__(self, repo: Repository[domain.Deal], filter_by: dict = None, order_by: OrderBy = None):
        self._repo = repo
        self._filter_by = filter_by
        self._order_by = order_by

    async def execute(self) -> list[domain.Deal]:
        return await self._repo.get_many(self._filter_by, self._order_by)


class UpdateDeal:
    def __init__(self, deal: domain.Deal, repo: Repository[domain.Deal]):
        self._deal = deal
        self._repo = repo

    async def execute(self):
        await self._repo.update_one(self._deal)

    async def rollback(self):
        raise NotImplemented


class DealCommandFactory:
    def __init__(self, repo: Repository[domain.Deal]):
        self._repo = repo

    def create_deal(self, deal: domain.Deal) -> CreateDeal:
        return CreateDeal(deal, self._repo)

    def get_many_deals(self, filter_by: dict = None, order_by: OrderBy = None) -> GetManyDeals:
        return GetManyDeals(self._repo, filter_by, order_by)

    def update_deal(self, deal: domain.Deal) -> UpdateDeal:
        return UpdateDeal(deal, self._repo)

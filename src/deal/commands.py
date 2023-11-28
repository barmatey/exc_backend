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


class CreateInnerTransaction:
    def __init__(self, repo: Repository[domain.InnerTransaction], trs: domain.InnerTransaction):
        self._repo = repo
        self._trs = trs

    async def execute(self):
        await self._repo.add_many([self._trs])


class DealCommandFactory:
    def __init__(self, deal_repo: Repository[domain.Deal], trs_repo: Repository[domain.InnerTransaction]):
        self._deal_repo = deal_repo
        self._trs_repo = trs_repo

    def create_deal(self, deal: domain.Deal) -> CreateDeal:
        return CreateDeal(deal, self._deal_repo)

    def get_many_deals(self, filter_by: dict = None, order_by: OrderBy = None) -> GetManyDeals:
        return GetManyDeals(self._deal_repo, filter_by, order_by)

    def update_deal(self, deal: domain.Deal) -> UpdateDeal:
        return UpdateDeal(deal, self._deal_repo)

    def create_inner_transaction(self, trs: domain.InnerTransaction) -> CreateInnerTransaction:
        return CreateInnerTransaction(self._trs_repo, trs)

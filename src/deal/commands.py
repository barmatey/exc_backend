from src.base.repo import Repository
from . import domain


class CreateDeal:
    def __init__(self, deal: domain.Deal, repo: Repository[domain.Deal]):
        self._deal = deal
        self._repo = repo

    async def execute(self):
        await self._repo.add_many([self._deal])

    async def rollback(self):
        raise NotImplemented

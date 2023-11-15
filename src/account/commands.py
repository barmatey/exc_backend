from uuid import UUID

from src.account import domain
from src.base.repo import Repository


class CreateAccount:
    def __init__(self, account: domain.Account, repo: Repository[domain.Account]):
        self._repo = repo
        self._account = account

    async def execute(self):
        await self._repo.add_many([self._account])


class GetAccountByUuid:
    def __init__(self, uuid: UUID, repo: Repository[domain.Account]):
        self._repo = repo
        self._uuid = uuid

    async def execute(self) -> domain.Account:
        return await self._repo.get_one_by_id(self._uuid)


class UpdateAccount:
    def __init__(self, account: domain.Account, repo: Repository[domain.Account]):
        self._repo = repo
        self._account = account

    async def execute(self):
        await self._repo.update_one(self._account)

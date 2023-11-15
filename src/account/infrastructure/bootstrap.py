from src.base.repo import Repository, PostgresRepo
from .. import domain, handlers
from . import postgres


class Bootstrap:
    def __init__(self, session):
        self._session = session

    def get_account_repo(self) -> Repository[domain.Account]:
        repo = PostgresRepo(self._session, postgres.AccountModel)
        return repo

    def get_command_factory(self) -> handlers.CommandFactory:
        factory = handlers.CommandFactory(self.get_account_repo())
        return factory

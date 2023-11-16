from src.base.repo import Repository, PostgresRepo
from src.commodity import domain, handlers
from . import postgres


class Bootstrap:
    def __init__(self, session):
        self._session = session

    def get_repo(self) -> Repository[domain.Commodity]:
        return PostgresRepo(self._session, postgres.CommodityModel)

    def get_command_factory(self):
        return handlers.CommandFactory(self.get_repo())

from src.base import eventbus
from src.base.repo import Repository, PostgresRepo
from src.deal import domain, handlers
from src.deal.infrastructure import postgres


class Bootstrap:
    def __init__(self, session):
        self._session = session
        self._queue = eventbus.Queue()

    def get_queue(self):
        return self._queue

    def get_deal_repo(self) -> Repository[domain.Deal]:
        repo = PostgresRepo(self._session, postgres.DealModel)
        return repo

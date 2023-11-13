from src.base.repo import Repository, PostgresRepo
from src.market import domain, service
from src.market.infrastructure import postgres


class Bootstrap:
    def __init__(self, session):
        self._session = session

    def get_order_repo(self) -> Repository[domain.Order]:
        return PostgresRepo(session=self._session, model=postgres.OrderModel)

    def get_order_service(self):
        repo = self.get_order_repo()
        return service.OrderService(repo)

    def get_market_service(self):
        repo = self.get_order_repo()
        return service.MarketService(repo)

from base import eventbus
from src.base.repo import Repository, PostgresRepo
from src.market import domain, service, handlers
from src.market.infrastructure import postgres


class Bootstrap:
    def __init__(self, session):
        self._session = session
        self._queue = eventbus.Queue()

    def get_queue(self):
        return self._queue

    def get_order_repo(self) -> Repository[domain.Order]:
        return PostgresRepo(session=self._session, model=postgres.OrderModel)

    def get_order_service(self):
        repo = self.get_order_repo()
        return service.OrderService(repo)

    def get_market_service(self):
        repo = self.get_order_repo()
        return service.MarketService(repo)

    def get_eventbus(self) -> eventbus.EventBus:
        handler = handlers.OrderHandler(self.get_order_repo())
        bus = eventbus.EventBus(self._queue)
        bus.register('OrderCreated', handler.handle_order_created)
        return bus

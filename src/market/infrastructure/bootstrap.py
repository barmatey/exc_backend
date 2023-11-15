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

    def get_transaction_repo(self) -> Repository[domain.Transaction]:
        return PostgresRepo(session=self._session, model=postgres.TransactionModel)

    def get_order_service(self):
        repo = self.get_order_repo()
        return service.OrderService(repo)

    def get_market_service(self):
        repo = self.get_order_repo()
        trs_repo = self.get_transaction_repo()
        return service.MarketService(repo, trs_repo)

    def get_eventbus(self) -> eventbus.EventBus:
        bus = eventbus.EventBus(self._queue)

        handler = handlers.OrderHandler(self.get_order_repo())
        bus.register('OrderCreated', handler.handle_order_created)
        bus.register('OrderUpdated', handler.handle_order_updated)
        bus.register('OrderCompleted', handler.handle_order_completed)

        handler = handlers.TransactionHandler(self.get_transaction_repo())
        bus.register('TransactionCreated', handler.handle_transaction_created)
        return bus

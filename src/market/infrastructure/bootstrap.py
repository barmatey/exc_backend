from src.base import eventbus
from src.base.repo import Repository, PostgresRepo
from src.market import domain, handlers
from src.market.infrastructure import postgres, gateway


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

    def get_deal_gateway(self) -> handlers.DealGateway:
        return gateway.DealGatewayM(self._session)

    def get_acc_gateway(self) -> handlers.AccountGateway:
        return gateway.AccountGatewayM(self._session)

    def get_command_factory(self) -> handlers.CommandFactory:
        factory = handlers.CommandFactory(self.get_order_repo(), self.get_transaction_repo(), self.get_deal_gateway(),
                                          self.get_acc_gateway(), self._queue)
        return factory

    def get_eventbus(self) -> eventbus.EventBus:
        bus = eventbus.EventBus(self._queue)

        handler = handlers.OrderHandler(self.get_order_repo())
        bus.register('OrderCreated', handler.handle_order_created)
        bus.register('OrderUpdated', handler.handle_order_updated)
        bus.register('OrderCompleted', handler.handle_order_completed)

        handler = handlers.TransactionHandler(
            self.get_transaction_repo(),
            self.get_deal_gateway(),
            self.get_acc_gateway(),
        )
        bus.register('TransactionCreated', handler.handle_transaction_created)
        return bus

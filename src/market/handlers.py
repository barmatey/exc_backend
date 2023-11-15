from abc import ABC, abstractmethod

from src.base.repo import Repository
from src.base import eventbus
from . import domain, service
from ..base.repo.repository import OrderBy
from ..core import Ticker


class DealGateway(ABC):
    @abstractmethod
    async def create_deals_from_transaction(self, trs: domain.Transaction):
        raise NotImplemented


class AccountGateway(ABC):
    @abstractmethod
    async def change_accounts_data(self, trs: domain.Transaction):
        raise NotImplemented

    @abstractmethod
    async def check_account_has_permission_to_send_order(self, order: domain.Order) -> bool:
        raise NotImplemented


class CommandHandler:
    def __init__(
            self,
            order_repo: Repository[domain.Order],
            trs_repo: Repository[domain.Transaction],
            deal_gw: DealGateway,
            acc_gw: AccountGateway,
            queue: eventbus.Queue,
    ):
        self._queue = queue
        self._order_repo = order_repo
        self._trs_repo = trs_repo
        self._deal_gw = deal_gw
        self._acc_gw = acc_gw

    async def get_market(self, ticker: Ticker) -> domain.Market:
        orders = await self._order_repo.get_many(filter_by={'ticker': ticker, 'status': 'PENDING'})
        transactions = await self._trs_repo.get_many({'ticker': ticker}, OrderBy('date', asc=True), 0, 100)
        market = domain.Market(ticker=ticker, orders=orders, transactions=transactions)
        return market

    async def send_order(self, order: domain.Order):
        orders = await self._order_repo.get_many(filter_by={'ticker': order.ticker, 'status': 'PENDING'})
        market = domain.Market(ticker=order.ticker, orders=orders)
        if not await self._acc_gw.check_account_has_permission_to_send_order(order):
            raise PermissionError
        market.send_order(order)
        self._queue.extend(market.events.parse_events())


class OrderHandler:
    def __init__(self, repo: Repository[domain.Order]):
        self._repo = repo

    async def handle_order_created(self, event: eventbus.Created[domain.Order]):
        await self._repo.add_many([event.entity])

    async def handle_order_updated(self, event: eventbus.Updated[domain.Order]):
        await self._repo.update_one(event.entity)

    async def handle_order_completed(self, event: eventbus.Deleted[domain.Order]):
        await self._repo.remove_many(filter_by={'uuid': event.entity.uuid})


class TransactionHandler:
    def __init__(self, trs_repo: service.Repository[domain.Transaction], deal_gw: DealGateway, acc_gw: AccountGateway):
        self._repo = trs_repo
        self._deal_gw = deal_gw
        self._acc_gw = acc_gw

    async def handle_transaction_created(self, event: eventbus.Created[domain.Transaction]):
        await self._repo.add_many([event.entity])
        await self._acc_gw.change_accounts_data(event.entity)
        await self._deal_gw.create_deals_from_transaction(event.entity)

from abc import ABC, abstractmethod
from uuid import UUID

from loguru import logger

from src.base.repo import Repository
from src.base import eventbus
from . import domain
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
    async def check_account_has_permission_to_send_order(self, order: domain.Order):
        raise NotImplemented


class GetMarketByTickerCommand:
    def __init__(
            self,
            ticker: Ticker,
            order_repo: Repository[domain.Order],
            trs_repo: Repository[domain.Transaction],
    ):
        self._ticker = ticker
        self._order_repo = order_repo
        self._trs_repo = trs_repo

    async def execute(self) -> domain.Market:
        ticker = self._ticker
        orders = await self._order_repo.get_many(filter_by={'ticker': ticker})
        transactions = await self._trs_repo.get_many({'ticker': ticker}, OrderBy('date', asc=True), 0, 100)
        market = domain.Market(ticker=ticker, orders=orders, transactions=transactions)
        return market


class GetManyOrdersCommand:
    def __init__(self, order_repo: Repository[domain.Order], filter_by=None, order_by=None):
        self._order_repo = order_repo
        self._filter_by = filter_by
        self._order_by = order_by

    async def execute(self) -> list[domain.Order]:
        return await self._order_repo.get_many(filter_by=self._filter_by, order_by=self._order_by)


class SendOrderCommand:
    def __init__(
            self,
            order: domain.Order,
            order_repo: Repository[domain.Order],
            trs_repo: Repository[domain.Transaction],
            deal_gw: DealGateway,
            acc_gw: AccountGateway,
            queue: eventbus.Queue,
    ):
        self._order = order
        self._order_repo = order_repo
        self._trs_repo = trs_repo
        self._deal_gw = deal_gw
        self._acc_gw = acc_gw
        self._queue = queue

    async def execute(self) -> domain.Market:
        order = self._order
        orders = await self._order_repo.get_many(filter_by={'ticker': order.ticker})
        market = domain.Market(ticker=order.ticker, orders=orders)
        await self._acc_gw.check_account_has_permission_to_send_order(order)
        market.send_order(order)
        self._queue.extend(market.events.parse_events())
        return market


class CancelOrderCommand:
    def __init__(
            self,
            order: domain.Order,
            order_repo: Repository[domain.Order],
            queue: eventbus.Queue,
    ):
        self._order = order
        self._order_repo = order_repo
        self._queue = queue

    async def execute(self) -> domain.Market:
        order = self._order
        await self._order_repo.remove_many({'uuid': order.uuid})
        orders = await self._order_repo.get_many(filter_by={'ticker': order.ticker})
        market = domain.Market(ticker=order.ticker, orders=orders)
        return market


class GetManyTransactionsCommand:
    def __init__(self, trs_repo: Repository[domain.Transaction], filter_by=None, order_by=None,
                 slice_from=None, slice_to=None):
        self._filter_by = filter_by
        self._order_by = order_by
        self._trs_repo = trs_repo
        self._slice_from = slice_from
        self._slice_to = slice_to

    async def execute(self):
        return await self._trs_repo.get_many(self._filter_by, self._order_by, self._slice_from, self._slice_to)


class GetAccountPositionsCommand:
    def __init__(self, trs_repo: Repository[domain.Transaction], account_uuid: UUID):
        self._trs_repo = trs_repo
        self._acc_uuid = account_uuid
        self._positions: dict[Ticker, domain.Position] = {}

    def __get_or_create_pos(self, ticker: Ticker):
        if self._positions.get(ticker) is None:
            self._positions[ticker] = domain.Position(self._acc_uuid, ticker)
        return self._positions[ticker]

    async def execute(self) -> list[domain.Position]:
        one = await self._trs_repo.get_many({"buyer": self._acc_uuid})
        two = await self._trs_repo.get_many({"seller": self._acc_uuid})

        for trs in one:
            position = self.__get_or_create_pos(trs.ticker)
            position.append_transaction(trs)

        for trs in two:
            position = self.__get_or_create_pos(trs.ticker)
            position.append_transaction(trs)

        return list(filter(lambda x: x.total_quantity != 0, self._positions.values()))


class CommandFactory:
    def __init__(
            self,
            order_repo: Repository[domain.Order],
            trs_repo: Repository[domain.Transaction],
            deal_gw: DealGateway,
            acc_gw: AccountGateway,
            queue: eventbus.Queue,
    ):
        self._order_repo = order_repo
        self._trs_repo = trs_repo
        self._deal_gw = deal_gw
        self._acc_gw = acc_gw
        self._queue = queue

    def get_many_orders(self, filter_by: dict = None, order_by: OrderBy = None) -> GetManyOrdersCommand:
        return GetManyOrdersCommand(self._order_repo, filter_by, order_by)

    def get_many_transactions(self, filter_by: dict = None, order_by: OrderBy = None,
                              slice_from: int = None, slice_to: int = None) -> GetManyTransactionsCommand:
        return GetManyTransactionsCommand(self._trs_repo, filter_by, order_by, slice_from, slice_to)

    def get_market_by_ticker(self, ticker: Ticker) -> GetMarketByTickerCommand:
        return GetMarketByTickerCommand(ticker, self._order_repo, self._trs_repo)

    def get_account_positions(self, acc_uuid: UUID) -> GetAccountPositionsCommand:
        return GetAccountPositionsCommand(self._trs_repo, acc_uuid)

    def send_order(self, order: domain.Order) -> SendOrderCommand:
        return SendOrderCommand(order, self._order_repo, self._trs_repo, self._deal_gw, self._acc_gw, self._queue)

    def cancel_order(self, order: domain.Order) -> CancelOrderCommand:
        return CancelOrderCommand(order, self._order_repo, self._queue)


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
    def __init__(self, trs_repo: Repository[domain.Transaction], deal_gw: DealGateway, acc_gw: AccountGateway):
        self._repo = trs_repo
        self._deal_gw = deal_gw
        self._acc_gw = acc_gw

    async def handle_transaction_created(self, event: eventbus.Created[domain.Transaction]):
        await self._repo.add_many([event.entity])
        await self._acc_gw.change_accounts_data(event.entity)
        await self._deal_gw.create_deals_from_transaction(event.entity)

from collections import deque
from datetime import datetime
from typing import Literal
from uuid import UUID
from sortedcontainers import SortedDict
from pydantic import ConfigDict, PrivateAttr, BaseModel, Field

from src.base import eventbus
from src.base.model import Entity
from src.core import Ticker

OrderType = Literal['MARKET', 'LIMIT']
OrderDirection = Literal['BUY', 'SELL']
OrderStatus = Literal['PENDING', 'PARTIAL', 'COMPLETED', 'CANCELED']


class Order(Entity):
    account: UUID
    ticker: Ticker
    dtype: OrderType
    direction: OrderDirection
    price: float
    quantity: int
    created: datetime = Field(default_factory=datetime.now)
    status: OrderStatus = 'PENDING'

    @property
    def amount(self) -> float:
        return self.price * self.quantity


class Transaction(Entity):
    ticker: Ticker
    date: datetime
    price: float
    quantity: int
    buyer: UUID
    seller: UUID
    model_config = ConfigDict(frozen=True)

    @property
    def amount(self) -> float:
        return self.price * self.quantity


class Position:
    def __init__(
            self,
            account_id: UUID,
            ticker: Ticker,
            weighted_price: float = 0,
            total_quantity: int = 0,
    ):
        self.account_uuid = account_id
        self.ticker = ticker
        self._weighted_price = weighted_price
        self._total_quantity = total_quantity

    def append_transaction(self, trs: Transaction):
        if trs.buyer != self.account_uuid or trs.seller != self.account_uuid:
            raise ValueError
        if trs.ticker != self.ticker:
            raise ValueError
        if trs.buyer == trs.seller:
            return

        quantity = trs.quantity if trs.buyer == self.account_uuid else -trs.quantity
        self._weighted_price = self._weighted_price + quantity * trs.price
        self._total_quantity += quantity

    @property
    def total_quantity(self) -> int:
        return self._total_quantity

    @property
    def avg_price(self) -> float:
        if self._total_quantity == 0:
            return 0
        return self._weighted_price / self._total_quantity


class Market(BaseModel):
    ticker: Ticker
    _buyers: SortedDict[float, deque[Order]] = PrivateAttr(default_factory=SortedDict)
    _sellers: SortedDict[float, deque[Order]] = PrivateAttr(default_factory=SortedDict)
    _transactions: list[Transaction] = PrivateAttr(default_factory=list)
    _orders: list[Order] = PrivateAttr(default_factory=list)
    _events: eventbus.EventStore = PrivateAttr(default_factory=eventbus.EventStore)

    def __init__(self, orders: list[Order], transactions: list[Transaction] = None, **data):
        super().__init__(**data)
        for order in orders:
            self.__push_order_in_deque(order, constructor=True)
        if len(self._buyers) and len(self._sellers):
            if self._buyers.peekitem(-1)[0] >= self._sellers.peekitem(0)[0]:
                raise Exception(f'buyers max price({self._buyers.peekitem(-1)[0]}) '
                                f'>= sellers min  price ({self._sellers.peekitem(0)[0]})')
        if transactions is not None:
            self._transactions = transactions

    @property
    def events(self):
        return self._events

    @property
    def orders(self) -> list[Order]:
        return self._orders

    @property
    def transactions(self):
        return self._transactions

    @property
    def buy_level(self) -> SortedDict[float, int]:
        result = SortedDict()
        for key, value in self._buyers.items():
            result[key] = 0
            for order in value:
                result[key] += order.quantity
        return result

    @property
    def sell_level(self) -> SortedDict[float, int]:
        result = SortedDict()
        for key, value in self._sellers.items():
            result[key] = 0
            for order in value:
                result[key] += order.quantity
        return result

    def send_order(self, order: Order):
        if order.direction == 'BUY':
            if order.dtype == 'LIMIT':
                self.send_buy_limit_order(order)
                return
        elif order.direction == 'SELL':
            if order.dtype == 'LIMIT':
                self.send_sell_limit_order(order)
                return
        raise ValueError(f'{order}')

    def send_buy_limit_order(self, order: Order):
        order = order.model_copy()
        if order.dtype != 'LIMIT':
            raise ValueError
        if order.direction != 'BUY':
            raise ValueError
        if order.ticker != self.ticker:
            raise ValueError
        if order.quantity <= 0:
            raise ValueError

        while order.quantity:
            # If the lower seller price is higher than buyer limit then push order in deque
            if len(self._sellers) == 0 or self._sellers.peekitem(0)[0] > order.price:
                self.__push_order_in_deque(order)
                break
            else:
                best_sellers: deque[Order] = self._sellers.peekitem(0)[1]
                for seller in best_sellers:
                    self.__match_orders_and_create_transaction(order, seller)
                    if not order.quantity:
                        break
                self.__update_best_sellers()

    def send_sell_limit_order(self, order: Order):
        order = order.model_copy()
        if order.dtype != 'LIMIT':
            raise ValueError
        if order.direction != 'SELL':
            raise ValueError
        if order.ticker != self.ticker:
            raise ValueError
        if order.quantity <= 0:
            raise ValueError

        while order.quantity:
            # If the better buyer price is lower than seller limit then push order in deque
            if len(self._buyers) == 0 or self._buyers.peekitem(-1)[0] < order.price:
                self.__push_order_in_deque(order)
                break
            else:
                best_buyers: deque[Order] = self._buyers.peekitem(-1)[1]
                for buyer in best_buyers:
                    self.__match_orders_and_create_transaction(order, buyer)
                    if not order.quantity:
                        break
                self.__update_best_buyers()

    def __push_order_in_deque(self, order: Order, constructor=False):
        queue = self._buyers if order.direction == 'BUY' else self._sellers
        if queue.get(order.price) is None:
            queue[order.price] = deque()
        queue[order.price].append(order)
        if not constructor:
            self._orders.append(order)
            self.events.push_event(event=eventbus.Created(key='OrderCreated', entity=order))

    def __update_best_sellers(self):
        best_sellers = deque(x for x in self._sellers.peekitem(0)[1] if x.quantity > 0)
        if len(best_sellers) > 0:
            self._sellers[self._sellers.keys()[0]] = best_sellers
        else:
            self._sellers.popitem(0)

    def __update_best_buyers(self):
        best_buyers = deque(x for x in self._buyers.peekitem(-1)[1] if x.quantity > 0)
        if len(best_buyers) > 0:
            self._buyers[self._buyers.keys()[-1]] = best_buyers
        else:
            self._buyers.popitem()

    def __match_orders_and_create_transaction(self, order: Order, cparty: Order):
        if order.quantity < cparty.quantity:
            quantity = order.quantity
            order.quantity = 0
            cparty.quantity -= quantity
            cparty.status = 'PARTIAL'
            order.status = 'COMPLETED'
            self.events.push_event(eventbus.Updated(key='OrderUpdated', entity=cparty))
        else:
            quantity = cparty.quantity
            cparty.quantity = 0
            order.quantity -= quantity
            order.status = 'PARTIAL'
            cparty.status = 'COMPLETED'
            self.events.push_event(eventbus.Deleted(key='OrderCompleted', entity=cparty))

        self._orders.append(cparty)
        buy, sell = (order.account, cparty.account) if order.direction == 'BUY' else (cparty.account, order.account)

        transaction = Transaction(
            date=datetime.now(),
            buyer=buy,
            seller=sell,
            price=cparty.price,
            quantity=quantity,
            ticker=order.ticker,
        )
        self._transactions.append(transaction)
        self._events.push_event(eventbus.Created(key='TransactionCreated', entity=transaction))

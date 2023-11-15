from datetime import datetime
from uuid import uuid4

from src.market import domain


class TestMarket:
    market = domain.Market(ticker='ABC', orders=[])

    def test_send_buy_limit_order_without_seller_counterparty(self):
        market = self.market

        buy_orders = [
            domain.Order(
                uuid=uuid4(),
                account=uuid4(),
                ticker='ABC',
                dtype='LIMIT',
                direction='BUY',
                price=x,
                quantity=100,
                created=datetime.now(),
            )
            for x in range(10, 100, 10)
        ]
        for order in buy_orders:
            market.send_buy_limit_order(order)

        assert len(market.buy_level) == len(buy_orders)
        for actual, expected in zip(market.buy_level.keys(), buy_orders):
            assert actual == expected.price

    def test_send_sell_limit_order_with_counterparty_but_without_matching(self):
        market = self.market

        sell_orders = [
            domain.Order(
                uuid=uuid4(),
                account=uuid4(),
                ticker='ABC',
                dtype='LIMIT',
                direction='SELL',
                price=x,
                quantity=100,
                created=datetime.now(),
            )
            for x in range(110, 200, 20)
        ]

        for order in sell_orders:
            market.send_sell_limit_order(order)

        assert len(market.sell_level) == len(sell_orders) == 5
        for actual, expected in zip(market.sell_level.keys(), sell_orders):
            assert actual == expected.price

    def test_send_buy_limit_order_with_complex_matching(self):
        market = self.market
        market.send_buy_limit_order(
            domain.Order(
                uuid=uuid4(),
                account=uuid4(),
                ticker='ABC',
                dtype='LIMIT',
                direction='BUY',
                price=160,
                quantity=300,
                created=datetime.now(),
            )
        )
        assert len(market.transactions) == 3
        assert len(market.sell_level) == 2
        assert market.sell_level.peekitem(0)[0] == 170
        assert market.sell_level.peekitem(1)[0] == 190

    def test_send_limit_sell_order_with_complex_matching(self):
        market = self.market
        market.send_sell_limit_order(
            domain.Order(
                uuid=uuid4(),
                account=uuid4(),
                ticker='ABC',
                dtype='LIMIT',
                direction='SELL',
                price=90,
                quantity=200,
                created=datetime.now(),
            )
        )
        assert len(market.transactions) == 4
        assert market.sell_level.peekitem(0)[0] == 90

    def test_send_sell_order_append_to_existed_orders(self):
        market = self.market
        market.send_sell_limit_order(
            domain.Order(
                uuid=uuid4(),
                account=uuid4(),
                ticker='ABC',
                dtype='LIMIT',
                direction='SELL',
                price=90,
                quantity=200,
                created=datetime.now(),
            )
        )
        assert len(market.transactions) == 4
        assert market.sell_level[90] == 300

from uuid import UUID, uuid4

from pydantic import PrivateAttr

from src.base.model import Entity


class NotEnoughMoney(Exception):
    pass


class Account:
    def __init__(self, cash: float, bda: float, sda: float, uuid: UUID = lambda x: uuid4):
        self.validate(cash, bda, sda)
        self._cash = cash
        self._buy_deals_amount = bda
        self._sell_deals_amount = sda
        self.uuid = uuid

    @staticmethod
    def validate(cash, bda, sda):
        assert cash >= 0
        assert bda >= 0
        assert sda >= 0

    @property
    def cash(self) -> float:
        return self._cash

    @property
    def buy_deals_amount(self):
        return self._buy_deals_amount

    @property
    def sell_deals_amount(self):
        return self._sell_deals_amount

    @property
    def total_assets(self):
        return self._cash + self._buy_deals_amount + self._sell_deals_amount

    def reflect_purchase(self, value: float):
        self.change_cash(-value)
        self.change_buy_deals_amount(value)

    def reflect_sale(self, value: float):
        self.change_cash(-value)
        self.change_sell_deals_amount(value)

    def change_cash(self, value: float):
        self._cash += value
        if self._cash < 0:
            raise NotEnoughMoney

    def change_buy_deals_amount(self, value: float):
        self._buy_deals_amount += value
        assert self._buy_deals_amount >= 0

    def change_sell_deals_amount(self, value: float):
        self._sell_deals_amount += value
        assert self._sell_deals_amount >= 0

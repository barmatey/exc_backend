from abc import ABC, abstractmethod

from src.base import eventbus
from . import domain, service


class OrderHandler:
    def __init__(self, repo: service.Repository[domain.Order]):
        self._repo = repo

    async def handle_order_created(self, event: eventbus.Created[domain.Order]):
        await self._repo.add_many([event.entity])

    async def handle_order_updated(self, event: eventbus.Updated[domain.Order]):
        await self._repo.update_one(event.entity)

    async def handle_order_completed(self, event: eventbus.Deleted[domain.Order]):
        await self._repo.remove_many(filter_by={'uuid': event.entity.uuid})


class DealGateway(ABC):
    async def create_deals_from_transaction(self, trs: domain.Transaction):
        raise NotImplemented


class TransactionHandler:
    def __init__(self, trs_repo: service.Repository[domain.Transaction], deal_gw: DealGateway):
        self._repo = trs_repo
        self._deal_gw = deal_gw

    async def handle_transaction_created(self, event: eventbus.Created[domain.Transaction]):
        await self._repo.add_many([event.entity])
        await self._deal_gw.create_deals_from_transaction(event.entity)


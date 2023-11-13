from base import eventbus
from . import domain, service


class OrderHandler:
    def __init__(self, repo: service.Repository[domain.Order]):
        self._repo = repo

    async def handle_order_created(self, event: eventbus.Created[domain.Order]):
        await self._repo.add_many([event.entity])

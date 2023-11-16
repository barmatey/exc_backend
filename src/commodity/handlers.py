from src.base.repo import Repository
from src.base.repo.repository import OrderBy
from src.commodity import domain


class CreateCommodityCommand:
    def __init__(self, commodity: domain.Commodity, repo: Repository[domain.Commodity]):
        self._commodity = commodity
        self._repo = repo

    async def execute(self):
        await self._repo.add_many([self._commodity])


class GetManyCommoditiesCommand:
    def __init__(self, repo: Repository[domain.Commodity], filter_by: dict = None, order_by: OrderBy = None):
        self._filter_by = filter_by
        self._order_by = order_by
        self._repo = repo

    async def execute(self):
        return await self._repo.get_many(self._filter_by, self._order_by)


class CommandFactory:
    def __init__(self, repo: Repository[domain.Commodity]):
        self._repo = repo

    def create_commodity_command(self, commodity: domain.Commodity):
        return CreateCommodityCommand(commodity, self._repo)

    def get_many_commodities(self, filter_by: dict, order_by: OrderBy = None):
        return GetManyCommoditiesCommand(self._repo, filter_by, order_by)

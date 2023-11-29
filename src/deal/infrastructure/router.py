from uuid import UUID

from fastapi import APIRouter, Depends

from src import db
from src.base.repo.repository import OrderBy
from src.core import Ticker
from src.deal.infrastructure import bootstrap, schema

router_deal = APIRouter(
    prefix='/deal',
    tags=['Deal'],
)


@router_deal.get("/{account_uuid}")
async def get_account_deals(
        account_uuid: UUID,
        order_by: str = None,
        asc: bool = True,
        get_as=Depends(db.get_as),
):
    filter_by = {'account': account_uuid}
    order_by = OrderBy(order_by, asc) if order_by else None

    async with get_as as session:
        boot = bootstrap.Bootstrap(session)
        cmd = boot.get_deal_command_factory().get_many_deals(filter_by, order_by)
        deals = await cmd.execute()
        return [schema.DealSchema.from_entity(x) for x in deals]

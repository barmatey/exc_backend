from fastapi import APIRouter, Depends
from src import db

from . import bootstrap, schema

router_commodity = APIRouter(
    prefix='/commodity',
    tags=['Commodity'],
)


@router_commodity.post("/")
async def create_commodity(data: schema.CommoditySchema, get_as=Depends(db.get_as)) -> schema.CommoditySchema:
    async with get_as as session:
        boot = bootstrap.Bootstrap(session)
        await boot.get_command_factory().create_commodity_command(data.to_entity()).execute()
        await session.commit()
        return data


@router_commodity.get("/")
async def get_commodities(filter_by: str = None, get_as=Depends(db.get_as)) -> list[schema.CommoditySchema]:
    if filter_by is not None:
        raise NotImplemented
    async with get_as as session:
        boot = bootstrap.Bootstrap(session)
        entities = await boot.get_command_factory().get_many_commodities(filter_by).execute()
        result = [schema.CommoditySchema.from_entity(x) for x in entities]
        return result

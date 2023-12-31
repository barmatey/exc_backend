from uuid import UUID

from fastapi import APIRouter, Depends
from src import db

from . import bootstrap, schema

router_account = APIRouter(
    prefix='/account',
    tags=['Account'],
)


@router_account.post("/")
async def create_account(data: schema.AccountSchema, get_as=Depends(db.get_as)) -> schema.AccountSchema:
    async with get_as as session:
        boot = bootstrap.Bootstrap(session)
        await boot.get_command_factory().create_account(data.to_entity()).execute()
        await session.commit()
        return data


@router_account.post("/from-user-uuid")
async def create_account_from_user_uuid(user_uuid: UUID, get_as=Depends(db.get_as)) -> schema.AccountSchema:
    async with get_as as session:
        boot = bootstrap.Bootstrap(session)
        account = schema.AccountSchema(uuid=user_uuid, cash=100_000, buy_deals_amount=0, sell_deals_amount=0)
        await boot.get_command_factory().create_account(account.to_entity()).execute()
        await session.commit()
        return account


@router_account.get("/{account_uuid}")
async def get_account(account_uuid: UUID, get_as=Depends(db.get_as)) -> schema.AccountSchema:
    async with get_as as session:
        boot = bootstrap.Bootstrap(session)
        account = await boot.get_command_factory().get_account_by_uuid(account_uuid).execute()
        return schema.AccountSchema.from_entity(account)


@router_account.put("/{account_uuid}")
async def update_account(data: schema.AccountSchema, get_as=Depends(db.get_as)) -> schema.AccountSchema:
    async with get_as as session:
        boot = bootstrap.Bootstrap(session)
        await boot.get_command_factory().update_account(data.to_entity()).execute()
        await session.commit()
        return data

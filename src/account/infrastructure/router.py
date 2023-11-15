from fastapi import APIRouter, Depends
from src import db

from .. import domain, commands
from . import bootstrap, schema


router_account = APIRouter(
    prefix='/account',
    tags=['Account'],
)


@router_account.post("/")
async def create_account(data: schema.AccountSchema, get_as=Depends(db.get_as)) -> schema.AccountSchema:
    async with get_as as session:
        boot = bootstrap.Bootstrap(session)
        repo = boot.get_account_repo()
        acc = data.to_entity()
        cmd = commands.CreateAccount(account=acc, repo=repo)
        await cmd.execute()
        await session.commit()
        return schema.AccountSchema.from_entity(acc)

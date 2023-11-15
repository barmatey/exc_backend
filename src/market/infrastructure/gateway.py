from src.deal import (
    bootstrap as deal_bootstrap,
    domain as deal_domain,
    commands as deal_commands,
)
from src.account import (
    bootstrap as acc_bootstrap,
    domain as acc_domain,
    commands as acc_commands,
)
from .. import (
    domain as market_domain,
    handlers as market_handlers,
)


class DealGatewayM(market_handlers.DealGateway):
    def __init__(self, session):
        self._session = session

    async def create_deals_from_transaction(self, trs: market_domain.Transaction):
        deal_repo = deal_bootstrap.Bootstrap(self._session).get_deal_repo()
        cmd = deal_commands.CreateDeal(deal_domain.Deal(
            account=trs.buyer,
            ticker=trs.ticker,
            transaction=trs.uuid,
            status='PROCESSING',
            documents=[],
        ), deal_repo)
        await cmd.execute()

        cmd = deal_commands.CreateDeal(deal_domain.Deal(
            account=trs.seller,
            ticker=trs.ticker,
            transaction=trs.uuid,
            status='PROCESSING',
            documents=[],
        ), deal_repo)
        await cmd.execute()


class AccountGatewayM(market_handlers.AccountGateway):
    def __init__(self, session):
        self._session = session

    async def change_accounts_data(self, trs: market_domain.Transaction):
        acc_repo = acc_bootstrap.Bootstrap(self._session).get_account_repo()

        buyer = await acc_commands.GetAccountByUuid(trs.buyer, acc_repo).execute()
        buyer.reflect_purchase(trs.amount)
        await acc_commands.UpdateAccount(buyer, acc_repo).execute()

        seller = await acc_commands.GetAccountByUuid(trs.seller, acc_repo).execute()
        seller.reflect_sale(trs.amount)
        await acc_commands.UpdateAccount(seller, acc_repo).execute()

from src.deal import (
    bootstrap as deal_bootstrap,
    domain as deal_domain,
    commands as deal_commands,
)
from src.account import (
    bootstrap as acc_bootstrap,
    domain as acc_domain,
    handlers as acc_commands,
)
from .. import (
    domain as market_domain,
    handlers as market_handlers,
)


class DealGatewayM(market_handlers.DealGateway):
    def __init__(self, session):
        self._session = session

    async def create_deals_from_transaction(self, trs: market_domain.Transaction):
        factory = deal_bootstrap.Bootstrap(self._session).get_deal_command_factory()
        deals = (await factory.get_many_deals({'ticker': trs.ticker, 'account': trs.buyer}).execute())
        if len(deals) == 0:
            deal = deal_domain.Deal(
                account=trs.buyer,
                ticker=trs.ticker,
                status='PROCESSING',
                weighted_price=0,
                total_quantity=0,
            )
            deal.append_transaction(
                deal_domain.InnerTransaction(direction='BUY', price=trs.price, quantity=trs.quantity, uuid=trs.uuid)
            )
            await factory.create_deal(deal).execute()
        else:
            raise NotImplemented


class AccountGatewayM(market_handlers.AccountGateway):
    def __init__(self, session):
        self._session = session

    async def change_accounts_data(self, trs: market_domain.Transaction):
        acc_repo = acc_bootstrap.Bootstrap(self._session).get_account_repo()

        buyer: acc_domain.Account = await acc_commands.GetAccountByUuid(trs.buyer, acc_repo).execute()
        buyer.reflect_purchase(trs.amount)
        await acc_commands.UpdateAccount(buyer, acc_repo).execute()

        seller: acc_domain.Account = await acc_commands.GetAccountByUuid(trs.seller, acc_repo).execute()
        seller.reflect_sale(trs.amount)
        await acc_commands.UpdateAccount(seller, acc_repo).execute()

    async def check_account_has_permission_to_send_order(self, order: market_domain.Order):
        acc_repo = acc_bootstrap.Bootstrap(self._session).get_account_repo()
        acc: acc_domain.Account = await acc_commands.GetAccountByUuid(order.account, acc_repo).execute()
        if order.amount > acc.cash:
            raise PermissionError(f'order.amount > acc.cash ({order.amount} > {acc.cash})')

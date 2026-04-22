from bt_api_base.balance_utils import simple_balance_handler as _gmx_balance_handler
from bt_api_base.registry import ExchangeRegistry

from bt_api_gmx.containers.exchanges.gmx_exchange_data import GmxExchangeDataSpot
from bt_api_gmx.feeds.live_gmx.spot import GmxRequestDataSpot


def register_gmx():
    ExchangeRegistry.register_feed("GMX___DEX", GmxRequestDataSpot)
    ExchangeRegistry.register_exchange_data("GMX___DEX", GmxExchangeDataSpot)
    ExchangeRegistry.register_balance_handler("GMX___DEX", _gmx_balance_handler)


register_gmx()

from bt_api_gmx.containers.exchanges.gmx_exchange_data import (
    GmxChain,
    GmxExchangeDataSpot,
)
from bt_api_base.feeds.capability import Capability
from bt_api_gmx.feeds.live_gmx.request_base import GmxRequestData
from bt_api_base.functions.utils import update_extra_data
from bt_api_base.logging_factory import get_logger


class GmxRequestDataSpot(GmxRequestData):
    @classmethod
    def _capabilities(cls) -> set[Capability]:
        return {
            Capability.GET_TICK,
            Capability.GET_DEPTH,
            Capability.GET_KLINE,
            Capability.GET_EXCHANGE_INFO,
            Capability.GET_BALANCE,
            Capability.GET_ACCOUNT,
            Capability.MAKE_ORDER,
            Capability.CANCEL_ORDER,
        }

    def __init__(self, data_queue=None, **kwargs) -> None:
        super().__init__(data_queue, **kwargs)
        self.exchange_name = kwargs.get("exchange_name", "GMX___DEX")
        self.asset_type = kwargs.get("asset_type", "SPOT")

        chain_value = kwargs.get("chain", GmxChain.ARBITRUM)
        if isinstance(chain_value, str):
            try:
                self.chain = GmxChain(chain_value)
            except ValueError:
                self.chain = GmxChain.ARBITRUM
        else:
            self.chain = chain_value

        self._params = GmxExchangeDataSpot(self.chain)
        self.request_logger = get_logger("gmx_feed")

    def _get_tick(self, symbol: str, extra_data=None, **kwargs):
        request_type = "get_tick"
        path = self._params.get_rest_path("get_tick")

        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "chain": self.chain.value,
                "normalize_function": self._get_tick_normalize_function,
            },
        )

        return path, {}, extra_data

    @staticmethod
    def _get_tick_normalize_function(input_data, extra_data):
        if not input_data:
            return [], False

        tickers = input_data if isinstance(input_data, dict) else {}
        status = bool(tickers)

        return [tickers], status

    def get_tick(self, symbol: str, extra_data=None, **kwargs):
        path, params, extra_data = self._get_tick(symbol, extra_data, **kwargs)
        response = self.request(path, params, extra_data=extra_data)

        if symbol and response.data:
            tickers = response.data
            if isinstance(tickers, dict) and symbol in tickers:
                response.data = {symbol: tickers[symbol]}

        return response

    def async_get_tick(self, symbol: str, extra_data=None, **kwargs):
        path, params, extra_data = self._get_tick(symbol, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_kline(
        self, symbol: str, period: str, count: int = 1000, extra_data=None, **kwargs
    ):
        request_type = "get_kline"
        path = self._params.get_rest_path("get_candles")

        period_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
        }
        gmx_period = period_map.get(period, "1h")

        params = {
            "tokenSymbol": symbol,
            "period": gmx_period,
            "limit": min(count, 10000),
        }

        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "period": period,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "chain": self.chain.value,
                "normalize_function": self._get_kline_normalize_function,
            },
        )

        return path, params, extra_data

    @staticmethod
    def _get_kline_normalize_function(input_data, extra_data):
        if not input_data:
            return [], False

        candles = input_data.get("candles", []) if isinstance(input_data, dict) else []
        status = "candles" in input_data if isinstance(input_data, dict) else False

        return [candles], status

    def get_kline(self, symbol: str, period: str, count: int = 1000, extra_data=None, **kwargs):
        path, params, extra_data = self._get_kline(symbol, period, count, extra_data, **kwargs)
        return self.request(path, params, extra_data=extra_data)

    def async_get_kline(
        self, symbol: str, period: str, count: int = 1000, extra_data=None, **kwargs
    ):
        path, params, extra_data = self._get_kline(symbol, period, count, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_exchange_info(self, extra_data=None, **kwargs):
        request_type = "get_exchange_info"
        path = self._params.get_rest_path("get_markets")

        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "chain": self.chain.value,
                "normalize_function": self._get_exchange_info_normalize_function,
            },
        )

        return path, {}, extra_data

    @staticmethod
    def _get_exchange_info_normalize_function(input_data, extra_data):
        if not input_data:
            return [], False

        markets = input_data if isinstance(input_data, list) else []
        status = bool(markets)

        return [markets], status

    def get_exchange_info(self, extra_data=None, **kwargs):
        path, params, extra_data = self._get_exchange_info(extra_data, **kwargs)
        return self.request(path, params, extra_data=extra_data)

    def _get_depth(
        self, symbol: str, count: int = 20, extra_data=None, **kwargs
    ):
        request_type = "get_depth"

        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "chain": self.chain.value,
                "normalize_function": self._get_depth_normalize_function,
            },
        )

        path = self._params.get_rest_path("get_markets_info")

        return path, {}, extra_data

    @staticmethod
    def _get_depth_normalize_function(input_data, extra_data):
        if not input_data:
            return [], False

        markets = input_data if isinstance(input_data, list) else []
        status = bool(markets)

        return [markets], status

    def get_depth(self, symbol: str, count: int = 20, extra_data=None, **kwargs):
        path, params, extra_data = self._get_depth(symbol, count, extra_data, **kwargs)
        return self.request(path, params, extra_data=extra_data)

    def async_get_depth(self, symbol: str, count: int = 20, extra_data=None, **kwargs):
        path, params, extra_data = self._get_depth(symbol, count, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _make_order(
        self,
        symbol,
        volume,
        price,
        order_type,
        offset="open",
        post_only=False,
        client_order_id=None,
        extra_data=None,
        **kwargs,
    ):
        if extra_data is None:
            extra_data = {}
        extra_data.update(
            {
                "exchange_name": self.exchange_name,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "request_type": "make_order",
                "quantity": volume,
                "price": price,
                "order_type": order_type,
                "chain": self.chain.value,
            }
        )
        body = {
            "market": symbol,
            "size": str(volume),
            "price": str(price),
            "orderType": order_type,
        }
        return "POST /orders", body, extra_data

    def make_order(
        self,
        symbol,
        volume,
        price,
        order_type,
        offset="open",
        post_only=False,
        client_order_id=None,
        extra_data=None,
        **kwargs,
    ):
        path, body, extra_data = self._make_order(
            symbol,
            volume,
            price,
            order_type,
            offset,
            post_only,
            client_order_id,
            extra_data,
            **kwargs,
        )
        return self.request(path, body=body, extra_data=extra_data)

    def _cancel_order(self, symbol, order_id, extra_data=None, **kwargs):
        if extra_data is None:
            extra_data = {}
        extra_data.update(
            {
                "exchange_name": self.exchange_name,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "request_type": "cancel_order",
                "order_id": order_id,
            }
        )
        return f"DELETE /orders/{order_id}", {}, extra_data

    def cancel_order(self, symbol, order_id, extra_data=None, **kwargs):
        path, params, extra_data = self._cancel_order(symbol, order_id, extra_data, **kwargs)
        return self.request(path, params=params, extra_data=extra_data)

    def _query_order(self, symbol, order_id, extra_data=None, **kwargs):
        if extra_data is None:
            extra_data = {}
        extra_data.update(
            {
                "exchange_name": self.exchange_name,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "request_type": "query_order",
                "order_id": order_id,
            }
        )
        return f"GET /orders/{order_id}", {}, extra_data

    def query_order(self, symbol, order_id, extra_data=None, **kwargs):
        path, params, extra_data = self._query_order(symbol, order_id, extra_data, **kwargs)
        return self.request(path, params=params, extra_data=extra_data)

    def _get_open_orders(self, symbol=None, extra_data=None, **kwargs):
        if extra_data is None:
            extra_data = {}
        extra_data.update(
            {
                "exchange_name": self.exchange_name,
                "symbol_name": symbol or "",
                "asset_type": self.asset_type,
                "request_type": "get_open_orders",
            }
        )
        return "GET /orders", {}, extra_data

    def get_open_orders(self, symbol=None, extra_data=None, **kwargs):
        path, params, extra_data = self._get_open_orders(symbol, extra_data, **kwargs)
        return self.request(path, params=params, extra_data=extra_data)

    def _get_account(self, symbol=None, extra_data=None, **kwargs):
        if extra_data is None:
            extra_data = {}
        extra_data.update(
            {
                "exchange_name": self.exchange_name,
                "symbol_name": symbol or "",
                "asset_type": self.asset_type,
                "request_type": "get_account",
                "chain": self.chain.value,
            }
        )
        return self._params.get_rest_path("get_markets"), {}, extra_data

    def get_account(self, symbol=None, extra_data=None, **kwargs):
        path, params, extra_data = self._get_account(symbol, extra_data, **kwargs)
        return self.request(path, params=params, extra_data=extra_data)

    def _get_balance(self, symbol=None, extra_data=None, **kwargs):
        if extra_data is None:
            extra_data = {}
        extra_data.update(
            {
                "exchange_name": self.exchange_name,
                "symbol_name": symbol or "",
                "asset_type": self.asset_type,
                "request_type": "get_balance",
                "chain": self.chain.value,
            }
        )
        return self._params.get_rest_path("get_markets"), {}, extra_data

    def get_balance(self, symbol=None, extra_data=None, **kwargs):
        path, params, extra_data = self._get_balance(symbol, extra_data, **kwargs)
        return self.request(path, params=params, extra_data=extra_data)

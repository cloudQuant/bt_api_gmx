from bt_api_base.containers.requestdatas.request_data import RequestData
from bt_api_base.feeds.capability import Capability
from bt_api_base.feeds.feed import Feed
from bt_api_base.feeds.http_client import HttpClient
from bt_api_base.logging_factory import get_logger

from bt_api_gmx.containers.exchanges.gmx_exchange_data import (
    GmxChain,
    GmxExchangeDataSpot,
)


class GmxRequestData(Feed):
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
        self.data_queue = data_queue
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
        self.async_logger = get_logger("gmx_feed")

        self._http_client = HttpClient(venue=self.exchange_name, timeout=30)

    def _get_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "User-Agent": "bt_api/1.0",
        }

    def request(
        self,
        path: str,
        params: dict = None,
        body=None,
        extra_data=None,
        timeout: int = 10,
    ):
        if params is None:
            params = {}
        method = path.split()[0] if " " in path else "GET"
        endpoint = path.split()[1] if " " in path else path

        url = self._params.get_rest_url() + endpoint
        headers = self._get_headers()

        try:
            response = self._http_client.request(
                method=method,
                url=url,
                headers=headers,
                json_data=body if method == "POST" else None,
                params=params,
            )
            return RequestData(response, extra_data)

        except Exception as e:
            self.request_logger.error(f"GMX request failed: {e}")
            raise

    async def async_request(
        self,
        path: str,
        params: dict = None,
        body=None,
        extra_data=None,
        timeout: int = 5,
    ):
        if params is None:
            params = {}
        method = path.split()[0] if " " in path else "GET"
        endpoint = path.split()[1] if " " in path else path

        url = self._params.get_rest_url() + endpoint
        headers = self._get_headers()

        try:
            response = await self._http_client.async_request(
                method=method,
                url=url,
                headers=headers,
                json_data=body if method == "POST" else None,
                params=params,
            )
            return RequestData(response, extra_data)
        except Exception as e:
            self.async_logger.error(f"GMX async request failed: {e}")
            raise

    def async_callback(self, future):
        try:
            result = future.result()
            if result is not None:
                self.push_data_to_queue(result)
        except Exception as e:
            self.async_logger.error(f"Async callback error: {e}")

    def _get_server_time(self, extra_data=None, **kwargs):
        if extra_data is None:
            extra_data = {}
        extra_data.update(
            {
                "exchange_name": self.exchange_name,
                "symbol_name": "",
                "asset_type": self.asset_type,
                "request_type": "get_server_time",
                "server_time": 0,
            }
        )
        return "GET /prices/tickers", {}, extra_data

    def get_server_time(self, extra_data=None, **kwargs):
        path, params, extra_data = self._get_server_time(extra_data, **kwargs)
        import time

        return RequestData({"server_time": time.time()}, extra_data)

    def push_data_to_queue(self, data):
        if self.data_queue is not None:
            self.data_queue.put(data)
        else:
            raise RuntimeError("Queue not initialized")

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def is_connected(self) -> bool:
        return True

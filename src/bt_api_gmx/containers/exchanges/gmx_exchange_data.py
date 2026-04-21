import os
from bt_api_base._compat import StrEnum
from bt_api_base.logging_factory import get_logger

logger = get_logger("gmx_exchange_data")

_gmx_config = None
_gmx_config_loaded = False
_gmx_config_raw = None


def _get_gmx_config():
    global _gmx_config, _gmx_config_loaded, _gmx_config_raw
    if _gmx_config_loaded:
        return _gmx_config
    try:
        import yaml
        from bt_api_base.config_loader import load_exchange_config

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(base_dir, "configs", "gmx.yaml")
        if os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                _gmx_config_raw = yaml.safe_load(f)

            _gmx_config = load_exchange_config(config_path)
            _gmx_config._raw_config = _gmx_config_raw
        _gmx_config_loaded = True
    except (OSError, ValueError, KeyError, ImportError) as e:
        logger.warning(f"Failed to load gmx.yaml config: {e}")
    return _gmx_config


class GmxChain(StrEnum):
    ARBITRUM = "arbitrum"
    AVALANCHE = "avalanche"
    BOTANIX = "botanix"


class GmxExchangeData:
    DEFAULT_CHAIN = GmxChain.ARBITRUM

    API_URLS = {
        GmxChain.ARBITRUM: "https://arbitrum-api.gmxinfra.io",
        GmxChain.AVALANCHE: "https://avalanche-api.gmxinfra.io",
        GmxChain.BOTANIX: "https://botanix-api.gmxinfra.io",
    }

    def __init__(self, chain=GmxChain.ARBITRUM, asset_type=None) -> None:
        self.chain = chain
        self.asset_type = asset_type or "spot"
        self.config = _get_gmx_config()

        if self.config and asset_type:
            self._load_from_config(asset_type)
        else:
            self.rest_url = self.API_URLS[self.chain]
            self.rest_paths = {}
            self.wss_paths = {}

    def _load_from_config(self, asset_type):
        if not self.config:
            return False

        asset_cfg = self.config.asset_types.get(asset_type)
        if not asset_cfg:
            return False

        raw = getattr(self.config, "_raw_config", None)
        if raw:
            raw_base_urls = raw.get("base_urls", {})
            if raw_base_urls and raw_base_urls.get("rest"):
                chain_url = raw_base_urls["rest"].get(self.chain.value)
                if chain_url:
                    self.rest_url = chain_url
                else:
                    self.rest_url = list(raw_base_urls["rest"].values())[0]
            else:
                self.rest_url = self.API_URLS[self.chain]
        else:
            self.rest_url = self.API_URLS[self.chain]

        if asset_cfg.rest_paths:
            self.rest_paths = dict(asset_cfg.rest_paths)
        else:
            self.rest_paths = {}

        if hasattr(asset_cfg, "wss_paths") and asset_cfg.wss_paths:
            self.wss_paths = dict(asset_cfg.wss_paths)
        else:
            self.wss_paths = {}

        return True

    def get_rest_url(self):
        return self.rest_url

    def get_chain_value(self):
        return self.chain.value

    def get_rest_path(self, request_type):
        if self.rest_paths and request_type in self.rest_paths:
            return self.rest_paths[request_type]

        standard_paths = {
            "get_server_time": "GET /ping",
            "get_tick": "GET /prices/tickers",
            "get_candles": "GET /prices/candles",
            "get_tokens": "GET /tokens",
            "get_markets": "GET /markets",
        }
        return standard_paths.get(request_type, f"GET /{request_type}")


class GmxExchangeDataSpot(GmxExchangeData):
    kline_periods = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
    }

    legal_currency = ["USDC", "USDT", "USD", "BTC", "ETH", "AVAX"]

    supported_symbols = ["BTC", "ETH", "USDC", "USDT", "AVAX", "ARB", "UNI", "LINK"]

    def __init__(self, chain=None):
        if chain is None:
            chain = GmxExchangeData.DEFAULT_CHAIN
        if isinstance(chain, str):
            try:
                chain = GmxChain(chain)
            except ValueError:
                chain = GmxExchangeData.DEFAULT_CHAIN

        super().__init__(chain, "spot")

        raw = getattr(self.config, "_raw_config", None)
        if raw:
            if "kline_periods" in raw:
                self.kline_periods = dict(raw["kline_periods"])

            if "legal_currency" in raw:
                self.legal_currency = list(raw["legal_currency"])

            asset_cfg = raw.get("asset_types", {}).get("spot", {})
            if "legal_currency" in asset_cfg:
                self.legal_currency = list(asset_cfg["legal_currency"])

            self.supported_symbols = self.legal_currency.copy()

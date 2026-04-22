# GMX Documentation

## English

Welcome to the GMX documentation for bt_api.

### Quick Start

```bash
pip install bt_api_gmx
```

```python
from bt_api_py import BtApi

api = BtApi(exchange_kwargs={
    "GMX___SPOT": {
        "api_key": "your_api_key",
        "secret": "your_secret",
    }
})

ticker = api.get_tick("GMX___SPOT", "BTCUSDT")
print(ticker)
```

## 中文

欢迎使用 bt_api 的 GMX 文档。

### 快速开始

```bash
pip install bt_api_gmx
```

```python
from bt_api_py import BtApi

api = BtApi(exchange_kwargs={
    "GMX___SPOT": {
        "api_key": "your_api_key",
        "secret": "your_secret",
    }
})

ticker = api.get_tick("GMX___SPOT", "BTCUSDT")
print(ticker)
```

## API Reference

See source code in `src/bt_api_gmx/` for detailed API documentation.

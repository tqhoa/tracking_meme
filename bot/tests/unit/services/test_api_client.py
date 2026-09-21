import httpx
import pytest
import respx

from app.services.api_client import ApiClient

_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
_BASE = "http://api:8000"

REPORT = {
    "success": True,
    "data": {
        "token": {"address": _ADDRESS, "name": "USD Coin", "symbol": "USDC", "chain": "eth", "dex": "uniswap"},
        "market": {
            "price_usd": 1.0, "market_cap": 40000000000, "fdv": 40000000000, "liquidity_usd": 5000000,
            "volume": {"m5": 0, "h1": 0, "h6": 0, "h24": 5000000},
            "price_change": {"m5": 0.0, "h1": 0.0, "h6": 0.0, "h24": 0.01},
            "txns_h24": {"buys": 1000, "sells": 950},
        },
        "security": {
            "is_honeypot": False, "buy_tax": 0.0, "sell_tax": 0.0, "is_open_source": True,
            "owner_address": None, "creator_address": None,
            "holder_count": 500000, "top_10_holders_pct": 80.0, "lp_locked": True,
        },
        "social": {"twitter": "https://twitter.com/circle", "website": "https://centre.io", "telegram": None},
        "analysis": {"risk_flags": [], "positive_flags": ["Stablecoin"], "summary": "ok", "risk_level": "LOW"},
        "data_source": "dexscreener",
        "fetched_at": "2026-09-21T10:00:00+00:00",
    },
}


@respx.mock
async def test_search_token_returns_data_on_200() -> None:
    respx.post(f"{_BASE}/api/v1/token/search").mock(
        return_value=httpx.Response(200, json=REPORT)
    )
    client = ApiClient(base_url=_BASE)
    result = await client.search_token(_ADDRESS)
    assert result["success"] is True
    assert result["data"]["token"]["symbol"] == "USDC"


@respx.mock
async def test_search_token_returns_error_dict_on_404() -> None:
    respx.post(f"{_BASE}/api/v1/token/search").mock(
        return_value=httpx.Response(404, json={"success": False, "error": {"code": "TOKEN_NOT_FOUND", "message": "Not found"}})
    )
    client = ApiClient(base_url=_BASE)
    result = await client.search_token(_ADDRESS)
    assert result["success"] is False
    assert result["error"]["code"] == "TOKEN_NOT_FOUND"


@respx.mock
async def test_search_token_returns_error_dict_on_network_failure() -> None:
    respx.post(f"{_BASE}/api/v1/token/search").mock(
        side_effect=httpx.ConnectError("refused")
    )
    client = ApiClient(base_url=_BASE)
    result = await client.search_token(_ADDRESS)
    assert result["success"] is False
    assert "error" in result

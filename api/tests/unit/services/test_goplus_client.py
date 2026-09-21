import pytest
import httpx
import respx

from app.services.goplus_client import GoplusClient

_CHAIN_ID = "1"
_ADDRESS = "0xabc123def456abc123def456abc123def456abc1"

MOCK_RESPONSE = {
    "code": 1,
    "result": {
        _ADDRESS.lower(): {
            "is_honeypot": "0",
            "buy_tax": "0.05",
            "sell_tax": "0.05",
            "is_open_source": "1",
            "owner_address": "0x000",
            "creator_address": "0x111",
            "holder_count": "1200",
            "lp_locked": "0",
            "top10_holder_rate": "0.452",
        }
    },
}


@respx.mock
async def test_fetch_security_parses_all_fields() -> None:
    respx.get(f"https://api.gopluslabs.io/api/v1/token_security/{_CHAIN_ID}").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    client = GoplusClient()
    result = await client.fetch_security(_ADDRESS, _CHAIN_ID)
    assert result is not None
    assert result["is_honeypot"] is False
    assert result["buy_tax"] == pytest.approx(0.05)
    assert result["sell_tax"] == pytest.approx(0.05)
    assert result["is_open_source"] is True
    assert result["holder_count"] == 1200
    assert result["top_10_holders_pct"] == pytest.approx(45.2)
    assert result["lp_locked"] is False


@respx.mock
async def test_fetch_security_returns_none_on_missing_address() -> None:
    respx.get(f"https://api.gopluslabs.io/api/v1/token_security/{_CHAIN_ID}").mock(
        return_value=httpx.Response(200, json={"code": 1, "result": {}})
    )
    client = GoplusClient()
    result = await client.fetch_security(_ADDRESS, _CHAIN_ID)
    assert result is None


@respx.mock
async def test_fetch_security_returns_none_on_http_error() -> None:
    respx.get(f"https://api.gopluslabs.io/api/v1/token_security/{_CHAIN_ID}").mock(
        return_value=httpx.Response(500)
    )
    client = GoplusClient()
    result = await client.fetch_security(_ADDRESS, _CHAIN_ID)
    assert result is None


@respx.mock
async def test_fetch_security_returns_none_on_network_error() -> None:
    respx.get(f"https://api.gopluslabs.io/api/v1/token_security/{_CHAIN_ID}").mock(
        side_effect=httpx.ConnectError("timeout")
    )
    client = GoplusClient()
    result = await client.fetch_security(_ADDRESS, _CHAIN_ID)
    assert result is None



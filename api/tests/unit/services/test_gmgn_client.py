import httpx
import respx

from app.services.gmgn_client import GmgnClient

MOCK_TOKEN_INFO = {
    "code": 0,
    "data": {
        "token": {
            "address": "0xabc",
            "symbol": "HENRY",
            "name": "Henry",
            "price": 0.000285,
            "market_cap": 285000,
            "fdv": 285000,
            "liquidity": 41000,
            "volume_24h": 2190000,
            "price_change_percent1h": -8.47,
            "price_change_percent24h": 23572.0,
            "swaps_24h": 7999,
            "buys_24h": 4220,
            "sells_24h": 3779,
            "twitter": "https://twitter.com/henry",
            "website": None,
            "telegram": None,
        }
    },
}

MOCK_SECURITY = {
    "code": 0,
    "data": {
        "is_honeypot": 0,
        "buy_tax": "0",
        "sell_tax": "0",
        "is_open_source": 1,
        "owner_address": "0x000",
        "creator_address": "0x111",
        "holder_count": 1200,
        "lp_locked_percent": "0",
    },
}


@respx.mock
async def test_fetch_token_info_returns_parsed_data() -> None:
    respx.get("https://gmgn.ai/defi/quotation/v1/tokens/eth/0xabc").mock(
        return_value=httpx.Response(200, json=MOCK_TOKEN_INFO)
    )
    client = GmgnClient()
    result = await client.fetch_token_info("0xabc", "eth")
    assert result is not None
    assert result["symbol"] == "HENRY"
    assert result["price"] == 0.000285


@respx.mock
async def test_fetch_token_info_returns_none_on_404() -> None:
    respx.get("https://gmgn.ai/defi/quotation/v1/tokens/eth/0xabc").mock(
        return_value=httpx.Response(404)
    )
    client = GmgnClient()
    result = await client.fetch_token_info("0xabc", "eth")
    assert result is None


@respx.mock
async def test_fetch_token_info_returns_none_on_error_code() -> None:
    respx.get("https://gmgn.ai/defi/quotation/v1/tokens/eth/0xabc").mock(
        return_value=httpx.Response(200, json={"code": 1, "msg": "not found"})
    )
    client = GmgnClient()
    result = await client.fetch_token_info("0xabc", "eth")
    assert result is None


@respx.mock
async def test_fetch_security_returns_parsed_data() -> None:
    respx.get("https://gmgn.ai/defi/quotation/v1/token_security/eth/0xabc").mock(
        return_value=httpx.Response(200, json=MOCK_SECURITY)
    )
    client = GmgnClient()
    result = await client.fetch_token_security("0xabc", "eth")
    assert result is not None
    assert result["is_honeypot"] == 0


@respx.mock
async def test_fetch_security_returns_none_on_error() -> None:
    respx.get("https://gmgn.ai/defi/quotation/v1/token_security/eth/0xabc").mock(
        side_effect=httpx.ConnectError("timeout")
    )
    client = GmgnClient()
    result = await client.fetch_token_security("0xabc", "eth")
    assert result is None

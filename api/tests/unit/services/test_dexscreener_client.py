import pytest
import respx
import httpx

from app.services.dexscreener_client import DexScreenerClient, parse_pair

MOCK_PAIR = {
    "chainId": "ethereum",
    "dexId": "uniswap",
    "baseToken": {"address": "0xabc", "name": "Henry", "symbol": "HENRY"},
    "priceUsd": "0.000285",
    "marketCap": 285000,
    "fdv": 285000,
    "liquidity": {"usd": 41000},
    "volume": {"m5": 100, "h1": 74000, "h6": 1820000, "h24": 2190000},
    "priceChange": {"m5": 3.67, "h1": -8.47, "h6": 274.0, "h24": 23572.0},
    "txns": {"h24": {"buys": 4220, "sells": 3779}},
    "info": {"socials": [{"type": "twitter", "url": "https://twitter.com/henry"}], "websites": []},
}

MOCK_RESPONSE = {"pairs": [MOCK_PAIR]}


def test_parse_pair_extracts_all_fields() -> None:
    result = parse_pair(MOCK_PAIR)
    assert result["token"]["name"] == "Henry"
    assert result["token"]["symbol"] == "HENRY"
    assert result["token"]["chain"] == "eth"
    assert result["market"]["price_usd"] == pytest.approx(0.000285)
    assert result["market"]["liquidity_usd"] == 41000
    assert result["market"]["volume"]["h24"] == 2190000
    assert result["market"]["price_change"]["h6"] == 274.0
    assert result["market"]["txns_h24"]["buys"] == 4220
    assert result["social"]["twitter"] == "https://twitter.com/henry"


def test_parse_pair_maps_chain_id() -> None:
    pair = {**MOCK_PAIR, "chainId": "bsc"}
    result = parse_pair(pair)
    assert result["token"]["chain"] == "bsc"


def test_parse_pair_handles_missing_optional_fields() -> None:
    minimal = {
        "chainId": "ethereum",
        "dexId": "uniswap",
        "baseToken": {"address": "0xabc", "name": "X", "symbol": "X"},
        "priceUsd": "0",
    }
    result = parse_pair(minimal)
    assert result["market"]["market_cap"] == 0
    assert result["social"]["twitter"] is None


@respx.mock
async def test_fetch_returns_parsed_data() -> None:
    respx.get("https://api.dexscreener.com/latest/dex/tokens/0xabc").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    client = DexScreenerClient()
    result = await client.fetch_by_address("0xabc")
    assert result is not None
    assert result["token"]["symbol"] == "HENRY"


@respx.mock
async def test_fetch_returns_none_on_empty_pairs() -> None:
    respx.get("https://api.dexscreener.com/latest/dex/tokens/0xabc").mock(
        return_value=httpx.Response(200, json={"pairs": []})
    )
    client = DexScreenerClient()
    result = await client.fetch_by_address("0xabc")
    assert result is None


@respx.mock
async def test_fetch_returns_none_on_404() -> None:
    respx.get("https://api.dexscreener.com/latest/dex/tokens/0xabc").mock(
        return_value=httpx.Response(404)
    )
    client = DexScreenerClient()
    result = await client.fetch_by_address("0xabc")
    assert result is None


@respx.mock
async def test_fetch_filters_by_chain_eth() -> None:
    pairs = [
        {**MOCK_PAIR, "chainId": "bsc"},
        {**MOCK_PAIR, "chainId": "ethereum"},
    ]
    respx.get("https://api.dexscreener.com/latest/dex/tokens/0xabc").mock(
        return_value=httpx.Response(200, json={"pairs": pairs})
    )
    client = DexScreenerClient()
    result = await client.fetch_by_address("0xabc", chain="eth")
    assert result is not None
    assert result["token"]["chain"] == "eth"


@respx.mock
async def test_fetch_prefers_eth_bsc_over_other_chains_when_no_chain_hint() -> None:
    pairs = [
        {**MOCK_PAIR, "chainId": "pulsechain", "liquidity": {"usd": 999999}},
        {**MOCK_PAIR, "chainId": "ethereum", "liquidity": {"usd": 1000}},
    ]
    respx.get("https://api.dexscreener.com/latest/dex/tokens/0xabc").mock(
        return_value=httpx.Response(200, json={"pairs": pairs})
    )
    client = DexScreenerClient()
    result = await client.fetch_by_address("0xabc", chain=None)
    assert result is not None
    assert result["token"]["chain"] == "eth"

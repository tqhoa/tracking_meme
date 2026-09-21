from unittest.mock import AsyncMock, patch

import pytest

from app.exceptions import AppError
from app.services.token_service import TokenService


@pytest.fixture
def gmgn() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def dex() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def goplus() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def analysis() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def svc(gmgn: AsyncMock, dex: AsyncMock, goplus: AsyncMock, analysis: AsyncMock) -> TokenService:
    return TokenService(gmgn=gmgn, dex=dex, goplus=goplus, analysis=analysis)


ETH_DATA = {
    "token": {"address": "0xabc", "name": "X", "symbol": "X", "chain": "eth", "dex": "uniswap"},
    "market": {"price_usd": 1.0, "market_cap": 1000, "fdv": 1000, "liquidity_usd": 5000,
               "volume": {"m5": 0, "h1": 0, "h6": 0, "h24": 0},
               "price_change": {"m5": 0, "h1": 0, "h6": 0, "h24": 0},
               "txns_h24": {"buys": 10, "sells": 5}},
    "social": {"twitter": None, "website": None, "telegram": None},
}

SECURITY_DATA = {
    "is_honeypot": False, "buy_tax": 0.0, "sell_tax": 0.0,
    "is_open_source": True, "owner_address": None, "creator_address": None,
    "holder_count": 100, "top_10_holders_pct": 30.0, "lp_locked": True,
}

ANALYSIS_DATA = {
    "risk_flags": [], "positive_flags": [], "summary": "ok", "risk_level": "LOW"
}


async def test_gmgn_eth_used_when_chain_is_eth(svc: TokenService, gmgn: AsyncMock, dex: AsyncMock, analysis: AsyncMock) -> None:
    gmgn.fetch_token_info.return_value = ETH_DATA["token"]
    gmgn.fetch_token_security.return_value = None
    dex.fetch_by_address.return_value = ETH_DATA
    analysis.generate.return_value = ANALYSIS_DATA

    await svc.search("0xabc", chain="eth")
    gmgn.fetch_token_info.assert_called_once_with("0xabc", "eth")


async def test_dexscreener_fallback_when_gmgn_returns_none(svc: TokenService, gmgn: AsyncMock, dex: AsyncMock, analysis: AsyncMock) -> None:
    gmgn.fetch_token_info.return_value = None
    dex.fetch_by_address.return_value = ETH_DATA
    analysis.generate.return_value = ANALYSIS_DATA

    result = await svc.search("0xabc", chain=None)
    assert dex.fetch_by_address.called
    assert result["data_source"] == "dexscreener"


async def test_raises_token_not_found_when_all_sources_none(svc: TokenService, gmgn: AsyncMock, dex: AsyncMock) -> None:
    gmgn.fetch_token_info.return_value = None
    dex.fetch_by_address.return_value = None

    with pytest.raises(AppError) as exc:
        await svc.search("0xabc", chain=None)
    assert exc.value.code == "TOKEN_NOT_FOUND"


async def test_auto_detect_tries_eth_then_bsc(svc: TokenService, gmgn: AsyncMock, dex: AsyncMock, analysis: AsyncMock) -> None:
    gmgn.fetch_token_info.side_effect = [None, None]
    dex.fetch_by_address.return_value = ETH_DATA
    analysis.generate.return_value = ANALYSIS_DATA

    await svc.search("0xabc", chain=None)
    calls = [c.args[1] for c in gmgn.fetch_token_info.call_args_list]
    assert calls == ["eth", "bsc"]


async def test_goplus_failure_is_non_fatal(svc: TokenService, gmgn: AsyncMock, dex: AsyncMock, goplus: AsyncMock, analysis: AsyncMock) -> None:
    gmgn.fetch_token_info.return_value = None
    dex.fetch_by_address.return_value = ETH_DATA
    goplus.fetch_security.return_value = None
    analysis.generate.return_value = ANALYSIS_DATA

    result = await svc.search("0xabc", chain=None)
    assert result is not None

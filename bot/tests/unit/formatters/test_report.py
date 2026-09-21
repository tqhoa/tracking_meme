from app.formatters.report import format_number, format_pct, format_report

REPORT_DATA = {
    "token": {"address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "name": "Henry", "symbol": "HENRY", "chain": "eth", "dex": "uniswap_v2"},
    "market": {
        "price_usd": 0.000285, "market_cap": 285000, "fdv": 285000, "liquidity_usd": 41000,
        "volume": {"m5": 0, "h1": 74000, "h6": 1820000, "h24": 2190000},
        "price_change": {"m5": 3.67, "h1": -8.47, "h6": 274.0, "h24": 23572.0},
        "txns_h24": {"buys": 4220, "sells": 3779},
    },
    "security": {
        "is_honeypot": False, "buy_tax": 0.0, "sell_tax": 0.0, "is_open_source": True,
        "owner_address": None, "creator_address": None,
        "holder_count": 1200, "top_10_holders_pct": 45.2, "lp_locked": False,
    },
    "social": {"twitter": "https://twitter.com/henry", "website": None, "telegram": None},
    "analysis": {
        "risk_flags": ["Volume 24h gấp ~8x MCap", "Liquidity thấp"],
        "positive_flags": ["Buy/sell cân bằng"],
        "summary": "Token rủi ro cao.",
        "risk_level": "HIGH",
    },
    "data_source": "dexscreener",
    "fetched_at": "2026-09-21T10:00:00+00:00",
}


def test_format_number_thousands() -> None:
    assert format_number(285000) == "$285K"


def test_format_number_millions() -> None:
    assert format_number(2190000) == "$2.19M"


def test_format_number_below_thousand() -> None:
    assert format_number(500) == "$500"


def test_format_pct_positive() -> None:
    assert format_pct(3.67) == "+3.67%"


def test_format_pct_negative() -> None:
    assert format_pct(-8.47) == "-8.47%"


def test_format_report_contains_symbol() -> None:
    text = format_report(REPORT_DATA)
    assert "HENRY" in text


def test_format_report_contains_chain() -> None:
    text = format_report(REPORT_DATA)
    assert "Ethereum" in text or "eth" in text.lower()


def test_format_report_contains_risk_flags() -> None:
    text = format_report(REPORT_DATA)
    assert "Volume 24h gấp ~8x MCap" in text


def test_format_report_contains_summary() -> None:
    text = format_report(REPORT_DATA)
    assert "Token rủi ro cao" in text


def test_format_report_has_security_section() -> None:
    text = format_report(REPORT_DATA)
    assert "Honeypot" in text or "honeypot" in text.lower()

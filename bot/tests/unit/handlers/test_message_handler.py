from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_update(text: str) -> MagicMock:
    update = MagicMock()
    update.message.text = text
    update.message.reply_text = AsyncMock()
    update.message.chat_id = 123
    return update


def _make_context() -> MagicMock:
    return MagicMock()


async def test_message_with_address_calls_api_and_sends_report() -> None:
    from app.handlers.message import handle_message

    update = _make_update("Kiểm tra token này: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    ctx = _make_context()

    mock_result = {
        "success": True,
        "data": {
            "token": {"address": "0xabc", "name": "X", "symbol": "X", "chain": "eth", "dex": "uni"},
            "market": {
                "price_usd": 1.0, "market_cap": 1000, "fdv": 1000, "liquidity_usd": 5000,
                "volume": {"m5": 0, "h1": 0, "h6": 0, "h24": 100},
                "price_change": {"m5": 0, "h1": 0, "h6": 0, "h24": 0},
                "txns_h24": {"buys": 10, "sells": 5},
            },
            "security": {
                "is_honeypot": False, "buy_tax": 0, "sell_tax": 0, "is_open_source": True,
                "owner_address": None, "creator_address": None,
                "holder_count": 100, "top_10_holders_pct": 20.0, "lp_locked": True,
            },
            "social": {"twitter": None, "website": None, "telegram": None},
            "analysis": {"risk_flags": [], "positive_flags": [], "summary": "ok", "risk_level": "LOW"},
            "data_source": "dexscreener",
            "fetched_at": "2026-09-21T10:00:00+00:00",
        },
    }

    with patch("app.handlers.message.get_settings") as mock_cfg, \
         patch("app.handlers.message.ApiClient") as MockClient:
        mock_cfg.return_value = MagicMock(api_base_url="http://api:8000")
        instance = MockClient.return_value
        instance.search_token = AsyncMock(return_value=mock_result)
        await handle_message(update, ctx)

    update.message.reply_text.assert_called()
    call_text = update.message.reply_text.call_args[0][0]
    assert "X" in call_text


async def test_message_without_address_is_ignored() -> None:
    from app.handlers.message import handle_message

    update = _make_update("Hello bot, how are you?")
    ctx = _make_context()

    with patch("app.handlers.message.ApiClient") as MockClient:
        await handle_message(update, ctx)

    update.message.reply_text.assert_not_called()


async def test_token_not_found_sends_error_message() -> None:
    from app.handlers.message import handle_message

    update = _make_update("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    ctx = _make_context()

    error_result = {
        "success": False,
        "error": {"code": "TOKEN_NOT_FOUND", "message": "Not found"},
    }

    with patch("app.handlers.message.get_settings") as mock_cfg, \
         patch("app.handlers.message.ApiClient") as MockClient:
        mock_cfg.return_value = MagicMock(api_base_url="http://api:8000")
        instance = MockClient.return_value
        instance.search_token = AsyncMock(return_value=error_result)
        await handle_message(update, ctx)

    update.message.reply_text.assert_called()
    call_text = update.message.reply_text.call_args[0][0]
    assert "Không tìm thấy" in call_text or "không tìm thấy" in call_text.lower()

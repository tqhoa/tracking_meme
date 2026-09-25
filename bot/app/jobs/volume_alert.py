import logging

from telegram.ext import ContextTypes

from app.config import get_settings
from app.formatters.report import format_report
from app.handlers.alert import get_subscribed_chats
from app.services.api_client import ApiClient
from app.services.volume_scanner import TokenAlert, VolumeScanner

logger = logging.getLogger(__name__)


def _build_header(total: int) -> str:
    return f"🔥 *Top Volume Tokens* (scan 5 phút) — {total} token\n"


async def volume_alert_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    chats = get_subscribed_chats()
    if not chats:
        return

    scanner = VolumeScanner()
    try:
        alerts = await scanner.scan()
    except Exception:
        logger.exception("volume_alert.scan_failed")
        return

    if not alerts:
        logger.info("volume_alert.no_results")
        return

    settings = get_settings()
    api = ApiClient(base_url=settings.api_base_url)

    # Fetch all full reports once, then broadcast to all chats
    reports: list[str] = []
    for alert in alerts:
        reports.append(await _fetch_full_report(api, alert))

    header = _build_header(len(alerts))
    for chat_id in chats:
        try:
            await context.bot.send_message(chat_id=chat_id, text=header, parse_mode="Markdown")
        except Exception:
            logger.exception("volume_alert.send_header_failed", extra={"chat_id": chat_id})
            continue

        for alert, text in zip(alerts, reports):
            try:
                await context.bot.send_message(
                    chat_id=chat_id, text=text, parse_mode="Markdown"
                )
            except Exception:
                logger.exception(
                    "volume_alert.send_token_failed",
                    extra={"chat_id": chat_id, "address": alert.address},
                )


async def _fetch_full_report(api: ApiClient, alert: TokenAlert) -> str:
    result = await api.search_token(alert.address, alert.chain)
    if result.get("success") and result.get("data"):
        try:
            return format_report(result["data"])
        except Exception:
            logger.exception("volume_alert.format_failed", extra={"address": alert.address})
    return _fallback_message(alert)


def _fallback_message(a: TokenAlert) -> str:
    sign_h1 = "+" if a.price_change_h1 >= 0 else ""
    sign_h24 = "+" if a.price_change_h24 >= 0 else ""

    def fmt(v: float) -> str:
        if v >= 1_000_000:
            return f"${v / 1_000_000:.1f}M"
        if v >= 1_000:
            return f"${v / 1_000:.0f}K"
        return f"${v:.0f}"

    return (
        f"*${a.symbol}* — {a.chain.upper()}\n"
        f"📍 `{a.address}`\n"
        f"💰 Giá: ${a.price_usd:.8g} | MCap: {fmt(a.market_cap)} | Liq: {fmt(a.liquidity_usd)}\n"
        f"📊 Vol 24h: {fmt(a.volume_h24)} | 1h: {fmt(a.volume_h1)}\n"
        f"📈 {sign_h1}{a.price_change_h1:.2f}% (1h) | {sign_h24}{a.price_change_h24:.2f}% (24h)"
    )

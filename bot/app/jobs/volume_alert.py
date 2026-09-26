import logging

from telegram.ext import ContextTypes

from app.handlers.alert import get_subscribed_chats
from app.services.volume_scanner import TokenAlert, VolumeScanner

logger = logging.getLogger(__name__)


def _build_combined_report(alerts: list[TokenAlert]) -> str:
    lines = [f"🔥 *Top Volume Tokens* (scan 5 phút) — {len(alerts)} token\n"]
    for i, alert in enumerate(alerts, 1):
        lines.append(f"*{i}.* {_fallback_message(alert)}")
    return "\n".join(lines)


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

    report = _build_combined_report(alerts)

    for chat_id in chats:
        try:
            await context.bot.send_message(chat_id=chat_id, text=report, parse_mode="Markdown")
        except Exception:
            logger.exception("volume_alert.send_failed", extra={"chat_id": chat_id})


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

import logging

from telegram.ext import ContextTypes

from app.handlers.alert import get_subscribed_chats
from app.services.volume_scanner import TokenAlert, VolumeScanner

logger = logging.getLogger(__name__)

_CHAIN_LABELS = {"eth": "ETH", "bsc": "BSC"}


def _fmt_vol(v: float) -> str:
    if v >= 1_000_000:
        return f"${v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v / 1_000:.0f}K"
    return f"${v:.0f}"


def _fmt_pct(v: float) -> str:
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.1f}%"


def _build_message(alerts: list[TokenAlert]) -> str:
    lines = ["🔥 *Top Volume Tokens* (scan 5 phút)\n"]
    for i, a in enumerate(alerts, 1):
        short = a.address[:6] + "..." + a.address[-4:] if len(a.address) > 10 else a.address
        chain = _CHAIN_LABELS.get(a.chain, a.chain.upper())
        lines.append(
            f"*{i}. ${a.symbol}* — {chain}\n"
            f"   📊 Vol 24h: {_fmt_vol(a.volume_h24)} | 1h: {_fmt_vol(a.volume_h1)}\n"
            f"   📈 {_fmt_pct(a.price_change_h1)} (1h) | {_fmt_pct(a.price_change_h24)} (24h)\n"
            f"   🏦 MCap: {_fmt_vol(a.market_cap)} | Liq: {_fmt_vol(a.liquidity_usd)}\n"
            f"   📍 `{short}`\n"
        )
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

    text = _build_message(alerts)
    for chat_id in chats:
        try:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        except Exception:
            logger.exception("volume_alert.send_failed", extra={"chat_id": chat_id})

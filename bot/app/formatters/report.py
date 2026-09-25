from datetime import datetime, timezone

_CHAIN_NAMES = {"eth": "Ethereum Mainnet", "bsc": "BNB Chain"}
_RISK_EMOJI = {"LOW": "✅", "MEDIUM": "🟡", "HIGH": "⚠️", "VERY_HIGH": "🚨"}


def format_number(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:.0f}"


def format_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def format_report(data: dict) -> str:
    token = data["token"]
    market = data["market"]
    security = data["security"]
    social = data["social"]
    analysis = data["analysis"]

    chain_name = _CHAIN_NAMES.get(token.get("chain", ""), token.get("chain", ""))
    dex = token.get("dex") or "Unknown DEX"
    address = token.get("address", "")
    short_addr = address

    risk_level = analysis.get("risk_level", "MEDIUM")
    risk_emoji = _RISK_EMOJI.get(risk_level, "⚠️")

    vol = market.get("volume", {})
    pc = market.get("price_change", {})
    txns = market.get("txns_h24", {})
    liquidity = market.get("liquidity_usd", 0)
    mcap = market.get("market_cap", 0)

    # volume anomaly flag
    vol_h24 = vol.get("h24", 0)
    vol_mcap_flag = ""
    if mcap > 0 and vol_h24 > mcap * 5:
        ratio = round(vol_h24 / mcap, 1)
        vol_mcap_flag = f" (~{ratio}x MCap) 🚨"

    liquidity_flag = " ⚠️ Thấp" if liquidity < 50_000 else ""

    # social
    twitter = social.get("twitter")
    website = social.get("website")
    twitter_str = f"[Twitter]({twitter})" if twitter else "❌"
    website_str = f"[Website]({website})" if website else "❌"

    # security
    honeypot = security.get("is_honeypot")
    honeypot_str = "✅ Không" if honeypot is False else ("🚨 CÓ" if honeypot else "❓")
    buy_tax = security.get("buy_tax")
    sell_tax = security.get("sell_tax")
    tax_str = f"{buy_tax}% / {sell_tax}%" if buy_tax is not None else "❓"
    lp_locked = security.get("lp_locked")
    lp_str = "✅ Có" if lp_locked else ("❌ Chưa" if lp_locked is False else "❓")

    # risk flags
    risk_flags = analysis.get("risk_flags", [])
    positive_flags = analysis.get("positive_flags", [])
    flags_text = "\n".join(f"🚩 {f}" for f in risk_flags) if risk_flags else "_Không phát hiện_"
    pos_text = "\n".join(f"• {f}" for f in positive_flags) if positive_flags else "_Không có_"

    # source + time
    source = data.get("data_source", "unknown")
    fetched_at = data.get("fetched_at", "")
    try:
        dt = datetime.fromisoformat(fetched_at)
        time_str = dt.astimezone(timezone.utc).strftime("%H:%M %d/%m/%Y")
    except (ValueError, TypeError):
        time_str = fetched_at

    lines = [
        f"🔍 *${token['symbol']}* — {chain_name}",
        f"📍 `{short_addr}` | {dex}",
        "",
        "💰 *Thị trường*",
        f"• Giá: ${market.get('price_usd', 0):.8g}",
        f"• MCap: {format_number(mcap)} | FDV: {format_number(market.get('fdv', 0))}",
        f"• Liquidity: {format_number(liquidity)}{liquidity_flag}",
        "",
        "📈 *Biến động giá*",
        f"• 5m: {format_pct(pc.get('m5', 0))} | 1h: {format_pct(pc.get('h1', 0))} | 6h: {format_pct(pc.get('h6', 0))} | 24h: {format_pct(pc.get('h24', 0))}",
        "",
        "📊 *Volume*",
        f"• 24h: {format_number(vol_h24)}{vol_mcap_flag}",
        f"• 6h: {format_number(vol.get('h6', 0))} | 1h: {format_number(vol.get('h1', 0))}",
        "",
        "🔄 *Giao dịch 24h*",
        f"• Mua: {txns.get('buys', 0):,} | Bán: {txns.get('sells', 0):,}",
        "",
        "🔒 *Security*",
        f"• Honeypot: {honeypot_str}",
        f"• Tax mua/bán: {tax_str}",
        f"• LP Locked: {lp_str}",
        "",
        "🌐 *Social*",
        f"• Twitter: {twitter_str} | Website: {website_str}",
        "",
        f"{risk_emoji} *Rủi ro: {risk_level}*",
        flags_text,
        "",
        "✅ *Tín hiệu tốt*",
        pos_text,
        "",
        f"📝 *Nhận định:* {analysis.get('summary', '')}",
        "",
        f"🕐 _Dữ liệu từ: {source} | {time_str}_",
    ]
    return "\n".join(lines)

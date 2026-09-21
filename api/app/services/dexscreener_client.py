import httpx

_BASE_URL = "https://api.dexscreener.com/latest/dex"
_CHAIN_MAP = {
    "ethereum": "eth",
    "bsc": "bsc",
    "eth": "eth",
}
_PREFERRED_CHAINS = {"eth", "bsc"}


def parse_pair(pair: dict) -> dict:
    base = pair.get("baseToken", {})
    info = pair.get("info", {})
    socials = {s["type"]: s["url"] for s in info.get("socials", []) if "type" in s}
    websites = info.get("websites", [])

    volume_raw = pair.get("volume", {})
    price_change_raw = pair.get("priceChange", {})
    txns_h24 = pair.get("txns", {}).get("h24", {})
    liquidity = pair.get("liquidity", {})

    return {
        "token": {
            "address": base.get("address", ""),
            "name": base.get("name", ""),
            "symbol": base.get("symbol", ""),
            "chain": _CHAIN_MAP.get(pair.get("chainId", ""), pair.get("chainId", "")),
            "dex": pair.get("dexId"),
        },
        "market": {
            "price_usd": float(pair.get("priceUsd") or 0),
            "market_cap": float(pair.get("marketCap") or 0),
            "fdv": float(pair.get("fdv") or 0),
            "liquidity_usd": float(liquidity.get("usd") or 0),
            "volume": {
                "m5": float(volume_raw.get("m5") or 0),
                "h1": float(volume_raw.get("h1") or 0),
                "h6": float(volume_raw.get("h6") or 0),
                "h24": float(volume_raw.get("h24") or 0),
            },
            "price_change": {
                "m5": float(price_change_raw.get("m5") or 0),
                "h1": float(price_change_raw.get("h1") or 0),
                "h6": float(price_change_raw.get("h6") or 0),
                "h24": float(price_change_raw.get("h24") or 0),
            },
            "txns_h24": {
                "buys": int(txns_h24.get("buys") or 0),
                "sells": int(txns_h24.get("sells") or 0),
            },
        },
        "social": {
            "twitter": socials.get("twitter"),
            "website": websites[0].get("url") if websites else None,
            "telegram": socials.get("telegram"),
        },
    }


class DexScreenerClient:
    async def fetch_by_address(self, address: str, chain: str | None = None) -> dict | None:
        url = f"{_BASE_URL}/tokens/{address}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
            if response.status_code != 200:
                return None
            pairs = response.json().get("pairs") or []
            if not pairs:
                return None
            if chain:
                target = _CHAIN_MAP.get(chain, chain)
                pairs = [p for p in pairs if _CHAIN_MAP.get(p.get("chainId", ""), "") == target]
                if not pairs:
                    return None
            else:
                # prefer ETH/BSC; only fall back to other chains if none found
                preferred = [p for p in pairs if _CHAIN_MAP.get(p.get("chainId", ""), "") in _PREFERRED_CHAINS]
                if preferred:
                    pairs = preferred

            # pick pair with highest liquidity
            pairs.sort(key=lambda p: float((p.get("liquidity") or {}).get("usd") or 0), reverse=True)
            return parse_pair(pairs[0])
        except (httpx.RequestError, KeyError, ValueError):
            return None

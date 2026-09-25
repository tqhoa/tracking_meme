"""Scans DexScreener for high-volume tokens on ETH/BSC."""
from typing import NamedTuple

import httpx

_BOOST_URL = "https://api.dexscreener.com/token-boosts/top/v1"
_PREFERRED_CHAINS = {"ethereum", "bsc"}
_CHAIN_MAP = {"ethereum": "eth", "bsc": "bsc"}
_MAX_TOKENS = 20
_TOP_RESULTS = 5


class TokenAlert(NamedTuple):
    address: str
    name: str
    symbol: str
    chain: str
    price_usd: float
    volume_h24: float
    volume_h1: float
    price_change_h1: float
    price_change_h24: float
    market_cap: float
    liquidity_usd: float


class VolumeScanner:
    def __init__(
        self,
        min_volume_h24: float = 100_000,
        min_liquidity: float = 10_000,
    ) -> None:
        self._min_volume_h24 = min_volume_h24
        self._min_liquidity = min_liquidity

    async def scan(self) -> list[TokenAlert]:
        boosted = await self._fetch_boosted()
        if not boosted:
            return []

        eth_bsc = [t for t in boosted if t.get("chainId") in _PREFERRED_CHAINS][:_MAX_TOKENS]
        if not eth_bsc:
            return []

        addresses = ",".join(t["tokenAddress"] for t in eth_bsc)
        pairs = await self._fetch_pairs(addresses)
        if not pairs:
            return []

        alerts: list[TokenAlert] = []
        seen: set[str] = set()

        for pair in pairs:
            base = pair.get("baseToken", {})
            addr = base.get("address", "").lower()
            if addr in seen:
                continue
            seen.add(addr)

            chain = _CHAIN_MAP.get(pair.get("chainId", ""), "")
            if chain not in ("eth", "bsc"):
                continue

            vol = pair.get("volume", {})
            liq = pair.get("liquidity", {})
            vol_h24 = float(vol.get("h24") or 0)
            liq_usd = float(liq.get("usd") or 0)

            if vol_h24 < self._min_volume_h24 or liq_usd < self._min_liquidity:
                continue

            pc = pair.get("priceChange", {})
            alerts.append(
                TokenAlert(
                    address=base.get("address", ""),
                    name=base.get("name", ""),
                    symbol=base.get("symbol", ""),
                    chain=chain,
                    price_usd=float(pair.get("priceUsd") or 0),
                    volume_h24=vol_h24,
                    volume_h1=float(vol.get("h1") or 0),
                    price_change_h1=float(pc.get("h1") or 0),
                    price_change_h24=float(pc.get("h24") or 0),
                    market_cap=float(pair.get("marketCap") or 0),
                    liquidity_usd=liq_usd,
                )
            )

        alerts.sort(key=lambda a: a.volume_h24, reverse=True)
        return alerts[:_TOP_RESULTS]

    async def _fetch_boosted(self) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(_BOOST_URL)
            if response.status_code != 200:
                return []
            return response.json() or []
        except httpx.RequestError:
            return []

    async def _fetch_pairs(self, addresses: str) -> list[dict]:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{addresses}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
            if response.status_code != 200:
                return []
            return response.json().get("pairs") or []
        except httpx.RequestError:
            return []

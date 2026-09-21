import asyncio
import time
from datetime import datetime, timezone

import structlog

from app.exceptions import AppError

logger = structlog.get_logger()
from app.services.dexscreener_client import DexScreenerClient
from app.services.gmgn_client import GmgnClient
from app.services.goplus_client import GoplusClient, CHAIN_TO_ID

_CHAINS = ["eth", "bsc"]


class TokenService:
    def __init__(
        self,
        gmgn: GmgnClient,
        dex: DexScreenerClient,
        goplus: GoplusClient,
        analysis: object,
    ) -> None:
        self._gmgn = gmgn
        self._dex = dex
        self._goplus = goplus
        self._analysis = analysis  # type: ignore[assignment]

    async def search(self, address: str, chain: str | None) -> dict:
        t0 = time.monotonic()
        market_data, data_source = await self._resolve_market(address, chain)
        detected_chain = market_data["token"]["chain"]

        logger.info("token.resolved", address=address, chain=detected_chain, source=data_source)

        chain_id = CHAIN_TO_ID.get(detected_chain, "1")
        security_raw, analysis_result = await asyncio.gather(
            self._goplus.fetch_security(address, chain_id),
            self._analysis.generate(market_data["market"], None, market_data["social"]),  # type: ignore[attr-defined]
        )

        from app.schemas.token import SecurityData
        security = SecurityData(**(security_raw if isinstance(security_raw, dict) else {}))

        duration_ms = int((time.monotonic() - t0) * 1000)
        logger.info(
            "token.search.complete",
            address=address,
            source=data_source,
            risk_level=analysis_result.get("risk_level"),
            duration_ms=duration_ms,
        )

        return {
            "token": market_data["token"],
            "market": market_data["market"],
            "security": security.model_dump(),
            "social": market_data["social"],
            "analysis": analysis_result,
            "data_source": data_source,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _resolve_market(self, address: str, chain: str | None) -> tuple[dict, str]:
        chains_to_try = [chain] if chain else _CHAINS

        for c in chains_to_try:
            info = await self._gmgn.fetch_token_info(address, c)
            if info:
                return _gmgn_to_market(info, c), "gmgn"

        dex_data = await self._dex.fetch_by_address(address, chain)
        if dex_data:
            return dex_data, "dexscreener"

        raise AppError("Token not found", 404, "TOKEN_NOT_FOUND")


def _gmgn_to_market(info: dict, chain: str) -> dict:
    return {
        "token": {
            "address": info.get("address", ""),
            "name": info.get("name", ""),
            "symbol": info.get("symbol", ""),
            "chain": chain,
            "dex": None,
        },
        "market": {
            "price_usd": float(info.get("price") or 0),
            "market_cap": float(info.get("market_cap") or 0),
            "fdv": float(info.get("fdv") or 0),
            "liquidity_usd": float(info.get("liquidity") or 0),
            "volume": {"m5": 0, "h1": 0, "h6": 0, "h24": float(info.get("volume_24h") or 0)},
            "price_change": {
                "m5": 0, "h1": float(info.get("price_change_percent1h") or 0),
                "h6": 0, "h24": float(info.get("price_change_percent24h") or 0),
            },
            "txns_h24": {
                "buys": int(info.get("buys_24h") or 0),
                "sells": int(info.get("sells_24h") or 0),
            },
        },
        "social": {
            "twitter": info.get("twitter"),
            "website": info.get("website"),
            "telegram": info.get("telegram"),
        },
    }

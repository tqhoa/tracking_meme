import httpx

_BASE_URL = "https://api.gopluslabs.io/api/v1/token_security"

CHAIN_TO_ID = {
    "eth": "1",
    "bsc": "56",
}


class GoplusClient:
    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key

    async def fetch_security(self, address: str, chain_id: str) -> dict | None:
        params: dict[str, str] = {"contract_addresses": address}
        if self._api_key:
            params["apikey"] = self._api_key

        url = f"{_BASE_URL}/{chain_id}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
            if response.status_code != 200:
                return None
            data = response.json()
            result = (data.get("result") or {}).get(address.lower())
            if not result:
                return None
            return _parse_security(result)
        except (httpx.RequestError, KeyError, ValueError):
            return None


def _parse_security(raw: dict) -> dict:
    return {
        "is_honeypot": _to_bool(raw.get("is_honeypot")),
        "buy_tax": _to_float(raw.get("buy_tax")),
        "sell_tax": _to_float(raw.get("sell_tax")),
        "is_open_source": _to_bool(raw.get("is_open_source")),
        "owner_address": raw.get("owner_address"),
        "creator_address": raw.get("creator_address"),
        "holder_count": _to_int(raw.get("holder_count")),
        "top_10_holders_pct": _to_pct(raw.get("top10_holder_rate")),
        "lp_locked": _to_bool(raw.get("lp_locked")),
    }


def _to_bool(v: object) -> bool | None:
    if v is None:
        return None
    return str(v) == "1"


def _to_float(v: object) -> float | None:
    if v is None:
        return None
    try:
        return float(v)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None


def _to_int(v: object) -> int | None:
    if v is None:
        return None
    try:
        return int(v)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None


def _to_pct(v: object) -> float | None:
    f = _to_float(v)
    return round(f * 100, 2) if f is not None else None

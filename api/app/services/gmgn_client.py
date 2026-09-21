import httpx

_BASE_URL = "https://gmgn.ai/defi/quotation/v1"


class GmgnClient:
    async def fetch_token_info(self, address: str, chain: str) -> dict | None:
        url = f"{_BASE_URL}/tokens/{chain}/{address}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
            if response.status_code != 200:
                return None
            data = response.json()
            if data.get("code", 1) != 0:
                return None
            token = (data.get("data") or {}).get("token")
            return token or None
        except (httpx.RequestError, KeyError, ValueError):
            return None

    async def fetch_token_security(self, address: str, chain: str) -> dict | None:
        url = f"{_BASE_URL}/token_security/{chain}/{address}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
            if response.status_code != 200:
                return None
            data = response.json()
            if data.get("code", 1) != 0:
                return None
            return data.get("data") or None
        except (httpx.RequestError, KeyError, ValueError):
            return None

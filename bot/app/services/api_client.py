import httpx


class ApiClient:
    def __init__(self, base_url: str = "http://api:8000") -> None:
        self._base_url = base_url.rstrip("/")

    async def search_token(self, address: str, chain: str | None = None) -> dict:
        payload: dict[str, object] = {"address": address}
        if chain:
            payload["chain"] = chain
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self._base_url}/api/v1/token/search",
                    json=payload,
                )
            return response.json()
        except httpx.RequestError as exc:
            return {
                "success": False,
                "error": {"code": "NETWORK_ERROR", "message": f"Không thể kết nối tới API: {exc}"},
            }

from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_invalid_address_returns_422() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/token/search", json={"address": "notanaddress"})
    assert response.status_code == 422

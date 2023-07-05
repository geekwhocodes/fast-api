import pytest
from async_asgi_testclient import TestClient
from httpx import Response, _status_codes


@pytest.mark.asyncio
async def test_get_store_by_id(client: TestClient):
    response:Response = await client.get("/v1/stores/")
    assert response.status_code == _status_codes.code.OK
    resp = response.json()
    assert resp.get("status") == "success"
    assert isinstance(resp.get("value"), list)

async def test_create_store(client: TestClient):
    pass

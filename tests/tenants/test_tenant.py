import base64
import uuid

import pytest
from async_asgi_testclient import TestClient
from httpx import Response, _status_codes

from opalizer.api.tenants.schemas import TenantSchema, TenantSchemaIn
from opalizer.config import settings

auth_str = base64.b64encode(f"{settings.admin.username}:{settings.admin.password}".encode("utf-8"))
auth_headers = {"Authorization" : f"Basic {auth_str.decode('utf-8')}"}

@pytest.mark.tenant
@pytest.mark.asyncio
async def test_tenants_get_all(client: TestClient):
    client.headers = auth_headers
    response:Response = await client.get("/v1/tenants/")
    assert response.status_code == _status_codes.code.OK
    resp = response.json()
    assert resp.get("status") == "success"
    assert isinstance(resp.get("value"), list)

@pytest.mark.tenant
@pytest.mark.asyncio
async def test_tenant_create(client: TestClient):
    client.headers = auth_headers
    org_name = str(uuid.uuid4()).replace("-", "_")[:30]
    payload = TenantSchemaIn(name=org_name)
    response:Response = await client.post("/v1/tenants/", data=payload.json())
    assert response.status_code in [_status_codes.code.OK]
    resp = response.json()
    assert resp.get("status") == "success"
    result = TenantSchema(**resp.get("value"))
    assert isinstance(result, TenantSchema)
    assert result.name == org_name

@pytest.mark.tenant
@pytest.mark.asyncio
async def test_tenant_get_by_name(client: TestClient):
    client.headers = auth_headers
    name = "test_tenant__________________01"
    response:Response = await client.get(f"/v1/tenants/{name}")
    assert response.status_code == _status_codes.code.OK
    resp = response.json()
    assert resp.get("status") == "success"

@pytest.mark.tenant
@pytest.mark.asyncio
async def test_tenant_delete_by_name(client: TestClient):
    client.headers = auth_headers
    name = "test_tenant__________________01"
    response:Response = await client.delete(f"/v1/tenants/{name}")
    assert response.status_code == _status_codes.code.OK
    resp = response.json()
    assert resp.get("status") == "success"

from typing import List

from fastapi import APIRouter, Depends, Request, Response
from fastapi import status as HttpStatus
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession

from opalizer.api.tenants import service as ts
from opalizer.api.tenants.schemas import TenantSchema, TenantSchemaIn
from opalizer.core.rate_limiter import limiter
from opalizer.database import get_public_async_db
from opalizer.exceptions import TenantNameNotAvailableError
from opalizer.internal.admin.auth import validate_basic_credentials
from opalizer.schemas import CollectionResponse, RequestStatus, SingleResponse

tenants_router = APIRouter(
    prefix="/v1/tenants",
    dependencies=[Depends(validate_basic_credentials)],
    tags=["Tenants"],
    include_in_schema=False,
)


@tenants_router.get("/{name}", status_code=HttpStatus.HTTP_200_OK)
async def get_tenant(
    request: Request,
    response: Response,
    name: str,
    db: AsyncSession = Depends(get_public_async_db),
):
    try:
        tenant = await ts.get_by_name(session=db, tenant_name=name)
        if tenant:
            return SingleResponse(
                status=RequestStatus.success, value=TenantSchema.from_orm(tenant)
            )
        return SingleResponse(status=RequestStatus.success, value=None)
    except Exception:
        return SingleResponse(
            status=RequestStatus.error, value=None, error="Internal error"
        )


@tenants_router.get("/", status_code=HttpStatus.HTTP_200_OK)
async def get_all_tenants(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_public_async_db),
):
    try:
        tenants = await ts.get_all(db)
        return CollectionResponse(
            status=RequestStatus.success,
            value=parse_obj_as(List[TenantSchema], tenants),
        )
    except Exception:
        return SingleResponse(
            status=RequestStatus.error, value=None, error="Internal error"
        )


@tenants_router.post("/", status_code=HttpStatus.HTTP_200_OK)
@limiter.limit("10/second")
async def create_tenant(
    request: Request,
    response: Response,
    payload: TenantSchemaIn,
    db: AsyncSession = Depends(get_public_async_db),
) -> SingleResponse:
    try:
        tenant = await ts.get_by_name(session=db, tenant_name=payload.name)
        if tenant:
            response.status_code = HttpStatus.HTTP_409_CONFLICT
            return SingleResponse(
                status=RequestStatus.error,
                value=None,
                error=f"Tenant name '{payload.name}' is not available. Please use different tenant name.",
            )

        new_tenant = await ts.create_tenant(session=db, payload=payload)

        return SingleResponse(
            status=RequestStatus.success, value=TenantSchema.from_orm(new_tenant)
        )

    except TenantNameNotAvailableError as e:
        response.status_code = HttpStatus.HTTP_409_CONFLICT
        return SingleResponse(status=RequestStatus.error, value=None, error=str(e))

    except Exception:
        return SingleResponse(
            status=RequestStatus.error, value=None, error="Internal error"
        )


@tenants_router.delete("/{name}", status_code=HttpStatus.HTTP_200_OK)
async def delete_tenant(
    request: Request,
    response: Response,
    name: str,
    db: AsyncSession = Depends(get_public_async_db),
):
    try:
        await ts.delete_tenant(schema=name, cascade=True)
        return SingleResponse(status=RequestStatus.success, value=None)
    except Exception:
        return SingleResponse(
            status=RequestStatus.error, value=None, error="Internal error"
        )

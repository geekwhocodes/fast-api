import uuid
from typing import List

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, Request, Response, Security
from fastapi import status as HttpStatus
from pydantic import parse_obj_as
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import opalizer.api.store.service as ss
from opalizer.api.store.schemas import StoreSchema, StoreSchemaIn
from opalizer.api.tenants.models import Tenant
from opalizer.auth.key import validate_api_key
from opalizer.core.rate_limiter import limiter
from opalizer.database import get_async_db, get_tanant
from opalizer.geolocator.gmaps import gmaps
from opalizer.schemas import CollectionResponse, RequestStatus, SingleResponse

stores_router = APIRouter(
    prefix="/v1/stores",
    dependencies=[Security(validate_api_key)],
    tags=["Stores"],
)


@stores_router.get("/{id}", status_code=HttpStatus.HTTP_200_OK)
@limiter.limit("10/second")
async def get_store(
    request: Request,
    response: Response,
    id: uuid.UUID,
    db: Session = Depends(get_async_db),
):
    try:
        store = await ss.get_by_id(session=db, id=id)
        if store:
            return SingleResponse(
                status=RequestStatus.success, value=StoreSchema.from_orm(store)
            )
        return SingleResponse(status=RequestStatus.success, value=None)
    except Exception:
        return SingleResponse(
            status=RequestStatus.error, value=None, error="Internal error"
        )


@stores_router.get("/", status_code=HttpStatus.HTTP_200_OK)
async def get_all_stores(
    request: Request, response: Response, db: Session = Depends(get_async_db)
):
    try:
        stores = await ss.get_all(db)
        return CollectionResponse(
            status=RequestStatus.success, value=parse_obj_as(List[StoreSchema], stores)
        )
    except Exception:
        return SingleResponse(
            status=RequestStatus.error, value=None, error="Internal error"
        )


@stores_router.post("/", status_code=HttpStatus.HTTP_200_OK)
@limiter.limit("50/second")
async def create_store(
    request: Request,
    response: Response,
    payload: StoreSchemaIn,
    tenant: Tenant = Depends(get_tanant),
    db: Session = Depends(get_async_db),
) -> SingleResponse:
    try:
        store = await ss.get_by_name(session=db, name=payload.name)
        if store:
            response.status_code = HttpStatus.HTTP_409_CONFLICT
            return SingleResponse(
                status=RequestStatus.error,
                value=None,
                error=f"Store name '{payload.name}' is not available. Please use different store name.",
            )

        lat, long = await gmaps.get_geocode(payload)
        new_payload = StoreSchema(
            name=payload.name,
            owner=payload.owner,
            latitude=lat,
            longitude=long,
            radius=payload.radius,
        )
        new_store = await ss.create_store(db, new_payload, tenant)
        return SingleResponse(
            status=RequestStatus.success, value=StoreSchema.from_orm(new_store)
        )
    except IntegrityError as e:
        if e.orig:
            if e.orig.sqlstate == UniqueViolationError.sqlstate:
                return SingleResponse(
                    status=RequestStatus.error,
                    value=None,
                    error="Unique field values are required.",
                )
    except Exception:
        return SingleResponse(
            status=RequestStatus.error, value=None, error="Internal error"
        )


@stores_router.get("/{id}", status_code=HttpStatus.HTTP_200_OK)
@limiter.limit("10/second")
async def delete_store(
    request: Request,
    response: Response,
    id: uuid.UUID,
    db: Session = Depends(get_async_db),
):
    try:
        await ss.delete_store(session=db, id=id)
        return SingleResponse(status=RequestStatus.success, value=None)
    except Exception:
        return SingleResponse(
            status=RequestStatus.error,
            value=None,
            error="Internal error, pleaase try again.",
        )

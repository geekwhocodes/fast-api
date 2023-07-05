import uuid
from typing import List

from asyncpg.exceptions import UniqueViolationError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import opalizer.api.geomap.service as gs
import opalizer.api.store.service as ss
from opalizer.api.events.models import Address, Event
from opalizer.api.events.schemas import EventSchemaIn
from opalizer.api.events.utils import event_in_perimeter, parse_utm_values
from opalizer.api.geomap.models import GeoMap
from opalizer.api.store.models import Store
from opalizer.api.tenants.models import Tenant
from opalizer.database import with_async_db


async def process_event(
    payload: EventSchemaIn,
    tenant: Tenant,
    public_session: AsyncSession,
    private_session: AsyncSession,
):
    """ """
    try:
        stores: List[Store] = await ss.get_all(session=private_session)
        if event_in_perimeter(stores=stores, e=payload):
            new_event = Event(**payload.dict())
            new_event.__dict__.update(
                **parse_utm_values(payload.window_location_json.search)
            )
            address: GeoMap = await gs.get_address(
                latitude=new_event.latitude, longitude=new_event.longitude
            )
            new_event.tenant_id = tenant.id
            await add_or_update_address(tenant, address)
            private_session.add(new_event)
            await private_session.commit()
    except Exception as e:
        print(e)
        # TODo : add to deadletter
        raise


async def add_or_update_address(tenant: Tenant, geomap: GeoMap):
    try:
        if geomap:
            async with with_async_db(tenant_schema_name=tenant.schema) as session:
                new_address = Address()
                new_address.geohash = geomap.geohash
                new_address.geomap_id = geomap.id
                session.add(new_address)
                await session.commit()
    except IntegrityError as e:
        if e.orig:
            if e.orig.sqlstate == UniqueViolationError.sqlstate:
                pass
    except Exception:
        raise


async def process_impression(e: EventSchemaIn, tenant: Tenant):
    if not e.ga_user_id:
        return
    try:
        async with with_async_db(tenant_schema_name=tenant.schema) as session:
            update_query = f"""
                INSERT INTO {tenant.schema}.impressions(id, user_id, count)
                VALUES ('{uuid.uuid4()}', '{e.ga_user_id}', 1)
                ON CONFLICT (user_id)
                DO UPDATE SET count = {tenant.schema}.impressions.count + 1
            """
            await session.execute(text(update_query))
            await session.commit()
    except IntegrityError as e:
        if e.orig:
            if e.orig.sqlstate == UniqueViolationError.sqlstate:
                pass
    except Exception:
        raise

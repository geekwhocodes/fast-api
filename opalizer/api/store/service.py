from typing import List, Union

from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession

from opalizer.api.store.models import Store
from opalizer.api.store.schemas import StoreSchema
from opalizer.api.tenants.models import Tenant


async def get_by_id(session: AsyncSession, id: UUID) -> Union[None, Store]:
    try:
        result = await session.execute(select(Store).where(Store.id == id))
        return result.scalar_one_or_none()
    except Exception:
        raise


async def get_all(session: AsyncSession) -> Union[None, List[Store]]:
    result = await session.execute(select(Store))
    return result.scalars().all()


async def get_by_name(session: AsyncSession, name: str) -> Union[None, Store]:
    try:
        result = await session.execute(select(Store).where(Store.name == name))
        return result.scalar_one_or_none()
    except Exception:
        raise


async def create_store(
    session: AsyncSession, payload: StoreSchema, tenant: Tenant
) -> Store:
    new_store = Store(**payload.dict())
    new_store.tenant_id = tenant.id
    session.add(new_store)
    await session.commit()
    await session.refresh(new_store)
    return new_store


async def delete_store(session: AsyncSession, id: UUID) -> None:
    try:
        store = await get_by_id(session, id)
        if store:
            await session.delete(store)
    except Exception:
        raise

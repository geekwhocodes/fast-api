from typing import Union

import geohash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from opalizer.api.geomap.models import GeoMap
from opalizer.database import with_async_db
from opalizer.geolocator.gmaps import GEO_HASH_PRECISION, gmaps


async def get_address(latitude: float, longitude: float) -> Union[GeoMap, None]:
    async with with_async_db("public") as session:
        address = await _get_address(
            session=session, latitude=latitude, longitude=longitude
        )
        return address


async def _get_address(
    session: AsyncSession, latitude: float, longitude: float
) -> Union[GeoMap, None]:
    try:
        hash = geohash.encode(
            latitude=latitude, longitude=longitude, precision=GEO_HASH_PRECISION
        )
        result = await session.execute(select(GeoMap).where(GeoMap.geohash == hash))
        address = result.scalar_one_or_none()
        if address:
            return address

        address = await gmaps.get_address(latitude, longitude)
        if address:
            geomap = GeoMap()
            geomap.address = address._raw
            geomap.geohash = hash
            geomap.latitude = latitude
            geomap.longitude = longitude
            session.add(geomap)
            await session.commit()
            await session.refresh(geomap)
            return geomap
        return None
    except Exception:
        raise

from typing import Tuple, Union

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import GoogleV3
from geopy.location import Location

from opalizer.api.store.schemas import StoreSchemaIn
from opalizer.config import settings
from opalizer.geolocator.geocoder import GeoLocator

GEO_HASH_PRECISION = 12


class Gmaps(GeoLocator):
    def __init__(self, api_key: str = None) -> None:
        super().__init__()
        if not settings.get("gmaps_key"):
            raise ValueError(
                "Google maps key is required. Please set it by setting this env var `OPALIZER_GMAPS_KEY`"
            )
        self.api_key = settings.gmaps_key
        if api_key:
            self.api_key = api_key

    async def get_address(self, lat: float, long: float) -> Union[Location, None]:
        async with GoogleV3(
            api_key=self.api_key,
            user_agent=f"{settings.app.name}/{settings.app.version}".lower(),
            adapter_factory=AioHTTPAdapter,
        ) as geolocator:
            address = await geolocator.reverse(query=(lat, long), exactly_one=True)
            return address

    async def get_geocode(self, address: StoreSchemaIn) -> Tuple[float, float]:
        try:
            async with GoogleV3(
                api_key=self.api_key,
                user_agent=f"{settings.app.name}/{settings.app.version}".lower(),
                adapter_factory=AioHTTPAdapter,
                timeout=5,
            ) as geolocator:
                address = await geolocator.geocode(query=str(address), exactly_one=True)
                if address:
                    return (address.latitude, address.longitude)
        except Exception:
            raise


gmaps = Gmaps()

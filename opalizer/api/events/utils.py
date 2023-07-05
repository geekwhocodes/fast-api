from typing import Dict, List
from urllib.parse import parse_qs

from geopy.distance import Distance, geodesic

from opalizer.api.events.schemas import EventSchemaIn
from opalizer.api.store.models import Store


def get_utm_keys() -> List[str]:
    return ["utm_medium", "utm_source", "utm_campaign", "utm_term", "utm_content"]


def parse_utm_values(q: str) -> Dict[str, str]:
    """Parse search query and get utm params values"""
    result = {}
    if q.startswith("?"):
        q = q[1:]
    qs = parse_qs(q, encoding="utf-8")
    for utm_key in get_utm_keys():
        if utm_key in qs.keys():
            if isinstance(qs[utm_key], list):
                result[utm_key] = qs[utm_key][0]
        else:
            result[utm_key] = None
    return result


def event_in_perimeter(stores: List[Store], e: EventSchemaIn) -> bool:
    if len(stores) <= 0:
        return False
    for s in stores:
        store_point = (s.latitude, s.longitude)
        radius = Distance(miles=s.radius)
        event_point = (e.latitude, e.longitude)
        if geodesic(store_point, event_point).miles <= radius:
            return True
    return False

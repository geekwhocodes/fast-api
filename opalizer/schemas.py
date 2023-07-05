from datetime import datetime
from enum import Enum
from typing import Any, List, Union
from zoneinfo import ZoneInfo

import orjson
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, root_validator


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class ORJSONModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        json_encoders = {
            datetime: convert_datetime_to_gmt
        }  # method for customer JSON encoding of datetime fields
        orm_mode = True

    # @root_validator(pre=True)
    # def build_additional_properties(cls, values: Dict[str, Any]) -> Dict[str, Any]:
    #     """ Maps extra fields into additionalProperties fields"""
    #     all_required_field_names = {field.alias for field in cls.__fields__.values() if field.alias != 'extra'}  # to support alias

    #     extra: Dict[str, Any] = {}
    #     for field_name in list(values):
    #         if field_name not in all_required_field_names:
    #             extra[field_name] = values.pop(field_name)
    #     values['additional_properties'] = extra
    #     return values

    @root_validator()
    def set_null_microseconds(cls, data: dict) -> dict:
        """Drops microseconds in all the datetime field values."""
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(k, datetime)
        }
        return {**data, **datetime_fields}

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        default_dict = super().dict(**kwargs)

        return jsonable_encoder(default_dict)


class RequestStatus(Enum):
    success = "success"
    error = "error"


class SingleResponse(ORJSONModel):
    status: RequestStatus
    value: Any | None
    error: Union[Any, None]


class CollectionResponse(ORJSONModel):
    status: RequestStatus
    value: List[Any | None]
    error: Union[Any, None]

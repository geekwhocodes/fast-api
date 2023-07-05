import datetime
from typing import Optional, Union

from pydantic import UUID4, Extra, Field

from opalizer.schemas import ORJSONModel


class TenantSchema(ORJSONModel):
    id: UUID4
    name: str = Field(min_length=3)
    api_key: Optional[str]
    created_at: datetime.datetime
    updated_at: Union[datetime.datetime, None]

    class Config:
        extra = Extra.ignore


class TenantSchemaIn(ORJSONModel):
    name: str = Field(min_length=3, max_length=30)

    class Config:
        extra = Extra.forbid

from typing import Optional

from pydantic import UUID4, Extra, Field

from opalizer.schemas import ORJSONModel


class StoreSchemaIn(ORJSONModel):
    id: Optional[UUID4]
    name: str = Field(min_length=3, max_length=200)
    owner: str = Field(default="owner", max_length=64)
    address: str = Field(description="Address")
    apartment: Optional[str] = Field(description="Apartment, suite, etc")
    city: str
    state: str = Field(description="City/Province")
    country: str
    zip_code: str
    radius: float = Field(description="Acceptable radius from the store location.")

    def __str__(self) -> str:
        return " ".join(
            filter(
                None,
                [
                    self.address,
                    self.apartment,
                    self.city,
                    self.state,
                    self.country,
                    self.zip_code,
                ],
            )
        )

    class Config:
        extra = Extra.forbid


class StoreSchema(ORJSONModel):
    id: Optional[UUID4]
    name: str = Field(min_length=3, max_length=200)
    owner: str = Field(default="owner", max_length=64)
    latitude: float = Field(description="Latitude of the store location.")
    longitude: float = Field(description="Longitude of the store location.")
    radius: float = Field(description="Acceptable radius from the store location.")

    class Config:
        extra = Extra.ignore

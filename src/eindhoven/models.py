"""Models for Open Data Platform of Eindhoven."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from mashumaro import field_options
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin


class ParkingType(StrEnum):
    """Enum representing the parking types."""

    PARKING = "Parkeerplaats"
    PERMIT_PARKING = "Parkeerplaats Vergunning"
    DISABLED_PARKING = "Parkeerplaats Gehandicapten"
    CROSSED_OUT_PARKING = "Parkeerplaats Afgekruist"
    LOADING_UNLOADING_PARKING = "Parkeerplaats laden/lossen"
    ELECTRIC_CHARGING_PARKING = "Parkeerplaats Electrisch opladen"


@dataclass(slots=True)
class ParkingData(DataClassORJSONMixin):
    """Typed original parking fields without inventing unknown source values."""

    class Config(BaseConfig):
        """Use the original ODSv2 field names in serialized data."""

        serialize_by_alias = True

    parking_type: str = field(metadata=field_options(alias="type_en_merk"))
    street: str | None = field(metadata=field_options(alias="straat"))
    number: int | float | None = field(metadata=field_options(alias="aantal"))


@dataclass(slots=True)
class Geometry(DataClassORJSONMixin):
    """Typed WGS84 Point with convenient latitude and longitude access."""

    coordinates: list[float]
    type: str = "Point"

    @property
    def latitude(self) -> float:
        """Return the Point latitude."""
        return self.coordinates[1]

    @property
    def longitude(self) -> float:
        """Return the Point longitude."""
        return self.coordinates[0]


@dataclass(slots=True)
class ParkingSpot(DataClassORJSONMixin):
    """Original source record without consumer-specific parking interpretation."""

    spot_id: str
    source_attributes: dict[str, Any]
    geometry: Geometry
    data: ParkingData


@dataclass(slots=True)
class ParkingCollection(DataClassORJSONMixin):
    """Complete selection from one unchanged observed source version."""

    records: list[ParkingSpot]
    total_count: int
    pages_fetched: int
    source_version: str | None
    complete: bool = True

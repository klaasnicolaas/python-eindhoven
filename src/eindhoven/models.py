"""Models for Open Data Platform of Eindhoven."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

from mashumaro import field_options
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin

_ResultDataT = TypeVar("_ResultDataT")


class ParkingType(str, Enum):
    """Enum representing the parking types."""

    PARKING = "Parkeerplaats"
    PERMIT_PARKING = "Parkeerplaats Vergunning"
    DISABLED_PARKING = "Parkeerplaats Gehandicapten"
    CROSSED_OUT_PARKING = "Parkeerplaats Afgekruist"
    LOADING_UNLOADING_PARKING = "Parkeerplaats laden/lossen"
    ELECTRIC_CHARGING_PARKING = "Parkeerplaats Electrisch opladen"


@dataclass
class BaseResponse(DataClassORJSONMixin, Generic[_ResultDataT]):
    """Base response object for the API."""

    # pylint: disable-next=too-few-public-methods
    class Config(BaseConfig):
        """Configuration for mashumaro."""

        serialize_by_alias = True

    hits: int = field(metadata=field_options(alias="nhits"))
    records: _ResultDataT = field(metadata=field_options(alias="records"))


@dataclass(slots=True)
class ParkingSpot(DataClassORJSONMixin):
    """Object representing a parking spot."""

    spot_id: str = field(metadata=field_options(alias="recordid"))
    data: ParkingData = field(metadata=field_options(alias="fields"))
    geometry: Geometry = field(metadata=field_options(alias="geometry"))
    updated_at: datetime = field(
        metadata=field_options(
            alias="record_timestamp",
            deserialize=datetime.fromisoformat,
        )
    )


@dataclass(slots=True)
class ParkingData(DataClassORJSONMixin):
    """Object representing the data fields of a parking spot."""

    parking_type: str = field(metadata=field_options(alias="type_en_merk"))
    street: str = field(metadata=field_options(alias="straat"))
    number: int = field(metadata=field_options(alias="aantal"))


@dataclass(slots=True)
class Geometry(DataClassORJSONMixin):
    """Object representing the geometry of a parking spot."""

    coordinates: list[float] = field(metadata=field_options(alias="coordinates"))

    @property
    def latitude(self) -> float:
        """Return the latitude of the parking spot.

        Returns
        -------
            The latitude of the parking spot.

        """
        return self.coordinates[1]

    @property
    def longitude(self) -> float:
        """Return the longitude of the parking spot.

        Returns
        -------
            The longitude of the parking spot.

        """
        return self.coordinates[0]


@dataclass(slots=True)
class ParkingResponse(BaseResponse[list[ParkingSpot]]):
    """Response object for the parking spots API."""

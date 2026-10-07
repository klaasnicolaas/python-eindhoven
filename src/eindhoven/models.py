"""Models for Open Data Platform of Eindhoven."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ParkingType(StrEnum):
    """Enum representing the parking types."""

    PARKING = "Parkeerplaats"
    PERMIT_PARKING = "Parkeerplaats Vergunning"
    DISABLED_PARKING = "Parkeerplaats Gehandicapten"
    CROSSED_OUT_PARKING = "Parkeerplaats Afgekruist"
    LOADING_UNLOADING_PARKING = "Parkeerplaats laden/lossen"
    ELECTRIC_CHARGING_PARKING = "Parkeerplaats Electrisch opladen"


@dataclass(slots=True)
class ParkingSpot:
    """Original source record without consumer-specific parking interpretation."""

    spot_id: str
    source_attributes: dict[str, Any]
    geometry: dict[str, Any]


@dataclass(slots=True)
class ParkingCollection:
    """Complete selection from one unchanged observed source version."""

    records: list[ParkingSpot]
    total_count: int
    pages_fetched: int
    source_version: str | None
    complete: bool = True

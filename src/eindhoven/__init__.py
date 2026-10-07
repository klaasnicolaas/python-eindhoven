"""Asynchronous Python client providing Open Data information of Eindhoven."""

from .eindhoven import ODPEindhoven
from .exceptions import (
    ODPEindhovenConnectionError,
    ODPEindhovenError,
    ODPEindhovenResultsError,
)
from .models import (
    Geometry,
    ParkingCollection,
    ParkingData,
    ParkingSpot,
    ParkingType,
)

__all__ = [
    "Geometry",
    "ODPEindhoven",
    "ODPEindhovenConnectionError",
    "ODPEindhovenError",
    "ODPEindhovenResultsError",
    "ParkingCollection",
    "ParkingData",
    "ParkingSpot",
    "ParkingType",
]

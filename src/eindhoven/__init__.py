"""Asynchronous Python client providing Open Data information of Eindhoven."""

from .eindhoven import ODPEindhoven
from .exceptions import (
    ODPEindhovenConnectionError,
    ODPEindhovenError,
    ODPEindhovenResultsError,
)
from .models import (
    ParkingCollection,
    ParkingSpot,
    ParkingType,
)

__all__ = [
    "ODPEindhoven",
    "ODPEindhovenConnectionError",
    "ODPEindhovenError",
    "ODPEindhovenResultsError",
    "ParkingCollection",
    "ParkingSpot",
    "ParkingType",
]

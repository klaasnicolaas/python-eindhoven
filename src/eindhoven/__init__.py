"""Asynchronous Python client providing Open Data information of Eindhoven."""

from .eindhoven import ODPEindhoven
from .exceptions import (
    ODPEindhovenConnectionError,
    ODPEindhovenError,
    ODPEindhovenResultsError,
    ODPEindhovenTypeError,
)
from .models import BaseResponse, ParkingSpot, ParkingType

__all__ = [
    "ODPEindhoven",
    "ODPEindhovenConnectionError",
    "ODPEindhovenError",
    "ODPEindhovenResultsError",
    "ODPEindhovenTypeError",
    "BaseResponse",
    "ParkingSpot",
    "ParkingType",
]

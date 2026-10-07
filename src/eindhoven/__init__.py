"""Asynchronous Python client providing Open Data information of Eindhoven."""

from .eindhoven import ODPEindhoven
from .exceptions import (
    ODPEindhovenConnectionError,
    ODPEindhovenError,
    ODPEindhovenResultsError,
)
from .models import (
    BaseResponse,
    ParkingSnapshot,
    ParkingSnapshotRecord,
    ParkingSpot,
    ParkingType,
)

__all__ = [
    "BaseResponse",
    "ODPEindhoven",
    "ODPEindhovenConnectionError",
    "ODPEindhovenError",
    "ODPEindhovenResultsError",
    "ParkingSnapshot",
    "ParkingSnapshotRecord",
    "ParkingSpot",
    "ParkingType",
]

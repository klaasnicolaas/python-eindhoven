"""Models for parking eindhoven."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ParkingSpot:
    """Object representing a parking spot."""

    spot_id: str
    parking_type: str
    street: str
    number: int
    longitude: float
    latitude: float
    updated_at: datetime

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ParkingSpot:
        """Return a ParkingSpot object from a JSON dictionary.

        Args:
            data: The JSON data from the API.

        Returns:
            A ParkingSpot object.
        """

        attr = data["fields"]
        geo = data["geometry"]["coordinates"]
        return cls(
            spot_id=data["recordid"],
            parking_type=attr["type_en_merk"],
            street=attr["straat"],
            number=attr["aantal"],
            longitude=geo[0],
            latitude=geo[1],
            updated_at=data["record_timestamp"],
        )

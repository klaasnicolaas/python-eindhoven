"""Models for Open Data Platform of Eindhoven."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytz


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
    def from_json(cls: type[ParkingSpot], data: dict[str, Any]) -> ParkingSpot:
        """Return a ParkingSpot object from a JSON dictionary.

        Args:
        ----
            data: The JSON data from the API.

        Returns:
        -------
            A ParkingSpot object.
        """
        attr = data["fields"]
        geo = data["geometry"]["coordinates"]
        return cls(
            spot_id=data["recordid"],
            parking_type=attr.get("type_en_merk"),
            street=attr.get("straat"),
            number=attr.get("aantal"),
            longitude=geo[0],
            latitude=geo[1],
            updated_at=datetime.strptime(
                data["record_timestamp"],
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ).replace(tzinfo=pytz.timezone("CET")),
        )

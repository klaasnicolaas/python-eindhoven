"""Asynchronous Python client providing Open Data information of Eindhoven."""

from __future__ import annotations

import asyncio
import math
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

import orjson
from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

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

VERSION: str = metadata.version("eindhoven")


@dataclass
class ODPEindhoven:
    """Main class for handling data fetching from Open Data Platform of Eindhoven."""

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self, path: str = "", *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Read a bounded ODSv2 dataset response within the request deadline."""
        url = URL.build(
            scheme="https",
            host="data.eindhoven.nl",
            path="/api/explore/v2.1/catalog/datasets/parkeerplaatsen" + path,
        )
        if self.session is None:
            self.session = ClientSession()
            self._close_session = True
        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    METH_GET,
                    url,
                    params=params,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": f"PythonEindhoven/{VERSION}",
                    },
                    ssl=True,
                )
                response.raise_for_status()
                body = bytearray()
                async for chunk in response.content.iter_chunked(65536):
                    body.extend(chunk)
                    if len(body) > 2 * 1024 * 1024:
                        msg = "Eindhoven response exceeds the size limit"
                        raise ODPEindhovenResultsError(msg)
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Open Data Platform API."
            raise ODPEindhovenConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with the Open Data Platform API."
            raise ODPEindhovenConnectionError(msg) from exception
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            msg = "Unexpected content type response from the Open Data Platform API."
            raise ODPEindhovenError(msg, {"Content-Type": content_type})
        try:
            result = orjson.loads(body)
        except orjson.JSONDecodeError as exception:
            msg = "Invalid Eindhoven collection JSON"
            raise ODPEindhovenResultsError(msg) from exception
        if not isinstance(result, dict):
            msg = "Expected an Eindhoven response object"
            raise ODPEindhovenResultsError(msg)
        return result

    async def locations(
        self,
        limit: int = 10,
        parking_type: ParkingType = ParkingType.PARKING,
    ) -> list[ParkingSpot]:
        """Return up to limit original ODSv2 records without claiming completeness."""
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 0 < limit <= 9900
        ):
            msg = "limit must be between 1 and 9900"
            raise ValueError(msg)
        records: list[ParkingSpot] = []
        total: int | None = None
        ids: set[str] = set()
        while total is None or len(records) < min(limit, total):
            count, batch = await self._records_page(
                parking_type, len(records), min(100, limit - len(records))
            )
            if total is not None and count != total:
                msg = "Changing Eindhoven source count"
                raise ODPEindhovenResultsError(msg)
            total = count
            for record in batch:
                if record.spot_id in ids:
                    msg = "Eindhoven returned duplicate source IDs"
                    raise ODPEindhovenResultsError(msg)
                ids.add(record.spot_id)
                records.append(record)
        if not records:
            msg = "No parking locations were found"
            raise ODPEindhovenResultsError(msg)
        return records

    async def _records_page(
        self, parking_type: ParkingType, offset: int, limit: int
    ) -> tuple[int, list[ParkingSpot]]:
        """Parse the same ordered ODSv2 record page for both public methods."""
        page = await self._request(
            "/records",
            params={
                "where": f"type_en_merk='{parking_type.value}'",
                "order_by": "objectid asc",
                "limit": limit,
                "offset": offset,
            },
        )
        count = page.get("total_count")
        if isinstance(count, bool) or not isinstance(count, int) or count < offset:
            msg = "Invalid Eindhoven source count"
            raise ODPEindhovenResultsError(msg)
        batch = page.get("results")
        if not isinstance(batch, list) or len(batch) != min(limit, count - offset):
            msg = "Eindhoven returned an incomplete page"
            raise ODPEindhovenResultsError(msg)
        return count, [self._parking_spot(item, parking_type) for item in batch]

    async def dataset_version(self) -> str:
        """Return the portal's opaque data_processed token."""
        metadata_response = await self._request()
        try:
            version = metadata_response["metas"]["default"]["data_processed"]
        except (KeyError, TypeError) as exception:
            msg = "Eindhoven portal version is missing"
            raise ODPEindhovenResultsError(msg) from exception
        if not isinstance(version, str) or not version.strip():
            msg = "Eindhoven portal version is missing"
            raise ODPEindhovenResultsError(msg)
        return version

    async def parking_collection(
        self,
        parking_type: ParkingType = ParkingType.DISABLED_PARKING,
        *,
        max_records: int = 9900,
    ) -> ParkingCollection:
        """Fetch the entire selection or fail without returning partial records."""
        if (
            isinstance(max_records, bool)
            or not isinstance(max_records, int)
            or not 0 < max_records <= 9900
        ):
            msg = "max_records must be between 1 and 9900"
            raise ValueError(msg)
        version = await self.dataset_version()
        records: list[ParkingSpot] = []
        ids: set[str] = set()
        total: int | None = None
        pages = 0
        while total is None or len(records) < total:
            count, batch = await self._records_page(parking_type, len(records), 100)
            if count > max_records or (total is not None and count != total):
                msg = "Invalid or changing Eindhoven source count"
                raise ODPEindhovenResultsError(msg)
            total = count
            for record in batch:
                if record.spot_id in ids:
                    msg = "Eindhoven returned duplicate source IDs"
                    raise ODPEindhovenResultsError(msg)
                ids.add(record.spot_id)
                records.append(record)
            pages += 1
        if await self.dataset_version() != version:
            msg = "Eindhoven dataset changed during collection"
            raise ODPEindhovenResultsError(msg)
        return ParkingCollection(records, total, pages, version)

    @staticmethod
    def _parking_spot(item: Any, parking_type: ParkingType) -> ParkingSpot:
        """Preserve raw fields and the source's WGS84 Point and objectid."""
        if not isinstance(item, dict):
            msg = "Expected an Eindhoven source record object"
            raise ODPEindhovenResultsError(msg)
        object_id = item.get("objectid")
        if (
            isinstance(object_id, bool)
            or not isinstance(object_id, int)
            or object_id <= 0
        ):
            msg = "Invalid Eindhoven objectid"
            raise ODPEindhovenResultsError(msg)
        if item.get("type_en_merk") != parking_type.value:
            msg = "Unexpected Eindhoven parking category"
            raise ODPEindhovenResultsError(msg)
        shape = item.get("geo_shape")
        geometry = shape.get("geometry") if isinstance(shape, dict) else None
        if not isinstance(geometry, dict):
            msg = "Expected an Eindhoven geometry object"
            raise ODPEindhovenResultsError(msg)
        point = geometry.get("coordinates")
        if (
            geometry.get("type") != "Point"
            or not isinstance(point, list)
            or len(point) != 2
        ):
            msg = "Expected an Eindhoven WGS84 Point"
            raise ODPEindhovenResultsError(msg)
        for value, bound in zip(point, (180, 90), strict=True):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not -bound <= value <= bound
            ):
                msg = "Invalid Eindhoven WGS84 coordinate"
                raise ODPEindhovenResultsError(msg)
        return ParkingSpot.from_dict(
            {
                "spot_id": str(object_id),
                "source_attributes": item.copy(),
                "geometry": geometry.copy(),
            }
        )

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Open Data Platform Eindhoven object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()

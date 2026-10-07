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
    ParkingResponse,
    ParkingSnapshot,
    ParkingSnapshotRecord,
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
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
        max_response_bytes: int | None = None,
    ) -> Any:
        """Handle a request to the Open Data Platform API of Eindhoven.

        Args:
        ----
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
        -------
            A Python dictionary (json) with the response from
            the Open Data Platform API of Eindhoven.

        Raises:
        ------
            ODPEindhovenConnectionError: An error occurred while
                communicating with the Open Data Platform API
            ODPEindhovenError: Received an unexpected response from
                the Open Data Platform API.

        """
        url = URL.build(
            scheme="https",
            host="data.eindhoven.nl",
            path="/api/records/1.0/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/json, text/plain",
            "User-Agent": f"PythonEindhoven/{VERSION}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
                if max_response_bytes is not None:
                    body = bytearray()
                    async for chunk in response.content.iter_chunked(65536):
                        body.extend(chunk)
                        if len(body) > max_response_bytes:
                            msg = "Eindhoven response exceeds the size limit"
                            raise ODPEindhovenResultsError(msg)
                    bounded_text = body.decode("utf-8")
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Open Data Platform API."
            raise ODPEindhovenConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with the Open Data Platform API."
            raise ODPEindhovenConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")
        text = bounded_text if max_response_bytes is not None else await response.text()
        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from the Open Data Platform API."
            raise ODPEindhovenError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return text

    async def locations(
        self,
        limit: int = 10,
        parking_type: ParkingType = ParkingType.PARKING,
    ) -> list[ParkingSpot]:
        """Get all the parking locations.

        Args:
        ----
            limit (int): Number of rows to return.
            parking_type (enum): The selected parking type.

        Returns:
        -------
            A list of ParkingSpot objects.

        Raises:
        ------
            ODPEindhovenResultsError: When no results are found.

        """
        response = await self._request(
            "search/",
            params={
                "dataset": "parkeerplaatsen",
                "rows": limit,
                "refine.type_en_merk": parking_type.value,
            },
        )
        results = ParkingResponse.from_json(response).records

        if not results:
            msg = "No parking locations were found"
            raise ODPEindhovenResultsError(msg)
        return results

    async def dataset_version(self) -> str:
        """Return the portal's opaque data_processed token."""
        metadata_response = await self._snapshot_request()
        try:
            version = metadata_response["metas"]["default"]["data_processed"]
        except (KeyError, TypeError) as exception:
            msg = "Eindhoven portal version is missing"
            raise ODPEindhovenResultsError(msg) from exception
        if not isinstance(version, str) or not version.strip():
            msg = "Eindhoven portal version is missing"
            raise ODPEindhovenResultsError(msg)
        return version

    async def _snapshot_request(
        self, path: str = "", params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Read an ODSv2 dataset response through the existing transport."""
        response = await self._request(
            "/api/explore/v2.1/catalog/datasets/parkeerplaatsen" + path,
            params=params,
            max_response_bytes=2 * 1024 * 1024,
        )
        try:
            result = orjson.loads(response)
        except orjson.JSONDecodeError as exception:
            msg = "Invalid Eindhoven snapshot JSON"
            raise ODPEindhovenResultsError(msg) from exception
        if not isinstance(result, dict):
            msg = "Expected an Eindhoven response object"
            raise ODPEindhovenResultsError(msg)
        return result

    async def parking_snapshot(
        self,
        parking_type: ParkingType = ParkingType.DISABLED_PARKING,
        *,
        max_records: int = 9900,
    ) -> ParkingSnapshot:
        """Fetch the entire selection or fail without returning partial records."""
        if (
            isinstance(max_records, bool)
            or not isinstance(max_records, int)
            or not 0 < max_records <= 9900
        ):
            msg = "max_records must be between 1 and 9900"
            raise ValueError(msg)
        version = await self.dataset_version()
        records: list[ParkingSnapshotRecord] = []
        ids: set[str] = set()
        total: int | None = None
        pages = 0
        while total is None or len(records) < total:
            page = await self._snapshot_request(
                "/records",
                {
                    "where": f"type_en_merk='{parking_type.value}'",
                    "order_by": "objectid asc",
                    "limit": 100,
                    "offset": len(records),
                },
            )
            count = page.get("total_count")
            if (
                isinstance(count, bool)
                or not isinstance(count, int)
                or not 0 <= count <= max_records
                or (total is not None and count != total)
            ):
                msg = "Invalid or changing Eindhoven source count"
                raise ODPEindhovenResultsError(msg)
            total = count
            batch = page.get("results")
            if not isinstance(batch, list) or len(batch) != min(
                100, total - len(records)
            ):
                msg = "Eindhoven returned an incomplete page"
                raise ODPEindhovenResultsError(msg)
            for item in batch:
                record = self._snapshot_record(item, parking_type)
                if record.spot_id in ids:
                    msg = "Eindhoven returned duplicate source IDs"
                    raise ODPEindhovenResultsError(msg)
                ids.add(record.spot_id)
                records.append(record)
            pages += 1
        if await self.dataset_version() != version:
            msg = "Eindhoven dataset changed during collection"
            raise ODPEindhovenResultsError(msg)
        return ParkingSnapshot(records, total, pages, version)

    @staticmethod
    def _snapshot_record(item: Any, parking_type: ParkingType) -> ParkingSnapshotRecord:
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
        return ParkingSnapshotRecord(str(object_id), item.copy(), geometry.copy())

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

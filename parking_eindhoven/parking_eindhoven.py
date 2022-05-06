"""Asynchroon Python client for the Parking Eindhoven API."""
from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import metadata
from typing import Any

import async_timeout
from aiohttp.client import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import (
    ParkingEindhovenConnectionError,
    ParkingEindhovenError,
    ParkingEindhovenResultsError,
    ParkingEindhovenTypeError,
)
from .models import ParkingSpot


@dataclass
class ParkingEindhoven:
    """Main class for handling connections with the Parking Eindhoven API."""

    parking_type: int

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False
    _str_parking_type: str = ""

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Handle a request to the Parking Eindhoven API.

        Args:
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
            A Python dictionary (json) with the response from
            the Parking Eindhoven API.

        Raises:
            ParkingEindhovenConnectionError: An error occurred while
                communicating with the Parking Eindhoven API.
            ParkingEindhovenError: Received an unexpected response from
                the Parking Eindhoven API
        """
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https", host="data.eindhoven.nl", path="/api/records/1.0/"
        ).join(URL(uri))

        headers = {
            "Accept": "application/json, text/plain",
            "User-Agent": f"PythonParkingEindhoven/{version}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            raise ParkingEindhovenConnectionError("blabla") from exception
        except (ClientError, ClientResponseError) as exception:
            raise ParkingEindhovenConnectionError("blabla") from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            text = await response.text()
            raise ParkingEindhovenError(
                "Unexpected response from the Parking Eindhoven API",
                {"Content-Type": content_type, "response": text},
            )

        response_data: dict[str, Any] = await response.json(content_type=None)
        return response_data

    async def locations(self, rows: int = 10) -> list[ParkingSpot]:
        """Get all the parking locations.

        Args:
            rows: Number of rows to return.

        Returns:
            A list of ParkingSpot objects.

        Raises:
            ParkingEindhovenError: If the data is not valid.
            ParkingEindhovenResultsError: When no results are found.
        """
        results: list[ParkingSpot] = []
        data = await self._request(
            "search/",
            params={
                "dataset": "parkeerplaatsen",
                "rows": rows,
                "refine.type_en_merk": await self.define_type(),
            },
        )

        for item in data["records"]:
            try:
                results.append(ParkingSpot.from_json(item))
            except KeyError as exception:
                raise ParkingEindhovenError(f"Got wrong data: {item}") from exception
        if not results:
            raise ParkingEindhovenResultsError("No parking locations were found")
        return results

    async def define_type(self) -> str:
        """Define the parking type.

        Returns:
            The parking type as string.

        Raises:
            ParkingEindhovenTypeError: If the parking type is not valid.
        """
        if self.parking_type == 1:
            result_type = "Parkeerplaats"
        elif self.parking_type == 2:
            result_type = "Parkeerplaats Vergunning"
        elif self.parking_type == 3:
            result_type = "Parkeerplaats Gehandicapten"
        elif self.parking_type == 4:
            result_type = "Parkeerplaats Afgekruist"
        elif self.parking_type == 5:
            result_type = "Parkeerplaats laden/lossen"
        elif self.parking_type == 6:
            result_type = "Parkeerplaats Electrisch opladen"
        else:
            raise ParkingEindhovenTypeError(
                "The selected number does not match the list of parking types"
            )
        self._str_parking_type = result_type
        return self._str_parking_type

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> ParkingEindhoven:
        """Async enter.

        Returns:
            The Parking Eindhoven object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
            _exc_info: Exec type.
        """
        await self.close()

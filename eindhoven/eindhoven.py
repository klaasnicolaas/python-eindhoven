"""Asynchronous Python client providing Open Data information of Eindhoven."""
from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any

import aiohttp
import async_timeout
from aiohttp import hdrs
from yarl import URL

from .exceptions import (
    ODPEindhovenConnectionError,
    ODPEindhovenError,
    ODPEindhovenResultsError,
    ODPEindhovenTypeError,
)
from .models import ParkingSpot


@dataclass
class ODPEindhoven:
    """Main class for handling data fetching from Open Data Platform of Eindhoven."""

    request_timeout: float = 10.0
    session: aiohttp.client.ClientSession | None = None

    _close_session: bool = False

    @staticmethod
    async def define_type(parking_type: int) -> str:
        """Define the parking type.

        Args:
            parking_type: The selected parking type number.

        Returns:
            The parking type as string.

        Raises:
            ODPEindhovenTypeError: If the parking type is not listed.
        """
        options = {
            1: "Parkeerplaats",
            2: "Parkeerplaats Vergunning",
            3: "Parkeerplaats Gehandicapten",
            4: "Parkeerplaats Afgekruist",
            5: "Parkeerplaats laden/lossen",
            6: "Parkeerplaats Electrisch opladen",
        }.get(parking_type)

        # Check if the parking type is listed
        if options is None:
            raise ODPEindhovenTypeError(
                "The selected number does not match the list of parking types"
            )
        return options

    async def _request(
        self,
        uri: str,
        *,
        method: str = hdrs.METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Open Data Platform API of Eindhoven.

        Args:
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
            A Python dictionary (json) with the response from
            the Open Data Platform API of Eindhoven.

        Raises:
            ODPEindhovenConnectionError: An error occurred while
                communicating with the Open Data Platform API
            ODPEindhovenError: Received an unexpected response from
                the Open Data Platform API.
        """
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https", host="data.eindhoven.nl", path="/api/records/1.0/"
        ).join(URL(uri))

        headers = {
            "Accept": "application/json, text/plain",
            "User-Agent": f"PythonEindhoven/{version}",
        }

        if self.session is None:
            self.session = aiohttp.ClientSession()
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
            raise ODPEindhovenConnectionError(
                "Timeout occurred while connecting to the Open Data Platform API."
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ODPEindhovenConnectionError(
                "Error occurred while communicating with the Open Data Platform API."
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            text = await response.text()
            raise ODPEindhovenError(
                "Unexpected content type response from the Open Data Platform API",
                {"Content-Type": content_type, "response": text},
            )

        return await response.json()

    async def locations(
        self, limit: int = 10, parking_type: int = 1
    ) -> list[ParkingSpot]:
        """Get all the parking locations.

        Args:
            limit: Number of rows to return.
            parking_type: The selected parking type number.

        Returns:
            A list of ParkingSpot objects.

        Raises:
            ODPEindhovenResultsError: When no results are found.
        """
        results: list[ParkingSpot] = []
        locations = await self._request(
            "search/",
            params={
                "dataset": "parkeerplaatsen",
                "rows": limit,
                "refine.type_en_merk": await self.define_type(parking_type),
            },
        )

        for item in locations["records"]:
            results.append(ParkingSpot.from_json(item))
        if not results:
            raise ODPEindhovenResultsError("No parking locations were found")
        return results

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> ODPEindhoven:
        """Async enter.

        Returns:
            The Open Data Platform Eindhoven object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
            _exc_info: Exec type.
        """
        await self.close()

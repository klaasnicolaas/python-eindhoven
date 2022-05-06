"""Basic tests for the Parking Eindhoven API."""
# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import aiohttp
import pytest
from aresponses import Response, ResponsesMockServer

from parking_eindhoven import ParkingEindhoven
from parking_eindhoven.exceptions import (
    ParkingEindhovenConnectionError,
    ParkingEindhovenError,
)

from . import load_fixtures


@pytest.mark.asyncio
async def test_json_request(aresponses: ResponsesMockServer) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("parking.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(parking_type=2, session=session)
        response = await client._request("test")
        assert response is not None
        await client.close()


@pytest.mark.asyncio
async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("parking.json"),
        ),
    )
    async with ParkingEindhoven(parking_type=3) as client:
        await client._request("test")


@pytest.mark.asyncio
async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from Parking Eindhoven."""
    # Faking a timeout by sleeping
    async def reponse_handler(_: aiohttp.ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!", text=load_fixtures("parking.json")
        )

    aresponses.add("data.eindhoven.nl", "/api/records/1.0/test", "GET", reponse_handler)

    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(parking_type=4, session=session, request_timeout=0.1)
        with pytest.raises(ParkingEindhovenConnectionError):
            assert await client._request("test")


@pytest.mark.asyncio
async def test_content_type(aresponses: ResponsesMockServer) -> None:
    """Test request content type error from P1 Monitor."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "blabla/blabla"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(
            parking_type=1,
            session=session,
        )
        with pytest.raises(ParkingEindhovenError):
            assert await client._request("test")


@pytest.mark.asyncio
async def test_client_error() -> None:
    """Test request client error from Eindhoven API."""
    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(parking_type=1, session=session)
        with patch.object(
            session, "request", side_effect=aiohttp.ClientError
        ), pytest.raises(ParkingEindhovenConnectionError):
            assert await client._request("test")

"""Basic tests for the Open Data Platform API of Eindhoven."""

# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientError, ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from eindhoven import ODPEindhoven
from eindhoven.exceptions import ODPEindhovenConnectionError, ODPEindhovenError

from . import load_fixtures


async def test_json_request(
    aresponses: ResponsesMockServer,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("1_parkings.json"),
        ),
    )
    response = await odp_eindhoven_client._request("test")
    assert response is not None
    await odp_eindhoven_client.close()


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("1_parkings.json"),
        ),
    )
    async with ODPEindhoven() as client:
        await client._request("test")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout is handled correctly."""

    # Faking a timeout by sleeping
    async def reponse_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!",
            text=load_fixtures("parking.json"),
        )

    aresponses.add("data.eindhoven.nl", "/api/records/1.0/test", "GET", reponse_handler)

    async with ClientSession() as session:
        client = ODPEindhoven(session=session, request_timeout=0.1)
        with pytest.raises(ODPEindhovenConnectionError):
            assert await client._request("test")


async def test_content_type(
    aresponses: ResponsesMockServer,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test request content type error is handled correctly."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "blabla/blabla"},
        ),
    )
    with pytest.raises(ODPEindhovenError):
        assert await odp_eindhoven_client._request("test")


async def test_client_error() -> None:
    """Test request client error is handled correctly."""
    async with ClientSession() as session:
        client = ODPEindhoven(session=session)
        with (
            patch.object(
                session,
                "request",
                side_effect=ClientError,
            ),
            pytest.raises(ODPEindhovenConnectionError),
        ):
            assert await client._request("test")

"""Test specific exceptions for models."""

from __future__ import annotations

import pytest
from aresponses import ResponsesMockServer

from eindhoven import (
    ODPEindhoven,
    ODPEindhovenResultsError,
    ODPEindhovenTypeError,
)

from . import load_fixtures


async def test_no_parking_type(
    aresponses: ResponsesMockServer,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test when parking_type doesn't exist."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("zero_results.json"),
        ),
    )
    with pytest.raises(ODPEindhovenTypeError):
        await odp_eindhoven_client.locations(parking_type=7)


async def test_no_parking_results(
    aresponses: ResponsesMockServer,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test if there are no parking results."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("zero_results.json"),
        ),
    )
    with pytest.raises(ODPEindhovenResultsError):
        await odp_eindhoven_client.locations(parking_type=3)

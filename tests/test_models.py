"""Test the models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from . import load_fixtures

if TYPE_CHECKING:
    from eindhoven import ODPEindhoven, ParkingSpot


async def test_parking_model(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the parking model type (1)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("1_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(parking_type=1)
    assert locations == snapshot

    # Test the first location geometry properties
    assert locations[0].geometry.latitude == snapshot
    assert locations[0].geometry.longitude == snapshot


async def test_permit_parking_type(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the permit parking type (2)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("2_permit_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(parking_type=2)
    assert locations == snapshot


async def test_disabled_parking_type(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the disabled parking type (3)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("3_disabled_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(parking_type=3)
    assert locations == snapshot


async def test_crossed_out_parking_type(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the crossed out parking type (4)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("4_crossed_out_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(parking_type=4)
    assert locations == snapshot


async def test_loading_parking_type(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the load in/out parking type (5)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("5_loading_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(parking_type=5)
    assert locations == snapshot


async def test_charging_parking_type(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the electric charging parking type (6)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("6_charging_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(parking_type=6)
    assert locations == snapshot

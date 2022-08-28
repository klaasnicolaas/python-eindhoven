"""Test the models."""
import aiohttp
import pytest
from aresponses import ResponsesMockServer

from parking_eindhoven import (
    ParkingEindhoven,
    ParkingEindhovenResultsError,
    ParkingEindhovenTypeError,
    ParkingSpot,
)

from . import load_fixtures


@pytest.mark.asyncio
async def test_parking_model(aresponses: ResponsesMockServer) -> None:
    """Test the parking model."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("parking.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(session=session)
        locations: list[ParkingSpot] = await client.locations(parking_type=1, limit=1)
        for item in locations:
            assert item.spot_id is not None
            assert item.street is not None
            assert item.updated_at is not None


@pytest.mark.asyncio
async def test_no_parking_type(aresponses: ResponsesMockServer) -> None:
    """Test when parking_type doesn't exist."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("parking.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(session=session)
        with pytest.raises(ParkingEindhovenTypeError):
            locations: list[ParkingSpot] = await client.locations(
                parking_type=7, limit=1
            )
            assert locations == []


@pytest.mark.asyncio
async def test_no_parking_results(aresponses: ResponsesMockServer) -> None:
    """Test if there are no parking results."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("no_parking.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(session=session)
        with pytest.raises(ParkingEindhovenResultsError):
            locations: list[ParkingSpot] = await client.locations(
                parking_type=3, limit=1
            )
            assert locations == []


@pytest.mark.asyncio
async def test_crossed_out_parking_types(aresponses: ResponsesMockServer) -> None:
    """Test the crossed out (4) parking types."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("crossed_out_parking.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(session=session)
        locations: list[ParkingSpot] = await client.locations(parking_type=4, limit=1)
        for item in locations:
            assert item.spot_id == "875f9f4cdd316388bfa20e6710aac2d35add2531"
            assert item.street == "Veldmaarschalk Montgomerylaan"
            assert item.parking_type == "Parkeerplaats Afgekruist"


@pytest.mark.asyncio
async def test_loading_parking_types(aresponses: ResponsesMockServer) -> None:
    """Test the load in/out (5) parking types."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("loading_parking.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(session=session)
        locations: list[ParkingSpot] = await client.locations(parking_type=5, limit=1)
        for item in locations:
            assert item.spot_id == "c2f5fee912ee9da593e8224cd6f3cd8a6390dba1"
            assert item.street == "Stationsweg"
            assert item.parking_type == "Parkeerplaats laden/lossen"


@pytest.mark.asyncio
async def test_car_charging_parking_types(aresponses: ResponsesMockServer) -> None:
    """Test the electric charging (6) parking types."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("charging_parking.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ParkingEindhoven(session=session)
        locations: list[ParkingSpot] = await client.locations(parking_type=6, limit=1)
        for item in locations:
            assert item.spot_id == "9318b1236bce0c404dcf8bcbac22bdc72b3308ef"
            assert item.street == "Professor Dr Dorgelolaan"
            assert item.parking_type == "Parkeerplaats Electrisch opladen"

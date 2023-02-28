"""Test the models."""
from datetime import datetime

import pytest
import pytz
from aiohttp import ClientSession
from aresponses import ResponsesMockServer
from eindhoven import (
    ODPEindhoven,
    ODPEindhovenResultsError,
    ODPEindhovenTypeError,
    ParkingSpot,
)

from . import load_fixtures

cet = pytz.timezone("CET")


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
    async with ClientSession() as session:
        client = ODPEindhoven(session=session)
        locations: list[ParkingSpot] = await client.locations(parking_type=1, limit=1)
        for item in locations:
            assert item.spot_id == "b124abb045f038a12a255e410ccfceb49dba7c77"
            assert item.street == "Marconilaan"
            assert item.parking_type == "Parkeerplaats"
            assert item.updated_at == datetime(
                2022,
                9,
                1,
                21,
                45,
                3,
                599000,
                tzinfo=cet,
            )
            assert item.longitude == 5.457883100818987
            assert item.latitude == 51.450176173744275
            assert isinstance(item.spot_id, str)
            assert isinstance(item.street, str)
            assert isinstance(
                item.parking_type,
                str,
            )
            assert isinstance(item.updated_at, datetime)
            assert isinstance(
                item.longitude,
                float,
            )
            assert isinstance(
                item.latitude,
                float,
            )


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
    async with ClientSession() as session:
        client = ODPEindhoven(session=session)
        with pytest.raises(ODPEindhovenTypeError):
            await client.locations(
                parking_type=7,
                limit=1,
            )


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
    async with ClientSession() as session:
        client = ODPEindhoven(session=session)
        with pytest.raises(ODPEindhovenResultsError):
            await client.locations(
                parking_type=3,
                limit=1,
            )


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
    async with ClientSession() as session:
        client = ODPEindhoven(session=session)
        locations: list[ParkingSpot] = await client.locations(parking_type=4, limit=1)
        for item in locations:
            assert item.spot_id == "875f9f4cdd316388bfa20e6710aac2d35add2531"
            assert item.street == "Veldmaarschalk Montgomerylaan"
            assert item.parking_type == "Parkeerplaats Afgekruist"
            assert item.updated_at == datetime(
                2022,
                9,
                1,
                21,
                45,
                3,
                599000,
                tzinfo=cet,
            )
            assert item.longitude == 5.477020648373145
            assert item.latitude == 51.44925539150587
            assert isinstance(item.spot_id, str)
            assert isinstance(
                item.street,
                str,
            )
            assert isinstance(
                item.parking_type,
                str,
            )
            assert isinstance(item.updated_at, datetime)
            assert isinstance(
                item.longitude,
                float,
            )
            assert isinstance(
                item.latitude,
                float,
            )


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
    async with ClientSession() as session:
        client = ODPEindhoven(session=session)
        locations: list[ParkingSpot] = await client.locations(parking_type=5, limit=1)
        for item in locations:
            assert item.spot_id == "c2f5fee912ee9da593e8224cd6f3cd8a6390dba1"
            assert item.street == "Stationsweg"
            assert item.parking_type == "Parkeerplaats laden/lossen"
            assert item.updated_at == datetime(
                2022,
                9,
                1,
                21,
                45,
                3,
                599000,
                tzinfo=cet,
            )
            assert item.longitude == 5.48124495540772
            assert item.latitude == 51.441680658515224
            assert isinstance(item.spot_id, str)
            assert isinstance(item.street, str)
            assert isinstance(
                item.parking_type,
                str,
            )
            assert isinstance(item.updated_at, datetime)
            assert isinstance(
                item.longitude,
                float,
            )
            assert isinstance(
                item.latitude,
                float,
            )


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
    async with ClientSession() as session:
        client = ODPEindhoven(session=session)
        locations: list[ParkingSpot] = await client.locations(parking_type=6, limit=1)
        for item in locations:
            assert item.spot_id == "9318b1236bce0c404dcf8bcbac22bdc72b3308ef"
            assert item.street == "Professor Dr Dorgelolaan"
            assert item.parking_type == "Parkeerplaats Electrisch opladen"
            assert item.updated_at == datetime(
                2022,
                9,
                1,
                21,
                45,
                3,
                599000,
                tzinfo=cet,
            )
            assert item.longitude == 5.484090179656346
            assert item.latitude == 51.44487067822449
            assert isinstance(item.spot_id, str)
            assert isinstance(
                item.street,
                str,
            )
            assert isinstance(item.parking_type, str)
            assert isinstance(item.updated_at, datetime)
            assert isinstance(
                item.longitude,
                float,
            )
            assert isinstance(
                item.latitude,
                float,
            )

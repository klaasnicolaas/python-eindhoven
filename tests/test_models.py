"""Test the models."""

from __future__ import annotations

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from eindhoven import (
    Geometry,
    ODPEindhoven,
    ParkingCollection,
    ParkingData,
    ParkingSpot,
    ParkingType,
)

from . import load_fixtures


async def test_parking_model(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the parking model type (1)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/explore/v2.1/catalog/datasets/parkeerplaatsen/records",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("1_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(
        parking_type=ParkingType.PARKING
    )
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
        "/api/explore/v2.1/catalog/datasets/parkeerplaatsen/records",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("2_permit_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(
        parking_type=ParkingType.PERMIT_PARKING
    )
    assert locations == snapshot


async def test_disabled_parking_type(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the disabled parking type (3)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/explore/v2.1/catalog/datasets/parkeerplaatsen/records",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("3_disabled_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(
        parking_type=ParkingType.DISABLED_PARKING
    )
    assert locations == snapshot


async def test_crossed_out_parking_type(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the crossed out parking type (4)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/explore/v2.1/catalog/datasets/parkeerplaatsen/records",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("4_crossed_out_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(
        parking_type=ParkingType.CROSSED_OUT_PARKING
    )
    assert locations == snapshot


async def test_loading_parking_type(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the load in/out parking type (5)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/explore/v2.1/catalog/datasets/parkeerplaatsen/records",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("5_loading_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(
        parking_type=ParkingType.LOADING_UNLOADING_PARKING
    )
    assert locations == snapshot


async def test_charging_parking_type(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_eindhoven_client: ODPEindhoven,
) -> None:
    """Test the electric charging parking type (6)."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/explore/v2.1/catalog/datasets/parkeerplaatsen/records",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("6_charging_parkings.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_eindhoven_client.locations(
        parking_type=ParkingType.ELECTRIC_CHARGING_PARKING
    )
    assert locations == snapshot


def test_source_record_mashumaro_round_trip() -> None:
    """Parse validated raw v2 fields and preserve them through typed serialization."""
    source = {
        "objectid": 42,
        "type_en_merk": ParkingType.DISABLED_PARKING.value,
        "straat": None,
        "aantal": None,
        "extra": {"nested": [None, "unchanged", 7]},
        "geo_shape": {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [5.4, 51.4]},
        },
    }
    spot = ODPEindhoven._parking_spot(source, ParkingType.DISABLED_PARKING)
    assert isinstance(spot, ParkingSpot)
    assert spot.spot_id == "42"
    assert spot.source_attributes == source
    assert isinstance(spot.geometry, Geometry)
    assert isinstance(spot.data, ParkingData)
    assert spot.geometry.to_dict() == source["geo_shape"]["geometry"]
    assert spot.data.street is None
    assert spot.data.number is None
    assert spot.data.parking_type == ParkingType.DISABLED_PARKING.value
    assert ParkingSpot.from_json(spot.to_json()) == spot
    assert ParkingSpot.from_dict(spot.to_dict()) == spot
    assert spot.to_dict()["source_attributes"]["straat"] is None


def test_collection_mashumaro_round_trip() -> None:
    """Deserialize nested records as ParkingSpot while retaining the common envelope."""
    payload = {
        "records": [
            {
                "spot_id": "42",
                "source_attributes": {"objectid": 42, "aantal": None},
                "data": {
                    "type_en_merk": ParkingType.DISABLED_PARKING.value,
                    "straat": None,
                    "aantal": None,
                },
                "geometry": {"type": "Point", "coordinates": [5.4, 51.4]},
            }
        ],
        "total_count": 1,
        "pages_fetched": 1,
        "source_version": "opaque-revision",
        "complete": True,
    }
    collection = ParkingCollection.from_dict(payload)
    assert isinstance(collection.records[0], ParkingSpot)
    assert collection.to_dict() == payload
    assert ParkingCollection.from_json(collection.to_json()) == collection


def test_empty_collection_mashumaro_round_trip() -> None:
    """Serialize empty collections and unknown revision tokens without defaults."""
    collection = ParkingCollection([], 0, 1, None)
    assert ParkingCollection.from_json(collection.to_json()) == collection
    assert collection.to_dict()["source_version"] is None
    assert collection.to_dict()["records"] == []


def test_typed_data_preserves_fractional_number_and_geometry_extensions() -> None:
    """Typed views retain fractional claims while raw geometry keeps extra fields."""
    source = {
        "objectid": 7,
        "type_en_merk": ParkingType.DISABLED_PARKING.value,
        "straat": "Example street",
        "aantal": 1.5,
        "geo_shape": {
            "geometry": {"type": "Point", "coordinates": [5.4, 51.4], "extra": "raw"},
        },
    }
    spot = ODPEindhoven._parking_spot(source, ParkingType.DISABLED_PARKING)
    assert spot.data.number == 1.5
    assert spot.data.street == "Example street"
    assert spot.geometry.coordinates == [5.4, 51.4]
    assert spot.geometry.type == "Point"
    assert spot.geometry.latitude == 51.4
    assert spot.geometry.longitude == 5.4
    assert spot.source_attributes["geo_shape"]["geometry"]["extra"] == "raw"
    restored = ParkingSpot.from_json(spot.to_json())
    assert restored.data.number == 1.5
    assert restored.source_attributes == source


def test_typed_data_preserves_zero() -> None:
    """Zero remains a real source value while absent source fields remain unknown."""
    data = ParkingData.from_dict(
        {"type_en_merk": "Parkeerplaats", "straat": None, "aantal": 0}
    )
    assert data.number == 0
    assert data.street is None
    assert ParkingData.from_json(data.to_json()) == data

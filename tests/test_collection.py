"""Complete collection protocol and original source data guarantees."""

from typing import Any
from unittest.mock import AsyncMock, patch

import orjson
import pytest
from aresponses import ResponsesMockServer

from eindhoven import ODPEindhoven, ODPEindhovenResultsError, ParkingType


def record(object_id: int = 1) -> dict[str, Any]:
    """Build a source record with explicit nulls and extra fields."""
    return {
        "objectid": object_id,
        "type_en_merk": ParkingType.DISABLED_PARKING.value,
        "straat": None,
        "aantal": None,
        "extra": "retained",
        "geo_shape": {"geometry": {"type": "Point", "coordinates": [5.4, 51.4]}},
    }


def version(value: Any = "opaque-version") -> dict[str, Any]:
    """Build portal metadata without interpreting the revision token."""
    return {"metas": {"default": {"data_processed": value}}}


async def test_collection_pages() -> None:
    """Fetch every page, preserve source fields, and keep original IDs."""
    first = [record(number) for number in range(1, 101)]
    client = ODPEindhoven()
    request = AsyncMock(
        side_effect=[
            version(),
            {"total_count": 101, "results": first},
            {"total_count": 101, "results": [record(101)]},
            version(),
        ]
    )
    with patch.object(client, "_request", request):
        collection = await client.parking_collection()
    assert collection.complete is True
    assert collection.total_count == len(collection.records) == 101
    assert collection.pages_fetched == 2
    assert collection.source_version == "opaque-version"
    assert collection.records[0].spot_id == "1"
    assert collection.records[0].source_attributes == first[0]
    assert collection.records[0].geometry.to_dict() == first[0]["geo_shape"]["geometry"]
    assert request.call_args_list[2].kwargs["params"]["offset"] == 100
    assert request.call_args_list[1].kwargs["params"]["order_by"] == "objectid asc"


async def test_empty_collection() -> None:
    """A confirmed empty selection succeeds with its actual first page counted."""
    with patch.object(
        ODPEindhoven,
        "_request",
        AsyncMock(
            side_effect=[
                version(),
                {"total_count": 0, "results": []},
                version(),
            ]
        ),
    ):
        collection = await ODPEindhoven().parking_collection()
    assert collection.records == []
    assert collection.total_count == 0
    assert collection.pages_fetched == 1
    assert collection.complete is True


@pytest.mark.parametrize(
    ("count", "batch"),
    [
        (True, []),
        (-1, []),
        (9901, []),
        ("1", []),
        (1, []),
        (0, [record()]),
        (1, {}),
        (2, [record(), record()]),
    ],
)
async def test_invalid_pages(count: Any, batch: Any) -> None:
    """Reject invalid totals, truncated pages and duplicate source IDs."""
    with (
        patch.object(
            ODPEindhoven,
            "_request",
            AsyncMock(
                side_effect=[
                    version(),
                    {"total_count": count, "results": batch},
                ]
            ),
        ),
        pytest.raises(ODPEindhovenResultsError),
    ):
        await ODPEindhoven().parking_collection()


async def test_changing_count() -> None:
    """Reject a total changing between full pages."""
    with (
        patch.object(
            ODPEindhoven,
            "_request",
            AsyncMock(
                side_effect=[
                    version(),
                    {"total_count": 101, "results": [record(i) for i in range(1, 101)]},
                    {"total_count": 102, "results": [record(101), record(102)]},
                ]
            ),
        ),
        pytest.raises(ODPEindhovenResultsError, match="count"),
    ):
        await ODPEindhoven().parking_collection()


async def test_changing_version() -> None:
    """Reject a metadata token changing during the traversal."""
    with (
        patch.object(
            ODPEindhoven,
            "_request",
            AsyncMock(
                side_effect=[
                    version(),
                    {"total_count": 1, "results": [record()]},
                    version("changed"),
                ]
            ),
        ),
        pytest.raises(ODPEindhovenResultsError, match="changed"),
    ):
        await ODPEindhoven().parking_collection()


@pytest.mark.parametrize("metadata_response", [{}, version(None), version(" ")])
async def test_missing_version(metadata_response: dict[str, Any]) -> None:
    """Require meaningful portal revision metadata for Eindhoven."""
    with (
        patch.object(
            ODPEindhoven,
            "_request",
            AsyncMock(return_value=metadata_response),
        ),
        pytest.raises(ODPEindhovenResultsError, match="version"),
    ):
        await ODPEindhoven().parking_collection()


@pytest.mark.parametrize("maximum", [0, 9901, True, "100"])
async def test_invalid_bound(maximum: Any) -> None:
    """Reject invalid safety bounds before contacting the provider."""
    with pytest.raises(ValueError, match="max_records"):
        await ODPEindhoven().parking_collection(max_records=maximum)


@pytest.mark.parametrize(
    "item",
    [
        None,
        {**record(), "straat": 42},
        {**record(), "aantal": True},
        {**record(), "aantal": "1"},
        {**record(), "aantal": float("nan")},
        {},
        {**record(), "objectid": True},
        {**record(), "objectid": "1"},
        {**record(), "objectid": 0},
        {**record(), "type_en_merk": "other"},
        {**record(), "geo_shape": None},
        {**record(), "geo_shape": {"geometry": []}},
        {
            **record(),
            "geo_shape": {"geometry": {"type": "LineString", "coordinates": [5, 51]}},
        },
        {**record(), "geo_shape": {"geometry": {"type": "Point", "coordinates": [5]}}},
        {
            **record(),
            "geo_shape": {"geometry": {"type": "Point", "coordinates": [True, 51]}},
        },
        {
            **record(),
            "geo_shape": {"geometry": {"type": "Point", "coordinates": [181, 51]}},
        },
        {
            **record(),
            "geo_shape": {
                "geometry": {"type": "Point", "coordinates": [float("nan"), 51]}
            },
        },
    ],
)
async def test_invalid_records(item: Any) -> None:
    """Reject unusable IDs, category mismatches and non-WGS84 Points."""
    with (
        patch.object(
            ODPEindhoven,
            "_request",
            AsyncMock(
                side_effect=[
                    version(),
                    {"total_count": 1, "results": [item]},
                ]
            ),
        ),
        pytest.raises(ODPEindhovenResultsError),
    ):
        await ODPEindhoven().parking_collection()


@pytest.mark.parametrize("body", ["invalid json", "[]"])
async def test_invalid_collection_json(
    aresponses: ResponsesMockServer, body: str
) -> None:
    """Reject invalid JSON response shapes through the common transport."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/explore/v2.1/catalog/datasets/parkeerplaatsen",
        "GET",
        aresponses.Response(
            status=200, headers={"Content-Type": "application/json"}, text=body
        ),
    )
    async with ODPEindhoven() as client:
        with pytest.raises(ODPEindhovenResultsError):
            await client.parking_collection()


async def test_bounded_response(aresponses: ResponsesMockServer) -> None:
    """Reject overlarge collection bodies before parsing them."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/explore/v2.1/catalog/datasets/parkeerplaatsen",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text="x" * (2 * 1024 * 1024 + 1),
        ),
    )
    async with ODPEindhoven() as client:
        with pytest.raises(ODPEindhovenResultsError, match="size limit"):
            await client.parking_collection()


async def test_bounded_json_response(aresponses: ResponsesMockServer) -> None:
    """Read a bounded metadata response through the public transport."""
    aresponses.add(
        "data.eindhoven.nl",
        "/api/explore/v2.1/catalog/datasets/parkeerplaatsen",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=orjson.dumps(version()).decode(),
        ),
    )
    async with ODPEindhoven() as client:
        assert await client.dataset_version() == "opaque-version"


@pytest.mark.parametrize("limit", [True, 0, 9901, "10"])
async def test_locations_invalid_limit(limit: Any) -> None:
    """Reject invalid requested prefix sizes before contacting the source."""
    with pytest.raises(ValueError, match="limit"):
        await ODPEindhoven().locations(limit=limit)


async def test_locations_prefix() -> None:
    """Fetch only the requested prefix with the shared parser and retain nulls."""
    request = AsyncMock(
        side_effect=[
            {"total_count": 500, "results": [record(i) for i in range(1, 101)]},
            {"total_count": 500, "results": [record(101)]},
        ]
    )
    with patch.object(ODPEindhoven, "_request", request):
        spots = await ODPEindhoven().locations(
            limit=101, parking_type=ParkingType.DISABLED_PARKING
        )
    assert len(spots) == 101
    assert spots[0].spot_id == "1"
    assert spots[0].source_attributes["straat"] is None
    assert spots[0].source_attributes["aantal"] is None
    assert spots[0].source_attributes["extra"] == "retained"
    assert request.call_count == 2
    assert request.call_args_list[1].kwargs["params"]["limit"] == 1
    assert request.call_args_list[1].kwargs["params"]["offset"] == 100
    assert all(call.args[0] == "/records" for call in request.call_args_list)


@pytest.mark.parametrize(("count", "last_id"), [(102, 101), (101, 1)])
async def test_locations_changing_or_duplicate(count: int, last_id: int) -> None:
    """Limited reads still reject changing totals and duplicate original IDs."""
    with (
        patch.object(
            ODPEindhoven,
            "_request",
            AsyncMock(
                side_effect=[
                    {"total_count": 101, "results": [record(i) for i in range(1, 101)]},
                    {"total_count": count, "results": [record(last_id)]},
                ]
            ),
        ),
        pytest.raises(ODPEindhovenResultsError),
    ):
        await ODPEindhoven().locations(
            limit=101, parking_type=ParkingType.DISABLED_PARKING
        )

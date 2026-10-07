"""Complete snapshot protocol and original source data guarantees."""

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


async def test_snapshot_pages() -> None:
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
    with patch.object(client, "_snapshot_request", request):
        snapshot = await client.parking_snapshot()
    assert snapshot.complete is True
    assert snapshot.total_count == len(snapshot.records) == 101
    assert snapshot.pages_fetched == 2
    assert snapshot.source_version == "opaque-version"
    assert snapshot.records[0].spot_id == "1"
    assert snapshot.records[0].source_attributes == first[0]
    assert snapshot.records[0].geometry == first[0]["geo_shape"]["geometry"]
    assert request.call_args_list[2].args[1]["offset"] == 100
    assert request.call_args_list[1].args[1]["order_by"] == "objectid asc"


async def test_empty_snapshot() -> None:
    """A confirmed empty selection succeeds with its actual first page counted."""
    with patch.object(
        ODPEindhoven,
        "_snapshot_request",
        AsyncMock(
            side_effect=[
                version(),
                {"total_count": 0, "results": []},
                version(),
            ]
        ),
    ):
        snapshot = await ODPEindhoven().parking_snapshot()
    assert snapshot.records == []
    assert snapshot.total_count == 0
    assert snapshot.pages_fetched == 1
    assert snapshot.complete is True


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
            "_snapshot_request",
            AsyncMock(
                side_effect=[
                    version(),
                    {"total_count": count, "results": batch},
                ]
            ),
        ),
        pytest.raises(ODPEindhovenResultsError),
    ):
        await ODPEindhoven().parking_snapshot()


async def test_changing_count() -> None:
    """Reject a total changing between full pages."""
    with (
        patch.object(
            ODPEindhoven,
            "_snapshot_request",
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
        await ODPEindhoven().parking_snapshot()


async def test_changing_version() -> None:
    """Reject a metadata token changing during the traversal."""
    with (
        patch.object(
            ODPEindhoven,
            "_snapshot_request",
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
        await ODPEindhoven().parking_snapshot()


@pytest.mark.parametrize("metadata_response", [{}, version(None), version(" ")])
async def test_missing_version(metadata_response: dict[str, Any]) -> None:
    """Require meaningful portal revision metadata for Eindhoven."""
    with (
        patch.object(
            ODPEindhoven, "_snapshot_request", AsyncMock(return_value=metadata_response)
        ),
        pytest.raises(ODPEindhovenResultsError, match="version"),
    ):
        await ODPEindhoven().parking_snapshot()


@pytest.mark.parametrize("maximum", [0, 9901, True, "100"])
async def test_invalid_bound(maximum: Any) -> None:
    """Reject invalid safety bounds before contacting the provider."""
    with pytest.raises(ValueError, match="max_records"):
        await ODPEindhoven().parking_snapshot(max_records=maximum)


@pytest.mark.parametrize(
    "item",
    [
        None,
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
            "_snapshot_request",
            AsyncMock(
                side_effect=[
                    version(),
                    {"total_count": 1, "results": [item]},
                ]
            ),
        ),
        pytest.raises(ODPEindhovenResultsError),
    ):
        await ODPEindhoven().parking_snapshot()


@pytest.mark.parametrize("body", ["invalid json", "[]"])
async def test_invalid_snapshot_json(body: str) -> None:
    """Reject invalid JSON response shapes through the snapshot transport."""
    with (
        patch.object(ODPEindhoven, "_request", AsyncMock(return_value=body)),
        pytest.raises(ODPEindhovenResultsError),
    ):
        await ODPEindhoven().parking_snapshot()


async def test_snapshot_endpoint() -> None:
    """Use ODSv2 without changing the existing ODSv1 locations API."""
    request = AsyncMock(return_value=orjson.dumps({"total_count": 0, "results": []}))
    with patch.object(ODPEindhoven, "_request", request):
        result = await ODPEindhoven()._snapshot_request("/records", {"limit": 100})
    assert result["total_count"] == 0
    assert (
        request.call_args.args[0]
        == "/api/explore/v2.1/catalog/datasets/parkeerplaatsen/records"
    )


async def test_bounded_response(aresponses: ResponsesMockServer) -> None:
    """Reject overlarge snapshot bodies before parsing them."""
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
            await client.parking_snapshot()


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

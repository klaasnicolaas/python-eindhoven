# Complete collection contract

[Back to the README](../README.md)

Use `await client.parking_collection(parking_type=ParkingType.DISABLED_PARKING, max_records=9900)` for a complete selection. `locations(limit=..., parking_type=...)` is a limited convenience API using the same endpoint and record parser. It only fetches the requested prefix and does not assert a full, version-checked collection.

All parking collection clients share this envelope:

| Field | Meaning |
| :---- | :------ |
| `records` | Source-specific records, retaining original source IDs and raw fields |
| `total_count` | Source-declared count for the selected category; equals `len(records)` |
| `pages_fetched` | Actual record pages requested, including an empty first page |
| `source_version` | Opaque source revision token, or `None` where unavailable; never a record modification date |
| `complete` | Always `True` on success; failures raise an exception rather than returning a partial collection |

Eindhoven returns `ParkingSpot` with `id` (original positive integer `objectid` rendered as a decimal string), `source_attributes` (all original ODSv2 fields, including null values), `data` (typed original parking fields), and `geometry` (typed WGS84 Point). The exact original geometry, including additional source fields, remains in `source_attributes["geo_shape"]["geometry"]`. Consumer-specific mapping, access decisions, and publication remain outside this package.

The client requests pages of 100 ordered by `objectid`, validates totals, page lengths and unique IDs, and compares the portal's `data_processed` token before and after collection. Empty selections return a complete empty collection. The default safety bound is 9900 records and may be lowered; exceeding it raises `ODPEindhovenResultsError`. The revision comparison is an observation of portal metadata, not a transaction guarantee by the provider.

## Migration to ODSv2.1

This release changes the source endpoint and `ParkingSpot` shape. All requests now use `/api/explore/v2.1/catalog/datasets/parkeerplaatsen`; the ODSv1 path and response models are removed.

- Replace hashed ODSv1 `recordid` identities with the original `objectid` exposed as `id`. Do not treat these different IDs as equivalent.
- `spot.data.parking_type`, `.street` and `.number` remain available through typed `ParkingData`. Street and number can be `None`; a fractional source number is retained as a float without rounding. All raw fields are additionally preserved in `spot.source_attributes`.
- `spot.geometry.latitude`, `.longitude` and `.coordinates` remain available through typed `Geometry`; its `type` is `Point`. Exact additional geometry fields remain in the raw `source_attributes`.
- `updated_at`, `BaseResponse` and `ParkingResponse` are removed. ODSv2 does not provide the old per-record portal timestamp; `source_version` is an observed dataset revision token and must not be substituted for a record modification date.
- `locations()` retains its limited-list behavior and no-results exception. For a confirmed empty or complete selection, use `parking_collection()`.

## Model serialization

Both `locations()` and `parking_collection()` return the same `ParkingSpot` model from the ODSv2.1 endpoint. The client validates source IDs, categories and coordinates before mapping the source row through Mashumaro `ParkingSpot.from_dict()`. `ParkingSpot` and `ParkingCollection` support typed `from_dict()` / `from_json()` and `to_dict()` / `to_json()` round trips, including nested records and explicit null values.

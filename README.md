<!-- Banner -->
![alt Banner of the eindhoven package](https://raw.githubusercontent.com/klaasnicolaas/python-eindhoven/main/assets/header_eindhoven-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]
[![Code Coverage][codecov-shield]][codecov-url]
[![OpenSSF Scorecard][scorecard-shield]][scorecard-url]

Asynchronous Python client for the open datasets of Eindhoven (The Netherlands).

## About

A python package with which you can retrieve data from the Open Data Platform of Eindhoven via [their API][api]. This package was initially created to only retrieve parking data from the API, but the code base is made in such a way that it is easy to extend for other datasets from the same platform.

## Installation

```bash
pip install eindhoven
```

## Datasets

You can read the following datasets with this package:

- [Parking spots / Parkeerplaatsen][parking]

<details>
    <summary>Click here to get more details</summary>

### Parkings spots

You can use the following parameters in your request:

- **limit** (default: 10) - How many results you want to retrieve.
- **parking_type** (default: ParkingType.PARKING) - See the list below to find the corresponding enum value.

| `ParkingType`                    | Enum                      |
| :------------------------------- | :------------------------ |
| Parkeerplaats                    | PARKING                   |
| Parkeerplaats Vergunning         | PERMIT_PARKING            |
| Parkeerplaats Gehandicapten      | DISABLED_PARKING          |
| Parkeerplaats Afgekruist         | CROSSED_OUT_PARKING       |
| Parkeerplaats laden/lossen       | LOADING_UNLOADING_PARKING |
| Parkeerplaats Electrisch opladen | ELECTRIC_CHARGING_PARKING |

Both `locations()` and `parking_collection()` return the same `ParkingSpot` model from the ODSv2.1 endpoint. The client validates source IDs, categories and coordinates before mapping the source row through Mashumaro `ParkingSpot.from_dict()`. `ParkingSpot` and `ParkingCollection` support typed `from_dict()` / `from_json()` and `to_dict()` / `to_json()` round trips, including nested records and explicit null values.

| Attribute | Type | Description |
| :-------- | :--- | :---------- |
| `spot_id` | string | Original positive integer `objectid` as a decimal string |
| `source_attributes` | dict | All original ODSv2 fields, including null values |
| `data` | ParkingData | Typed `parking_type`, nullable `street` and nullable `number` (integer or float) |
| `geometry` | Geometry | Typed WGS84 Point with `type`, `coordinates`, `latitude` and `longitude` |

</details>

### Example

```python
import asyncio

from eindhoven import ODPEindhoven, ParkingType


async def main() -> None:
    """Show example on using the Open Data Platform API of Eindhoven."""
    async with ODPEindhoven() as client:
        locations = await client.locations(
            limit=100,
            parking_type=ParkingType.PARKING,
        )
        print(locations)


if __name__ == "__main__":
    asyncio.run(main())
```

## Complete collection contract

Use `await client.parking_collection(parking_type=ParkingType.DISABLED_PARKING, max_records=9900)` for a complete selection. `locations(limit=..., parking_type=...)` is a limited convenience API using the same endpoint and record parser. It only fetches the requested prefix and does not assert a full, version-checked collection.

All parking collection clients share this envelope:

| Field | Meaning |
| :---- | :------ |
| `records` | Source-specific records, retaining original source IDs and raw fields |
| `total_count` | Source-declared count for the selected category; equals `len(records)` |
| `pages_fetched` | Actual record pages requested, including an empty first page |
| `source_version` | Opaque source revision token, or `None` where unavailable; never a record modification date |
| `complete` | Always `True` on success; failures raise an exception rather than returning a partial collection |

Eindhoven returns `ParkingSpot` with `spot_id` (original positive integer `objectid` rendered as a decimal string), `source_attributes` (all original ODSv2 fields, including null values), `data` (typed original parking fields), and `geometry` (typed WGS84 Point). The exact original geometry, including additional source fields, remains in `source_attributes["geo_shape"]["geometry"]`. Consumer-specific mapping, access decisions, and publication remain outside this package.

The client requests pages of 100 ordered by `objectid`, validates totals, page lengths and unique IDs, and compares the portal's `data_processed` token before and after collection. Empty selections return a complete empty collection. The default safety bound is 9900 records and may be lowered; exceeding it raises `ODPEindhovenResultsError`. The revision comparison is an observation of portal metadata, not a transaction guarantee by the provider.

## Migration to ODSv2.1

This release changes the source endpoint and `ParkingSpot` shape. All requests now use `/api/explore/v2.1/catalog/datasets/parkeerplaatsen`; the ODSv1 path and response models are removed.

- Replace hashed ODSv1 `recordid` identities with the original `objectid` exposed as `spot_id`. Do not treat these different IDs as equivalent.
- `spot.data.parking_type`, `.street` and `.number` remain available through typed `ParkingData`. Street and number can be `None`; a fractional source number is retained as a float without rounding. All raw fields are additionally preserved in `spot.source_attributes`.
- `spot.geometry.latitude`, `.longitude` and `.coordinates` remain available through typed `Geometry`; its `type` is `Point`. Exact additional geometry fields remain in the raw `source_attributes`.
- `updated_at`, `BaseResponse` and `ParkingResponse` are removed. ODSv2 does not provide the old per-record portal timestamp; `source_version` is an observed dataset revision token and must not be substituted for a record modification date.
- `locations()` retains its limited-list behavior and no-results exception. For a confirmed empty or complete selection, use `parking_collection()`.

## Use cases

[NIPKaart.nl][nipkaart]

A website that provides insight into where disabled parking spaces are, based on data from users and municipalities. Operates mainly in the Netherlands, but also has plans to process data from abroad.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [uv][uv] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.12+
- [uv][uv-install]

### Installation

Install all packages, including all development requirements:

```bash
uv sync --locked
```

_uv creates a project virtual environment in `.venv` and installs the locked dependencies._

### Prek

This repository uses the [prek][prek] framework, all changes
are linted and tested with each commit. To setup the prek check, run:

```bash
uv run prek install
```

And to run all checks and tests manually, use the following command:

```bash
uv run prek run --all-files
```

### Testing

It uses [pytest](https://docs.pytest.org/en/stable/) as the test framework. To run the tests:

```bash
uv run pytest
```

To update the [syrupy](https://github.com/tophat/syrupy) snapshot tests:

```bash
uv run pytest --snapshot-update
```

## License

MIT License

Copyright (c) 2021-2026 Klaas Schoute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[api]: https://data.eindhoven.nl
[parking]: https://data.eindhoven.nl/explore/dataset/parkeerplaatsen/information
[nipkaart]: https://www.nipkaart.nl

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/tests.yaml
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-eindhoven.svg
[commits-url]: https://github.com/klaasnicolaas/python-eindhoven/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-eindhoven/branch/main/graph/badge.svg?token=4AMI23ZT7C
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-eindhoven
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/klaasnicolaas/python-eindhoven
[downloads-shield]: https://img.shields.io/pypi/dm/eindhoven
[downloads-url]: https://pypistats.org/packages/eindhoven
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-eindhoven.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-eindhoven.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2026.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[pypi]: https://pypi.org/project/eindhoven/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/eindhoven
[typing-shield]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-eindhoven.svg
[releases]: https://github.com/klaasnicolaas/python-eindhoven/releases

[uv-install]: https://docs.astral.sh/uv/getting-started/installation/
[uv]: https://docs.astral.sh/uv/
[prek]: https://github.com/j178/prek
[scorecard-shield]: https://api.scorecard.dev/projects/github.com/klaasnicolaas/python-eindhoven/badge
[scorecard-url]: https://scorecard.dev/viewer/?uri=github.com/klaasnicolaas/python-eindhoven

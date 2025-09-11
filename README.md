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

You get the following output data back with this dataset:

| Attribute    | Type        | Description                                       |
| :----------- | :---------- | :------------------------------------------------ |
| `spot_id`    | string      | The id of the parking spot                        |
| `data`       | ParkingData | The parking data of the parking spot              |
| `geometry`   | Geometry    | The geometry of the parking spot                  |
| `updated_at` | datetime    | When this parking spot was updated in the dataset |

#### ParkingData

The parking data of the parking spot.

| Attribute      | Type     | Description                                        |
| :------------- | :------- | :------------------------------------------------- |
| `parking_type` | string   | The type of parking of the parking spot            |
| `street`       | string   | The street name where this parking spot is located |
| `number`       | int      | The number of parkings spots on this location      |

#### Geometry

The geometry of the parking spot is a GeoJSON object. The coordinates are in the WGS84 coordinate system.

| Attribute     | Type  | Description                         |
| :------------ | :---- | :---------------------------------- |
| `coordinates` | list  | The coordinates of the parking spot |
| `longitude`   | float | The longitude of the parking spot   |
| `latitude`    | float | The latitude of the parking spot    |
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

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.11+
- [Poetry][poetry-install]

### Installation

Install all packages, including all development requirements:

```bash
poetry install
```

_Poetry creates by default an virtual environment where it installs all
necessary pip packages_.

### Pre-commit

This repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. To setup the pre-commit check, run:

```bash
poetry run pre-commit install
```

And to run all checks and tests manually, use the following command:

```bash
poetry run pre-commit run --all-files
```

### Testing

It uses [pytest](https://docs.pytest.org/en/stable/) as the test framework. To run the tests:

```bash
poetry run pytest
```

To update the [syrupy](https://github.com/tophat/syrupy) snapshot tests:

```bash
poetry run pytest --snapshot-update
```

## License

MIT License

Copyright (c) 2021-2025 Klaas Schoute

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
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[pypi]: https://pypi.org/project/eindhoven/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/eindhoven
[typing-shield]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-eindhoven.svg
[releases]: https://github.com/klaasnicolaas/python-eindhoven/releases

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com

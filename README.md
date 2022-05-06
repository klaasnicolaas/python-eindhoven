## Python - Parking Eindhoven Client

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]

[![Code Quality][code-quality-shield]][code-quality]
[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]

Asynchronous Python client for the parking locations in Eindhoven (The Netherlands).

## About

A python package with which you can retrieve the parking locations from the municipality of Eindhoven via [their API][api].

## Installation

```bash
pip install parking-eindhoven
```

## Usage

There are a number of variables you can set to retrieve the data:

- **parking_type** - See the list below to find the corresponding number.
    | **parking_type** | **number** |
    | --- | --- |
    | Parkeerplaats | 1 |
    | Parkeerplaats Vergunning | 2 |
    | Parkeerplaats Gehandicapten | 3 |
    | Parkeerplaats Afgekruist | 4 |
    | Parkeerplaats laden/lossen | 5 |
    | Parkeerplaats Electrisch opladen | 6 |
- **rows** (default: 10) - How many results you want to retrieve.

### Example

```python
import asyncio

from parking_eindhoven import ParkingEindhoven


async def main() -> None:
    """Show example on using the Parking Eindhoven API client."""
    async with ParkingEindhoven(parking_type=4) as client:
        locations = await client.locations(rows=100)
        print(locations)


if __name__ == "__main__":
    asyncio.run(main())
```

## Data

You can read the following data with this package:

- ID of the parking spot
- Parking type (what you have chosen above)
- Street
- Number (how many parking spots are available at the spot)
- Longitude
- Latitude
- Updated at (date when there was a change in the database)

## Use cases

[NIPKaart.nl][nipkaart]

A website that provides insight with a map where disabled parking spaces are in the Netherlands, based on data from users and municipalities.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

This Python project is fully managed using the [Poetry][poetry] dependency
manager.

You need at least:

- Python 3.9+
- [Poetry][poetry-install]

Install all packages, including all development requirements:

```bash
poetry install
```

Poetry creates by default an virtual environment where it installs all
necessary pip packages, to enter or exit the venv run the following commands:

```bash
poetry shell
exit
```

Setup the pre-commit check, you must run this inside the virtual environment:

```bash
pre-commit install
```

*Now you're all set to get started!*

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## License

MIT License

Copyright (c) 2020-2022 Klaas Schoute

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

[api]: https://data.eindhoven.nl/explore/dataset/parkeerplaatsen/information
[nipkaart]: https://www.nipkaart.nl

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-parking-eindhoven/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-parking-eindhoven/actions/workflows/tests.yaml
[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/klaasnicolaas/python-parking-eindhoven.svg?logo=lgtm&logoWidth=18
[code-quality]: https://lgtm.com/projects/g/klaasnicolaas/python-parking-eindhoven/context:python
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-parking-eindhoven.svg
[commits-url]: https://github.com/klaasnicolaas/python-parking-eindhoven/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-parking-eindhoven/branch/main/graph/badge.svg?token=4AMI23ZT7C
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-parking-eindhoven
[forks-shield]: https://img.shields.io/github/forks/klaasnicolaas/python-parking-eindhoven.svg
[forks-url]: https://github.com/klaasnicolaas/python-parking-eindhoven/network/members
[issues-shield]: https://img.shields.io/github/issues/klaasnicolaas/python-parking-eindhoven.svg
[issues-url]: https://github.com/klaasnicolaas/python-parking-eindhoven/issues
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-parking-eindhoven.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-parking-eindhoven.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2022.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/5756f943554d4c6ffa9f/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-parking-eindhoven/maintainability
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/parking-eindhoven/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/parking-eindhoven
[typing-shield]: https://github.com/klaasnicolaas/python-parking-eindhoven/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-parking-eindhoven/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-parking-eindhoven.svg
[releases]: https://github.com/klaasnicolaas/python-parking-eindhoven/releases
[stars-shield]: https://img.shields.io/github/stars/klaasnicolaas/python-parking-eindhoven.svg
[stars-url]: https://github.com/klaasnicolaas/python-parking-eindhoven/stargazers

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com

## Python - ODP Eindhoven Client

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
- **parking_type** (default: 1) - See the list below to find the corresponding number.

| parking_type | number |
| :----------- | :----: |
| Parkeerplaats | 1 |
| Parkeerplaats Vergunning | 2 |
| Parkeerplaats Gehandicapten | 3 |
| Parkeerplaats Afgekruist | 4 |
| Parkeerplaats laden/lossen | 5 |
| Parkeerplaats Electrisch opladen | 6 |

You get the following output data back with this python package:

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `spot_id` | string | The id of the parking spot |
| `parking_type` | string | The type of parking of the parking spot |
| `street` | string | The street name where this parking spot is located |
| `number` | int | The number of parkings spots on this location |
| `longitude` | float | The longitude of the parking spot |
| `latitude` | float | The latitude of the parking spot |
| `updated_at` | datetime | When this parking spot was updated in the dataset |
</details>

### Example

```python
import asyncio

from eindhoven import ODPEindhoven


async def main() -> None:
    """Show example on using the Open Data Platform API of Eindhoven."""
    async with ODPEindhoven() as client:
        locations = await client.locations(limit=100, parking_type=4)
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

[api]: https://data.eindhoven.nl
[parking]: https://data.eindhoven.nl/explore/dataset/parkeerplaatsen/information
[nipkaart]: https://www.nipkaart.nl

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/tests.yaml
[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/klaasnicolaas/python-eindhoven.svg?logo=lgtm&logoWidth=18
[code-quality]: https://lgtm.com/projects/g/klaasnicolaas/python-eindhoven/context:python
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-eindhoven.svg
[commits-url]: https://github.com/klaasnicolaas/python-eindhoven/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-eindhoven/branch/main/graph/badge.svg?token=4AMI23ZT7C
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-eindhoven
[forks-shield]: https://img.shields.io/github/forks/klaasnicolaas/python-eindhoven.svg
[forks-url]: https://github.com/klaasnicolaas/python-eindhoven/network/members
[issues-shield]: https://img.shields.io/github/issues/klaasnicolaas/python-eindhoven.svg
[issues-url]: https://github.com/klaasnicolaas/python-eindhoven/issues
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-eindhoven.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-eindhoven.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2022.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/c577da6bb1b3bb6553bd/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-eindhoven/maintainability
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/eindhoven/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/eindhoven
[typing-shield]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-eindhoven/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-eindhoven.svg
[releases]: https://github.com/klaasnicolaas/python-eindhoven/releases
[stars-shield]: https://img.shields.io/github/stars/klaasnicolaas/python-eindhoven.svg
[stars-url]: https://github.com/klaasnicolaas/python-eindhoven/stargazers

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com

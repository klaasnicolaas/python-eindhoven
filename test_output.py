# pylint: disable=W0621
"""Asynchronous Python client for the Parking Eindhoven API."""

import asyncio

from parking_eindhoven import ParkingEindhoven


async def main() -> None:
    """Show example on using the Parking Eindhoven API client."""
    async with ParkingEindhoven() as client:
        locations = await client.locations(limit=200, parking_type=3)
        count: int

        for index, item in enumerate(locations, 1):
            count = index
            print(item)

        print("__________________________")
        print(f"Total locations found: {count}")


if __name__ == "__main__":
    asyncio.run(main())

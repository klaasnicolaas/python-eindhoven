# pylint: disable=W0621
"""Asynchronous Python client for the Open Data Platform API of Eindhoven."""

import asyncio

from eindhoven import ODPEindhoven, ParkingType


async def main() -> None:
    """Show example on using the Open Data Platform API of Eindhoven."""
    async with ODPEindhoven() as client:
        locations = await client.locations(
            limit=200,
            parking_type=ParkingType.DISABLED_PARKING,
        )

        count: int = len(locations)
        for item in locations:
            print(item)

        print("__________________________")
        print(f"Total locations found: {count}")


if __name__ == "__main__":
    asyncio.run(main())

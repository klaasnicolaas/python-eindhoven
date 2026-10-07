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
        print(locations)

        count: int = len(locations)
        for item in locations:
            print("__________________________")
            print(f"Spot ID: {item.spot_id}")
            print(f"Parking type: {item.source_attributes['type_en_merk']}")
            print(f"Street: {item.source_attributes['straat']}")
            print(f"Number: {item.source_attributes['aantal']}")
            print()
            print("GEOMETRY")
            print(f"Latitude: {item.geometry['coordinates'][1]}")
            print(f"Longitude: {item.geometry['coordinates'][0]}")

        print("__________________________")
        print(f"Total locations found: {count}")


if __name__ == "__main__":
    asyncio.run(main())

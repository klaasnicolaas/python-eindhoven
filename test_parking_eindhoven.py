import aiohttp
import asyncio

import parking_eindhoven

async def main():
    """ Simple function to test the output. """
    async with aiohttp.ClientSession() as client:
        count = 0

        number = 200
        type = "Parkeerplaats Gehandicapten"

        result = await parking_eindhoven.get_locations(number, type, client)
        for item in result:
            count+=1

        print(result)
        print(f'{count} parkeerplekken gevonden')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
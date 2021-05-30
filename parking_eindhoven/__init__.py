from datetime import datetime
from aiohttp import ClientSession, ClientResponseError
from dataclasses import dataclass
import logging

@dataclass
class EindhovenParkerenCase:
    """Class for parking locations in Eindhoven."""

    id: str
    parking_type: str
    street: str
    number: int
    longitude: float
    latitude: float
    created_at: datetime

    @staticmethod
    def from_json(item):
        attr = item["fields"]
        geo = item["geometry"]["coordinates"]
        return EindhovenParkerenCase(
            id=item["recordid"],
            parking_type=attr["type_en_merk"],
            street=attr["straat"],
            number=attr["aantal"],
            longitude=geo[0],
            latitude=geo[1],
            created_at=item["record_timestamp"]
        )

async def get_locations(number, type, session: ClientSession, *, source=EindhovenParkerenCase):
    URL = f'https://data.eindhoven.nl/api/records/1.0/search/?dataset=parkeerplaatsen&q=&rows={number}&facet=straat&facet=type_en_merk&facet=aantal&refine.type_en_merk={type}'

    resp = await session.get(URL)
    data = await resp.json(content_type=None)

    if 'error' in data:
        raise ClientResponseError(
            resp.request_info,
            resp.history,
            status=data['error']['code'],
            message=data['error']['message'],
            headers=resp.headers
        )

    results = []

    for item in data["records"]:
        try:
            results.append(source.from_json(item))
        except KeyError:
            logging.getLogger(__name__).warning("Got wrong data: %s", item)
    return results
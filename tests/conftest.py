"""Fixture for the Eindhoven ODP tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from eindhoven import ODPEindhoven


@pytest.fixture(name="odp_eindhoven_client")
async def client() -> AsyncGenerator[ODPEindhoven, None]:
    """Fixture for the Eindhoven ODP client."""
    async with (
        ClientSession() as session,
        ODPEindhoven(session=session) as odp_eindhoven_client,
    ):
        yield odp_eindhoven_client

import pytest

pytestmark = pytest.mark.asyncio

async def test_sanity():
    assert 1 + 1 == 2

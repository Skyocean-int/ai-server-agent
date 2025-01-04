import pytest
from src.core.query_handler import QueryHandler

@pytest.mark.asyncio
async def test_query_flow():
    handler = QueryHandler()
    try:
        response = await handler.process_query("check configuration files")
        assert response is not None
    finally:
        await handler.close()

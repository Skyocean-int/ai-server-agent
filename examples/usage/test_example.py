import pytest
from ai_agent.core.query_handler import QueryHandler
from ai_agent.tools.file_cache_service import FileReader

@pytest.mark.asyncio
async def test_search_functionality():
    reader = FileReader()
    await reader.initialize()
    try:
        results = await reader.search_files("nginx config")
        assert len(results) > 0
        assert all(isinstance(r, dict) for r in results)
    finally:
        await reader.close()

@pytest.mark.asyncio
async def test_query_handling():
    handler = QueryHandler()
    try:
        response = await handler.process_query("show nginx status")
        assert response is not None
        assert isinstance(response, str)
    finally:
        await handler.close()

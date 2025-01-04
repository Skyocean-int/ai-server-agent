import pytest
from src.core.agent_v2 import AIAgentV2

@pytest.mark.asyncio
async def test_full_query_flow():
    agent = await AIAgentV2.create()
    try:
        response = await agent.process_query("check nginx configuration")
        assert response is not None
        assert len(response) > 0
    finally:
        await agent.close()

@pytest.mark.asyncio
async def test_file_search_and_cache():
    agent = await AIAgentV2.create()
    try:
        # First query - should read from server
        result1 = await agent.process_query("find config files")
        # Second query - should use cache
        result2 = await agent.process_query("find config files")
        assert result1 == result2
    finally:
        await agent.close()

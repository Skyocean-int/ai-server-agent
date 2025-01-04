import pytest
from src.core.query_handler import QueryHandler

@pytest.fixture
async def handler():
    handler = QueryHandler()
    yield handler
    await handler.close()

@pytest.mark.asyncio
async def test_process_query():
    with patch('anthropic.AsyncAnthropic') as mock_anthropic:
        handler = QueryHandler()
        mock_anthropic.messages.create.return_value.content = [{'text': 'test response'}]
        response = await handler.process_query('test query')
        assert 'test response' in response

@pytest.mark.asyncio
async def test_error_handling():
    handler = QueryHandler()
    with pytest.raises(Exception):
        await handler.process_query(None)

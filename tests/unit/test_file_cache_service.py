import pytest
from unittest.mock import Mock, patch
from src.tools.file_cache_service import FileReader

@pytest.fixture
async def file_reader():
    reader = FileReader()
    await reader.initialize()
    yield reader
    await reader.close()

@pytest.mark.asyncio
async def test_search_files():
    reader = FileReader()
    await reader.initialize()
    try:
        results = await reader.search_files("config query")
        assert isinstance(results, list)
    finally:
        await reader.close()

@pytest.mark.asyncio
async def test_search_documentation():
    reader = FileReader()
    await reader.initialize()
    try:
        results = await reader.search_documentation(["configuration"])
        assert isinstance(results, str)
    finally:
        await reader.close()

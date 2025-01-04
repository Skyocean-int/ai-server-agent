# Query Handler

Main entry point for all requests. Located in `src/core/query_handler.py`.

## Core Functions

```python
async def process_query(query: str) -> str:
    """
    Process user queries with context from files and documentation.
    """

async def _get_llm_response(prompt: str) -> str:
    """
    Get response from Claude.
    """
```

## Flow

1. Receives user query
2. Searches relevant files via `file_cache_service`
3. Builds context using RAG
4. Gets LLM response
5. Returns formatted result

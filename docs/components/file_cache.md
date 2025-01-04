# File Cache Service
File reading and caching system. Located in `src/tools/file_cache_service.py`.

## Key Components
- Redis caching
- SSH connections
- FAISS indexing
- Path security

## Core Functions
```python
async def search_files(query: str) -> List[Dict[str, str]]
async def read_file(server: str, path: str) -> Optional[str]
async def search_documentation(queries: List[str]) -> str
{
    "edge": [
        "/opt/edge-node",
        "/opt/edge-api",
        "/var/log"
    ],
    "core": [
        "/opt/dkg",
        "/root",
        "/var/log/dkg"
    ]
}

# API Documentation

## Core API Endpoints

### Query Processing
```python
POST /api/query
Content-Type: application/json

{
    "query": "check server status",
    "server": "server1"  # optional
}
```

### File Operations
```python
GET /api/files
Query params:
- server: string
- path: string
- recursive: boolean

POST /api/files/search
{
    "query": "config file",
    "servers": ["server1", "server2"]
}
```

### System Management
```python
GET /api/status
Returns system status including:
- Server connections
- Redis status
- Vector store status

POST /api/index/rebuild
Rebuilds search indices
```

## Python SDK Usage

```python
from ai_agent.client import AgentClient

client = AgentClient()

# Query servers
response = await client.query("check nginx configuration")

# Search files
files = await client.search_files(
    query="error log",
    servers=["server1"]
)

# Get server status
status = await client.get_status("server1")
```

## WebSocket Events

```python
# Status updates
{
    "type": "status",
    "data": {
        "server": "server1",
        "status": "connected"
    }
}

# Query progress
{
    "type": "progress",
    "data": {
        "query_id": "abc123",
        "progress": 0.5,
        "status": "processing"
    }
}

# API Endpoints

## Query Processing

### POST /api/query

Request:
```json
{
    "query": "string",
    "server": "string" // optional
}
```

Response:
```json
{
    "response": "string",
    "files": [
        {
            "server": "string",
            "path": "string",
            "content": "string"
        }
    ]
}
```

## File Operations

### GET /api/files

Request:
```json
{
    "server": "string",
    "path": "string"
}
```

### POST /api/files/search

Request:
```json
{
    "query": "string",
    "servers": ["string"]
}
```

## System Status

### GET /api/status

Response:
```json
{
    "servers": {
        "core": "connected",
        "edge": "connected"
    },
    "redis": "connected",
    "vector_store": "ready"
}

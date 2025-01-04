# Configuration Examples

## Environment Setup

```bash
ANTHROPIC_API_KEY=your_api_key
REDIS_URL=redis://localhost:6379

# Server configurations
SERVERS='[
  {
    "name": "core",
    "ip": "xxx.xxx.xxx.xxx",
    "search_paths": [
      "/opt/dkg",
      "/root"
    ]
  },
  {
    "name": "edge",
    "ip": "xxx.xxx.xxx.xxx",
    "search_paths": [
      "/opt/edge-node",
      "/opt/edge-api"
    ]
  }
]'
```

## Redis Configuration

```bash
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

## Vector Store Settings

```python
{
    "dimension": 768,
    "index_path": "/opt/ai-agent/data/vector_store",
    "metadata_path": "/opt/ai-agent/data/metadata.pkl"
}


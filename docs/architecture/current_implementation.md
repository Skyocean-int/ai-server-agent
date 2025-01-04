# Current Architecture Implementation

## Core Components

### Query Handler (`query_handler.py`)
- Primary entry point for queries
- Manages file discovery through `file_cache_service`
- Integrates with RAG for context building
- No direct LLM server access
- Async operations

### File Cache Service (`file_cache_service.py`)
- Core file reading component
- Redis caching
- FAISS index management
- Documentation search
- SSH connections pooling
- Path security enforcement

### RAG System
- Hybrid search for file and documentation content
- Vector similarity with FAISS
- Context building from multiple sources
- Response enhancement

## Data Flow

1. **Query Handling**
```mermaid
sequenceDiagram
    User->>QueryHandler: Submit Query
    QueryHandler->>FileCache: Get Files
    FileCache->>Redis: Check Cache
    FileCache->>SSH: Fetch if Needed
    QueryHandler->>RAG: Get Context
    QueryHandler->>LLM: Get Response
    QueryHandler->>User: Return Response
```

2. **File Discovery**
```mermaid
sequenceDiagram
    FileCache->>SSH: List Files
    FileCache->>FAISS: Index Content
    FileCache->>Redis: Cache Results
    FileCache->>Security: Validate Paths
```

## Security Model
- File access through cache only
- Path validation before access
- SSH key-based auth
- No direct LLM server access

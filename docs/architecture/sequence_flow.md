# Query Processing Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web UI
    participant Q as Query Handler
    participant F as File Reader
    participant C as Redis Cache
    participant R as RAG System
    participant L as Claude LLM

    U->>W: Submit Query
    W->>Q: Process Query
    
    Q->>C: Check Cache
    alt Cache Hit
        C-->>Q: Return Cached Data
    else Cache Miss
        Q->>F: Read Files
        F->>C: Cache Results
        C-->>Q: Return Data
    end

    Q->>R: Get Context
    R->>Q: Return Relevant Docs
    
    Q->>L: Generate Response
    L-->>Q: Response
    
    Q->>W: Format Response
    W->>U: Display Results

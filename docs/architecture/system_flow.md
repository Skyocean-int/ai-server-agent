graph TB
    User[User] --> WebUI[Web Interface]
    WebUI --> QueryHandler[Query Handler]
    
    subgraph FileAccess[File Access Layer]
        SSHManager[SSH Manager]
        FileCache[Redis Cache]
        PathMapper[Path Security]
    end

    subgraph Knowledge[Knowledge Layer]
        VectorStore[FAISS Store]
        DocProcessor[Document Processor]
        Indexer[File Indexer]
    end

    subgraph RAG[RAG System]
        ContextBuilder[Context Builder]
        HybridSearch[Hybrid Search]
        ResponseGen[Response Generator]
    end

    QueryHandler --> FileAccess
    QueryHandler --> Knowledge
    QueryHandler --> RAG
    
    SSHManager --> RemoteServer1[Remote Server 1]
    SSHManager --> RemoteServer2[Remote Server 2]
    
    FileCache --> QueryHandler
    VectorStore --> HybridSearch
    DocProcessor --> Indexer
    Indexer --> VectorStore
    
    HybridSearch --> ContextBuilder
    ContextBuilder --> ResponseGen
    ResponseGen --> QueryHandler
    QueryHandler --> WebUI

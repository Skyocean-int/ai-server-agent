import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    content: str
    metadata: Dict[str, Any]
    score: float
    source: str

class HybridSearch:
    def __init__(self, vector_store, relevance_threshold: float = 0.7):
        self.vector_store = vector_store
        self.relevance_threshold = relevance_threshold
        self.embedding_model = None
        self.patterns = {
            'file': r'(file|content|config)',
            'error': r'(error|issue|problem)',
            'status': r'(status|health)'
        }

    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        query_vector = self.embedding_model.encode([query])[0]
        results = await self.vector_store.search(query_vector, limit)
        
        filtered_results = [
            SearchResult(
                content=r['metadata']['content'],
                metadata=r['metadata'],
                score=r['score'],
                source=r['metadata'].get('source', 'unknown')
            )
            for r in results
            if r['score'] >= self.relevance_threshold
        ]
        
        return filtered_results

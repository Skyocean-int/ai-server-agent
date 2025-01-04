import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Structure for retrieval results."""
    content: str
    metadata: Dict[str, Any]
    score: float
    source_type: str  # 'documentation' or 'server'

class Retriever:
    """Handles retrieval operations from vector stores."""
    
    def __init__(self, vector_store, indexer,
                 min_score: float = 0.5,
                 max_results: int = 10):
        self.vector_store = vector_store
        self.indexer = indexer
        self.min_score = min_score
        self.max_results = max_results
        self.embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

    def hybrid_search(self, query: str, 
                     server_filter: Optional[str] = None,
                     time_filter: Optional[int] = None) -> List[RetrievalResult]:
        """Perform hybrid search across documentation and server data."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(
                query,
                normalize_embeddings=True,
                show_progress_bar=False
            )

            # Search both stores
            doc_results = self._search_documentation(query_embedding)
            server_results = self._search_server_data(
                query, 
                server_filter=server_filter,
                time_filter=time_filter
            )

            # Combine and rank results
            combined_results = self._combine_results(doc_results, server_results)
            
            # Log search statistics
            self._log_search_stats(query, combined_results)
            
            return combined_results

        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []

    def _search_documentation(self, 
                            query_embedding: np.ndarray) -> List[RetrievalResult]:
        """Search documentation vector store."""
        try:
            results = self.vector_store.search_documentation(
                query_embedding,
                k=self.max_results
            )

            retrieval_results = []
            for result in results:
                if result['distance'] <= self.min_score:
                    retrieval_results.append(
                        RetrievalResult(
                            content=result.get('content', ''),
                            metadata=result.get('metadata', {}),
                            score=float(result['distance']),
                            source_type='documentation'
                        )
                    )
            
            return retrieval_results

        except Exception as e:
            logger.error(f"Error searching documentation: {str(e)}")
            return []

    def _search_server_data(self, 
                          query: str,
                          server_filter: Optional[str] = None,
                          time_filter: Optional[int] = None) -> List[RetrievalResult]:
        """Search server data with filters."""
        try:
            # Prepare filter criteria
            filter_criteria = {}
            if server_filter:
                filter_criteria['server'] = server_filter
            if time_filter:
                cutoff_time = (datetime.now() - timedelta(minutes=time_filter)).isoformat()
                filter_criteria['timestamp'] = {'$gt': cutoff_time}

            results = self.vector_store.search_server_data(
                query_text=query,
                filter_criteria=filter_criteria,
                k=self.max_results
            )

            retrieval_results = []
            for result in results:
                score = result.get('distance', 1.0)
                if score <= self.min_score:
                    retrieval_results.append(
                        RetrievalResult(
                            content=result.get('text', ''),
                            metadata=result.get('metadata', {}),
                            score=float(score),
                            source_type='server'
                        )
                    )

            return retrieval_results

        except Exception as e:
            logger.error(f"Error searching server data: {str(e)}")
            return []

    def _combine_results(self, 
                        doc_results: List[RetrievalResult],
                        server_results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Combine and rank results from both sources."""
        try:
            # Combine all results
            combined = doc_results + server_results
            
            # Sort by score (lower is better)
            combined.sort(key=lambda x: x.score)
            
            # Return top results
            return combined[:self.max_results]

        except Exception as e:
            logger.error(f"Error combining results: {str(e)}")
            return []

    def search_server(self, 
                     server: str,
                     query: str,
                     time_window: Optional[int] = None) -> List[RetrievalResult]:
        """Search data from a specific server."""
        return self.hybrid_search(
            query,
            server_filter=server,
            time_filter=time_window
        )

    def get_context(self, 
                   query: str,
                   server: Optional[str] = None,
                   max_items: int = 5) -> str:
        """Get context for LLM prompt."""
        try:
            # Perform search
            results = self.hybrid_search(
                query,
                server_filter=server,
                time_filter=60  # Recent data from last hour
            )[:max_items]

            if not results:
                return ""

            # Format context
            context_parts = []
            for result in results:
                source = f"[{result.source_type}]"
                if result.metadata.get('server'):
                    source += f" Server: {result.metadata['server']}"
                if result.metadata.get('filepath'):
                    source += f" File: {result.metadata['filepath']}"

                context_parts.append(
                    f"{source}\n{result.content}\n"
                )

            return "\n---\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return ""

    def _log_search_stats(self, query: str, results: List[RetrievalResult]):
        """Log search statistics for monitoring."""
        try:
            stats = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'total_results': len(results),
                'documentation_results': sum(1 for r in results if r.source_type == 'documentation'),
                'server_results': sum(1 for r in results if r.source_type == 'server'),
                'average_score': sum(r.score for r in results) / len(results) if results else 0
            }
            logger.info(f"Search stats: {stats}")

        except Exception as e:
            logger.error(f"Error logging search stats: {str(e)}")

    def get_recent_server_data(self,
                             server: str,
                             minutes: int = 60) -> List[RetrievalResult]:
        """Get recent data from a specific server."""
        try:
            return self._search_server_data(
                query="",  # Empty query to match recent data
                server_filter=server,
                time_filter=minutes
            )

        except Exception as e:
            logger.error(f"Error getting recent server data: {str(e)}")
            return []

    def get_similar_documents(self, 
                            content: str,
                            min_similarity: float = 0.7) -> List[RetrievalResult]:
        """Find similar documents to given content."""
        try:
            # Generate embedding for content
            content_embedding = self.embedding_model.encode(
                content,
                normalize_embeddings=True,
                show_progress_bar=False
            )

            # Search both stores
            doc_results = self._search_documentation(content_embedding)
            server_results = self._search_server_data(content)

            # Filter by similarity threshold
            combined = [
                result for result in (doc_results + server_results)
                if result.score >= min_similarity
            ]

            # Sort by similarity
            combined.sort(key=lambda x: x.score, reverse=True)
            return combined

        except Exception as e:
            logger.error(f"Error finding similar documents: {str(e)}")
            return []

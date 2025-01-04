import logging
from typing import List, Dict, Any, Optional
import json
import numpy as np
from datetime import datetime
import asyncio
import redis.asyncio as redis
import traceback

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, redis_url: str = 'redis://localhost:6379'):
        self.redis_url = redis_url
        self.prefix = "ai_agent"
        self._lock = asyncio.Lock()
        self._redis = None
        self._connection_lock = asyncio.Lock()
        logger.info(f"VectorStore initialized with URL: {redis_url}")

    async def _ensure_connection(self) -> redis.Redis:
        """Ensure Redis connection is active and valid."""
        async with self._connection_lock:
            try:
                if self._redis is None:
                    logger.debug("Creating new Redis connection")
                    self._redis = await redis.from_url(
                        self.redis_url,
                        decode_responses=False,
                        health_check_interval=30,
                        retry_on_timeout=True
                    )
                await self._redis.ping()
                return self._redis
            except Exception as e:
                logger.error(f"Redis connection error:\n{traceback.format_exc()}")
                self._redis = None
                # Retry once
                self._redis = await redis.from_url(
                    self.redis_url,
                    decode_responses=False,
                    health_check_interval=30,
                    retry_on_timeout=True
                )
                await self._redis.ping()
                return self._redis

    async def add_vectors(self, texts: List[str], metadata_list: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Store vectors with their metadata and create indices."""
        try:
            async with self._lock:
                redis_client = await self._ensure_connection()
                pipe = redis_client.pipeline()

                # Store main vector data
                for i, (text, meta, emb) in enumerate(zip(texts, metadata_list, embeddings)):
                    key = f"{self.prefix}:doc:{datetime.now().isoformat()}:{i}"
                    # Example: Add doc_section or priority if not present
                    doc_section = meta.get('doc_section', 'general')
                    priority = meta.get('priority', 'normal')

                    doc_data = {
                        'text': text,
                        'metadata': json.dumps(meta),
                        'embedding': json.dumps(emb),
                        'doc_section': doc_section,
                        'priority': priority
                    }

                    await pipe.hset(key, mapping=doc_data)

                    # Create category indices
                    if 'categories' in meta:
                        for category in meta['categories']:
                            category_key = f"{self.prefix}:category:{category}"
                            await pipe.sadd(category_key, key)
                    
                    # Create concept indices
                    if 'concepts' in meta:
                        for concept_type, concepts in meta['concepts'].items():
                            for concept in concepts:
                                concept_key = f"{self.prefix}:concept:{concept_type}:{concept}"
                                await pipe.sadd(concept_key, key)

                await pipe.execute()
                logger.info(f"Successfully added {len(texts)} vectors with indices")
        except Exception as e:
            logger.error(f"Error in add_vectors:\n{traceback.format_exc()}")
            raise

    async def search(self,
                     query_embedding: List[float],
                     categories: List[str] = None,
                     concepts: Dict[str, List[str]] = None,
                     limit: int = 5) -> List[Dict[str, Any]]:
        """Enhanced search with category and concept filtering."""
        try:
            redis_client = await self._ensure_connection()
            
            # Get keys to search based on filters
            keys_to_search = set()
            
            if categories:
                for category in categories:
                    category_keys = await redis_client.smembers(f"{self.prefix}:category:{category}")
                    keys_to_search.update(category_keys)
            
            if concepts:
                for concept_type, concept_list in concepts.items():
                    for concept in concept_list:
                        concept_keys = await redis_client.smembers(
                            f"{self.prefix}:concept:{concept_type}:{concept}"
                        )
                        keys_to_search.update(concept_keys)
            
            # If no filters, search all documents
            if not keys_to_search:
                keys_to_search = await redis_client.keys(f"{self.prefix}:doc:*")
            
            logger.debug(f"Searching {len(keys_to_search)} documents")
            results = []
            query_vector = np.array(query_embedding)

            pipe = redis_client.pipeline()
            for key in keys_to_search:
                pipe.hgetall(key)
            all_data = await pipe.execute()

            for data in all_data:
                if not data:
                    continue
                stored_vector = np.array(json.loads(data[b'embedding'].decode()))
                similarity = float(np.dot(query_vector, stored_vector))

                results.append({
                    'content': data[b'text'].decode(),
                    'metadata': json.loads(data[b'metadata'].decode()),
                    'score': similarity,
                    'doc_section': data.get(b'doc_section', b'').decode(),
                    'priority': data.get(b'priority', b'').decode()
                })

            sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)[:limit]
            logger.info(f"Search completed. Found {len(sorted_results)} results")
            return sorted_results

        except Exception as e:
            logger.error(f"Error in search:\n{traceback.format_exc()}")
            raise

    async def get_categories(self) -> List[str]:
        try:
            redis_client = await self._ensure_connection()
            category_keys = await redis_client.keys(f"{self.prefix}:category:*")
            return [key.split(':')[-1] for key in category_keys]
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []

    async def clear(self):
        """Clear all stored data."""
        try:
            async with self._lock:
                redis_client = await self._ensure_connection()
                keys = await redis_client.keys(f"{self.prefix}:*")
                if keys:
                    await redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} keys")
        except Exception as e:
            logger.error(f"Error in clear:\n{traceback.format_exc()}")
            raise

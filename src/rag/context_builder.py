import logging
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Context:
   search_results: list
   server_info: dict
   metadata: dict

class ContextBuilder:
   def __init__(self, vector_store):
       self.vector_store = vector_store
   
   async def build_context(self, query: str, server: str = None) -> Context:
       search_results = await self.vector_store.search(query, limit=5)
       metadata = {'query': query, 'server': server}
       return Context(
           search_results=search_results,
           server_info={},
           metadata=metadata
       )

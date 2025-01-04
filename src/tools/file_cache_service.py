import asyncio
import logging
import json
from typing import Optional, Dict, List, Set
import paramiko
import os
import re
import redis.asyncio as redis
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from datetime import datetime
import pickle
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class FileReader:
    """Main class for handling file operations across servers with caching and search capabilities."""
    
    def __init__(self):
        # Basic connection management
        self._redis = None
        self._redis_lock = asyncio.Lock()
        self.ssh_clients = {}
        self.initialization_lock = asyncio.Lock()
        
        # Vector search setup
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_path = '/opt/ai-agent/data/file_index'
        self.index_metadata_path = '/opt/ai-agent/data/file_metadata.pkl'
        self.index = None
        self.index_metadata = {}
        
        # Define searchable paths for each server
        self.search_paths = {
            'edge': [
                '/opt/edge-node',
                '/opt/edge-node/edge-node-api',
                '/opt/edge-node/edge-node-authentication-service',
                '/opt/edge-node/edge-node-drag',
                '/opt/edge-node/edge-node-interface',
                '/opt/edge-node/edge-node-knowledge-mining',
                '/root',
                '/etc/nginx/sites-enabled',
                '/var/log'
            ],
            'core': [
                '/opt/dkg',
                '/opt/dkg/dkg-node',
                '/root',
                '/opt/dkg/config',
                '/var/log/dkg',
                '/etc/systemd/system',
                '/etc/nginx/sites-enabled'
            ],
            'erp': [
                '/home/frappe/frappe-bench',
                '/home/frappe/frappe-bench/sites',
                '/etc/nginx/conf.d',
                '/var/log',
                '/home/frappe/frappe-bench/config'
            ]
        }

        # Directories to exclude from searches
        self.excluded_dirs = {
            'node_modules',
            'dist',
            'dist.browser',
            'build',
            'vendor',
            '.git',
            '__pycache__',
            'cache',
            'tmp'
        }
        
        # Important configuration file patterns
        self.config_patterns = [
            '.env',
            '.json',
            '.yaml',
            '.yml',
            '.conf',
            '.config',
            'config.',
            '.ini',
            '.rc',
            'noderc',
            '.service'
        ]

    @property
    async def redis(self):
        """Ensure Redis connection exists and return it."""
        if self._redis is None:
            async with self._redis_lock:
                if self._redis is None:
                    self._redis = await redis.from_url(
                        'redis://localhost:6379',
                        decode_responses=True,
                        socket_connect_timeout=2,
                        retry_on_timeout=True,
                        health_check_interval=30
                    )
                    await self._redis.ping()
        return self._redis

    async def initialize(self):
        """Initialize all required connections and systems."""
        async with self.initialization_lock:
            try:
                await self.ensure_redis()
                await self.connect_servers()
                await self.initialize_index()
                await self.initialize_cache()
                logger.info("File reader initialized successfully")
            except Exception as e:
                logger.error("Error initializing file reader: " + str(e))
                raise

    async def ensure_redis(self):
        """Ensure Redis connection is active."""
        if self._redis is None:
            async with self._redis_lock:
                if self._redis is None:
                    try:
                        self._redis = await redis.from_url(
                            'redis://localhost:6379',
                            decode_responses=True,
                            socket_connect_timeout=2,
                            retry_on_timeout=True,
                            health_check_interval=30
                        )
                        await self._redis.ping()
                        logger.info("Redis connection established")
                    except Exception as e:
                        logger.error("Redis connection failed: " + str(e))
                        self._redis = None
                        raise

    async def connect_servers(self):
        """Initialize SSH connections to all servers."""
        servers = {
            'core': os.getenv('CORE_IP'),
            'edge': os.getenv('EDGE_IP'),
            'erp': os.getenv('ERPNEXT_IP')
        }

        for name, ip in servers.items():
            if not ip:
                continue

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                client.connect(
                    hostname=ip,
                    username='root',
                    key_filename='/root/.ssh/id_ed25519',
                    timeout=10
                )
                self.ssh_clients[name] = client
                logger.info("Connected to " + name + " server")
            except Exception as e:
                logger.error("Failed to connect to " + name + ": " + str(e))

    async def initialize_index(self):
        """Initialize or load the FAISS index."""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            if os.path.exists(self.index_path) and os.path.exists(self.index_metadata_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.index_metadata_path, 'rb') as f:
                    self.index_metadata = pickle.load(f)
                logger.info("Loaded existing file index")
            else:
                dimension = self.embedding_model.get_sentence_embedding_dimension()
                self.index = faiss.IndexFlatL2(dimension)
                self.index_metadata = {}
                logger.info("Created new file index")
            
            await self.index_important_files()
            
        except Exception as e:
            logger.error("Error initializing index: " + str(e))
            raise

    async def index_important_files(self):
        """Index important configuration files."""
        important_paths = {
            'core': [
                '/opt/dkg/dkg-node/config/config.json',
                '/opt/dkg/dkg-node/.origintrail_noderc',
                '/opt/dkg/dkg-node/.env'
            ],
            'edge': [
                '/opt/edge-node/edge-node-api/.env',
                '/opt/edge-node/edge-node-authentication-service/.env',
                '/opt/edge-node/edge-node-drag/.env'
            ]
        }

        for server, paths in important_paths.items():
            for path in paths:
                content = await self.read_file(server, path, use_cache=False)
                if content:
                    await self.index_file_content(server, path, content)

    async def index_file_content(self, server: str, path: str, content: str):
        """Add file content to the search index."""
        try:
            embedding = self.embedding_model.encode([content])[0]
            self.index.add(np.array([embedding]).astype('float32'))
            
            idx = self.index.ntotal - 1
            self.index_metadata[idx] = {
                'server': server,
                'path': path,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            
            faiss.write_index(self.index, self.index_path)
            with open(self.index_metadata_path, 'wb') as f:
                pickle.dump(self.index_metadata, f)
                
            logger.info("Indexed " + server + ":" + path)
            
        except Exception as e:
            logger.error("Error indexing file content: " + str(e))

    async def search_similar_files(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        """Search for similar files using vector similarity."""
        try:
            query_embedding = self.embedding_model.encode([query])[0]
            D, I = self.index.search(np.array([query_embedding]).astype('float32'), k)
            
            results = []
            for i, idx in enumerate(I[0]):
                if idx != -1:
                    metadata = self.index_metadata.get(int(idx))
                    if metadata:
                        results.append({
                            'server': metadata['server'],
                            'path': metadata['path'],
                            'content': metadata['content'],
                            'score': float(D[0][i]),
                            'timestamp': metadata['timestamp']
                        })
            
            return results
        except Exception as e:
            logger.error("Error searching similar files: " + str(e))
            return []

    def _is_excluded_path(self, path: str) -> bool:
        """Check if path should be excluded from search."""
        return any('/' + excluded + '/' in path for excluded in self.excluded_dirs)

    async def read_file(self, server: str, path: str, use_cache: bool = True) -> Optional[str]:
        """Read file content from server or cache."""
        if self._is_excluded_path(path):
            return None

        cache_key = "file:" + server + ":" + path
        
        try:
            if use_cache:
                redis_client = await self.redis
                cached = await redis_client.get(cache_key)
                if cached:
                    return cached
        except Exception as e:
            logger.error("Redis error reading cache: " + str(e))

        if server in self.ssh_clients:
            try:
                stdin, stdout, stderr = self.ssh_clients[server].exec_command("cat " + path)
                content = stdout.read().decode()
                error = stderr.read().decode()
                
                if error and not content:
                    logger.debug("No content for " + server + ":" + path + ": " + error)
                    return None
                    
                if content and use_cache:
                    try:
                        redis_client = await self.redis
                        await redis_client.setex(cache_key, 300, content)
                        logger.info("Cached " + server + ":" + path)
                    except Exception as e:
                        logger.error("Redis error setting cache: " + str(e))
                    
                    await self.index_file_content(server, path, content)
                    
                return content
            except Exception as e:
                logger.error("Error reading " + path + " from " + server + ": " + str(e))
        
        return None

    async def search_files(self, query: str) -> List[Dict[str, str]]:
        """Search files across all servers."""
        results = []
        
        index_results = await self.search_similar_files(query)
        results.extend(index_results)
        
        for server in self.ssh_clients:
            for base_path in self.search_paths[server]:
                try:
                    exclude_parts = []
                    for d in self.excluded_dirs:
                        exclude_parts.append("-not -path '*/" + d + "/*'")
                    exclude_args = ' '.join(exclude_parts)
                    
                    cmd = "find " + base_path + " -type f " + exclude_args + " 2>/dev/null"
                    stdin, stdout, stderr = self.ssh_clients[server].exec_command(cmd)
                    files = stdout.read().decode().splitlines()
                    
                    for path in files:
                        if query.lower() in path.lower():
                            content = await self.read_file(server, path)
                            if content and not self._is_excluded_path(path):
                                results.append({
                                    'server': server,
                                    'path': path,
                                    'content': content,
                                    'score': 1.0 if query.lower() in content.lower() else 0.5
                                })
                except Exception as e:
                    logger.warning("Error searching " + server + ":" + base_path + ": " + str(e))
        
        seen_paths = set()
        unique_results = []
        for r in results:
            if r['path'] not in seen_paths:
                seen_paths.add(r['path'])
                unique_results.append(r)
        
        return sorted(unique_results, key=lambda x: x.get('score', 0), reverse=True)

    async def search_documentation(self, queries: List[str]) -> str:
        """Search through DKG documentation."""
        docs_path = '/opt/ai-agent/docs/dkg/dkg-docs'
        results = []
        formatted_results = []
        
        try:
            if not os.path.exists(docs_path):
                logger.warning("Documentation path " + docs_path + " not found")
                return ""

            for root, _, files in os.walk(docs_path):
                for file in files:
                    if file.endswith(('.md', '.txt')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                for query in queries:
                                    if query.lower() in content.lower():
                                        relative_path = os.path.relpath(filepath, docs_path)
                                        file_exists = any(r['file'] == relative_path for r in results)
                                        if not file_exists:
                                            results.append({
                                                'file': relative_path,
                                                'content': content,
                                                'matched_query': query
                                            })
                                            break
                        except Exception as e:
                            logger.error("Error reading file " + filepath + ": " + str(e))
                            continue

            if results:
                for r in results:
                    content = r['content']
                    query = r['matched_query']
                    paragraphs = content.split('\n\n')
                    relevant_paragraphs = [p.strip() for p in paragraphs if query.lower() in p.lower()]
                    if relevant_paragraphs:
                        result_text = "From " + r['file'] + " (matched query: " + r['matched_query'] + "):\n"
                        result_text += "\n".join(relevant_paragraphs)
                        formatted_results.append(result_text)
                
                return "\n\n---\n\n".join(formatted_results)
                        
        except Exception as e:
            logger.error("Error searching documentation: " + str(e))
        
        return ""

    async def initialize_cache(self):
        """Initialize important file caching."""
        important_paths = {
            'core': [
                '/opt/dkg/dkg-node/config/config.json',
                '/opt/dkg/dkg-node/.origintrail_noderc',
                '/opt/dkg/dkg-node/.env'
            ],
            'edge': [
                '/opt/edge-node/edge-node-api/.env',
                '/opt/edge-node/edge-node-authentication-service/.env',
                '/opt/edge-node/edge-node-drag/.env'
            ]
        }

        for server, paths in important_paths.items():
            for path in paths:
                content = await self.read_file(server, path)
                if content:
                    logger.info("Cached important file " + server + ":" + path)
    async def close(self):
        """Close all connections properly."""
        if hasattr(self, '_redis') and self._redis is not None:
            try:
                redis_client = await self.redis
                await redis_client.aclose()
                self._redis = None
            except Exception as e:
                logger.error("Error closing Redis connection: " + str(e))
        for client in self.ssh_clients.values():
            try:
                client.close()
            except Exception as e:
                logger.error("Error closing SSH connection: " + str(e))

# Global instance
file_reader = FileReader()

import asyncio
from typing import List, Dict, Optional, Any
import re
from anthropic import AsyncAnthropic
import os
import logging
import json
from dotenv import load_dotenv

from src.tools.file_cache_service import file_reader

logger = logging.getLogger(__name__)

class QueryHandler:
    def __init__(self):
        # Explicitly load environment variables
        load_dotenv()
        
        # Get API key and validate
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
            
        # Initialize Anthropic client with explicit key
        self.anthropic = AsyncAnthropic(
            api_key=api_key
        )
        
        logger.info("QueryHandler initialized successfully")

    async def process_query(self, query: str) -> str:
        """Process user queries with context from files and documentation."""
        try:
            # Get files related to the error/query
            relevant_files = await file_reader.search_files(query)
            
            # If there's a 401/auth error, look for specific config files
            if '401' in query or 'authentication' in query.lower() or 'unauthorized' in query.lower():
                # Check all servers for relevant config files
                auth_files = [
                    '/root/.origintrail_noderc',
                    '/opt/dkg/config/config.json',
                    '/opt/edge-node/edge-node-api/.env',
                    '/opt/edge-node/edge-node-authentication-service/.env'
                ]
                
                for server in ['core', 'edge']:
                    for filepath in auth_files:
                        content = await file_reader.read_file(server, filepath)
                        if content:
                            relevant_files.append({
                                'server': server,
                                'path': filepath,
                                'content': content
                            })

            # Search OriginTrail documentation
            doc_results = await file_reader.search_documentation([
                'node authentication',
                'dkg authentication',
                'auth token',
                'node info api',
                '401 unauthorized'
            ])

            # Format context for LLM
            prompt = """Help troubleshoot this OriginTrail DKG issue:

Error/Issue:
{query}

Related Files Found:
{files}

Documentation Context:
{docs}

Based on the error message, configuration files, and documentation:
1. What is the root cause of the 401 authentication error?
2. What specific configurations or values are missing or incorrect?
3. What exact changes need to be made to fix this?
4. What commands should be run to apply the fixes?

Provide a clear step-by-step solution.""".format(
                query=query,
                files=json.dumps(relevant_files, indent=2),
                docs=doc_results
            )

            # Get analysis from LLM
            return await self._get_llm_response(prompt)

        except Exception as e:
            logger.error("Error processing query", exc_info=True)
            return f"Error processing your request: {str(e)}"

    async def _get_llm_response(self, prompt: str) -> str:
        """Get response from Claude."""
        try:
            system_prompt = """You are an AI expert in OriginTrail DKG troubleshooting.
            When analyzing errors and providing solutions:
            1. Analyze the complete context (error, files, and docs)
            2. Explain the specific cause of the error
            3. Provide exact configuration changes needed
            4. Give step-by-step commands to implement fixes
            5. Explain why the solution will work

            Be specific about files, values, and commands."""

            response = await self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
                system=system_prompt,
                temperature=0
            )
            return response.content[0].text
            
        except Exception as e:
            logger.error("LLM error", exc_info=True)
            return f"Error getting AI response: {str(e)}"

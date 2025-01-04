import os
import logging
import asyncio
import re
from typing import List, Dict

from dotenv import load_dotenv
from anthropic import AsyncAnthropic

from src.server_management.ssh_manager import SSHManager
from src.knowledge_base.indexer import SimpleIndexer  # Our minimal doc search

logger = logging.getLogger(__name__)

class AIAgentV4:
    def __init__(self):
        load_dotenv()
        self.logger = logging.getLogger(__name__)

        anthro_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.anthropic = AsyncAnthropic(api_key=anthro_key)

        # We'll gather servers from environment
        self.server_connections = {
            'core':  os.getenv('CORE_IP'),
            'edge':  os.getenv('EDGE_IP'),
            'erp':   os.getenv('ERPNEXT_IP')
        }
        self.ssh_clients = {}

        # Provide a minimal RAG index
        self.indexer = SimpleIndexer()

        # System instructions referencing both tools
        self.system_instructions = (
            "You are an AI assistant with two tools:\n"
            "1) file_retriever\n"
            "   If you need to read a server file, produce lines:\n"
            "   Tool: file_retriever\n"
            '   Tool Input: "serverKey:/absolute/path"\n\n'
            "2) docs_search\n"
            "   If you need doc context from the knowledge base, produce lines:\n"
            "   Tool: docs_search\n"
            '   Tool Input: "your doc question"\n\n'
            "No disclaimers about lacking server access. All permissions are in place. When done, produce a final answer."
        )

    async def initialize(self):
        """Connect to each server with SSH."""
        for name, ip in self.server_connections.items():
            if ip:
                mgr = SSHManager()
                await mgr.get_connection(ip)
                self.ssh_clients[name.lower()] = mgr  # Ensure keys are lowercase
                logger.info(f"[AIAgentV4] Connected to {name} server at {ip}")

    async def process_query(self, query: str) -> str:
        """
        The main method the UI calls for user queries. 
        We'll do multi-turn:
          1) user + system
          2) LLM output => parse tool usage => run => feed output => repeat
        """
        messages = [{"role": "user", "content": query}]
        conversation = []

        while True:
            # 1) call LLM
            response_text = await self._anthropic_completion(messages, conversation)
            conversation.append({"role": "assistant", "content": response_text})

            # 2) parse tool usage
            tool_name, tool_input = self._parse_tool_call(response_text)

            if tool_name == "file_retriever" and tool_input:
                # read file
                file_result = self._fetch_file_contents(tool_input)
                # feed back tool output
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": f"Tool Output:\n{file_result}"})

            elif tool_name == "docs_search" and tool_input:
                # doc retrieval
                doc_result = self._search_docs(tool_input)
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": f"Tool Output:\n{doc_result}"})

            else:
                # no more tool calls => final answer
                return response_text

    def _parse_tool_call(self, text: str):
        """Parse tool calls from LLM output."""
        lines = text.split("\n")
        tool_name = None
        tool_input = None

        pattern_tool = r"(?i)^\s*Tool:\s*(\S+)"
        pattern_inpt = r'(?i)^\s*Tool\s+Input:\s*"([^"]+)"'

        for line in lines:
            line_str = line.strip()
            mt = re.match(pattern_tool, line_str)
            if mt:
                tool_name = mt.group(1).lower()  # Normalize to lowercase

            mi = re.match(pattern_inpt, line_str)
            if mi:
                tool_input = mi.group(1)

        return (tool_name, tool_input)

    def _fetch_file_contents(self, input_str: str) -> str:
        """Process file retrieval request."""
        try:
            if ':' not in input_str:
                return "[file_retriever error] Must be serverKey:/path"

            server_key, file_path = input_str.split(':', 1)
            server_key = server_key.strip().lower()  # Normalize to lowercase
            file_path  = file_path.strip()

            if server_key not in self.ssh_clients:
                return f"[file_retriever error] Unknown server '{server_key}'"

            # run command
            out, err = asyncio.get_event_loop().run_until_complete(
                self.ssh_clients[server_key].run_command(f"cat {file_path}")
            )
            if out.strip():
                return out
            elif err.strip():
                return f"[file_retriever error reading {server_key}:{file_path}]\n{err}"
            else:
                return "[file_retriever] No output or error. Possibly empty file."
        except Exception as e:
            return f"[file_retriever exception] {str(e)}"

    def _search_docs(self, query: str) -> str:
        """Search documentation."""
        try:
            results = self.indexer.search(query)
            if not results:
                return "[docs_search] No relevant doc content found."
            # combine all
            combined = "\n---\n".join(r["content"] for r in results)
            return combined
        except Exception as e:
            return f"[docs_search error] {str(e)}"

    async def _anthropic_completion(self, messages: List[Dict[str,str]], conversation: List[Dict[str,str]]) -> str:
        """Get response from Claude API."""
        try:
            response = await self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4096,
                temperature=0,
                system=self.system_instructions,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            return f"Error getting response: {str(e)}"

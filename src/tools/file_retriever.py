import logging
from typing import List, Optional, Dict
import re

logger = logging.getLogger(__name__)

class FileRetriever:
    def __init__(self, ssh_clients):
        self.ssh_clients = ssh_clients
        self.common_paths = {
            'edge': [
                '/opt/edge-node/edge-node-api',
                '/opt/edge-node/edge-node-authentication-service',
                '/opt/edge-node/edge-node-drag',
                '/opt/edge-node/edge-node-interface',
                '/opt/edge-node/edge-node-knowledge-mining'
            ],
            'core': [
                '/opt/dkg',
                '/root/.origintrail_noderc'
            ],
            'erp': [
                '/home/frappe/frappe-bench/sites'
            ]
        }

    async def find_file(self, server: str, pattern: str) -> List[str]:
        """Find files matching pattern in common paths"""
        found_files = []
        try:
            if server in self.ssh_clients:
                client = self.ssh_clients[server]
                for base_path in self.common_paths[server]:
                    cmd = f'find {base_path} -name "{pattern}" 2>/dev/null'
                    output, _ = await client.run_command(cmd)
                    if output:
                        found_files.extend(output.splitlines())
                logger.info(f"Found {len(found_files)} files matching '{pattern}' on {server}")
            return found_files
        except Exception as e:
            logger.error(f"Error finding files on {server}: {str(e)}")
            return []

    async def read_file(self, server: str, path: str) -> Optional[str]:
        """Read file content safely"""
        try:
            if server in self.ssh_clients:
                client = self.ssh_clients[server]
                output, error = await client.run_command(f'cat {path}')
                if error:
                    logger.warning(f"Error reading {path} on {server}: {error}")
                return output if output else None
            return None
        except Exception as e:
            logger.error(f"Error reading file {path} on {server}: {str(e)}")
            return None

    async def read_service_logs(self, server: str, service: str, lines: int = 50) -> Optional[str]:
        """Read service logs"""
        try:
            if server in self.ssh_clients:
                client = self.ssh_clients[server]
                cmd = f'journalctl -u {service} -n {lines}'
                output, _ = await client.run_command(cmd)
                return output if output else None
            return None
        except Exception as e:
            logger.error(f"Error reading logs for {service} on {server}: {str(e)}")
            return None

    def parse_file_request(self, input_str: str) -> Optional[Dict[str, str]]:
        """Parse file request in format server:/path or server:pattern"""
        try:
            if ':' not in input_str:
                return None
            
            server, path = input_str.split(':', 1)
            return {
                'server': server.strip().lower(),
                'path': path.strip()
            }
        except Exception as e:
            logger.error(f"Error parsing file request '{input_str}': {str(e)}")
            return None

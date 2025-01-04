import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class PathMapper:
    def __init__(self):
        self.path_maps = {
            'edge': {
                'api': '/opt/edge-node/edge-node-api',
                'auth': '/opt/edge-node/edge-node-authentication-service',
                'drag': '/opt/edge-node/edge-node-drag',
                'interface': '/opt/edge-node/edge-node-interface',
                'mining': '/opt/edge-node/edge-node-knowledge-mining',
                'env': '/opt/edge-node/edge-node-api/.env'
            },
            'core': {
                'config': '/root/.origintrail_noderc',
                'dkg': '/opt/dkg',
                'env': '/opt/dkg/.env'
            },
            'erp': {
                'sites': '/home/frappe/frappe-bench/sites',
                'config': '/home/frappe/frappe-bench/config',
                'logs': '/home/frappe/frappe-bench/logs'
            }
        }
        
        # Common file patterns
        self.common_files = {
            'env': '.env',
            'config': '*.json',
            'logs': '*.log'
        }

    def resolve_path(self, server: str, service: str) -> Optional[str]:
        """Get absolute path for a service on a server"""
        try:
            return self.path_maps.get(server, {}).get(service)
        except Exception as e:
            logger.error(f"Error resolving path for {server}/{service}: {str(e)}")
            return None

    def get_service_paths(self, server: str) -> Dict[str, str]:
        """Get all service paths for a server"""
        return self.path_maps.get(server, {})

    def get_common_pattern(self, file_type: str) -> Optional[str]:
        """Get common file pattern"""
        return self.common_files.get(file_type)

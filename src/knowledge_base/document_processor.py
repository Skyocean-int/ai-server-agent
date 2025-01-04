import logging
from typing import List, Dict, Any
from pathlib import Path
import re
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.documentation_paths = {
            'origintrail': '/opt/ai-agent/docs/dkg/dkg-docs',
            'erpnext': '/opt/ai-agent/docs/erpnext/erpnext'
        }
        self.SUPPORTED_TYPES = {
            '.md': 'markdown',
            '.txt': 'text',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.json': 'json',
            '.env': 'env'
        }
        logger.info("Document processor initialized")

    async def process_documentation(self) -> List[Dict[str, Any]]:
        documents = []
        for doc_type, base_path in self.documentation_paths.items():
            try:
                path = Path(base_path)
                if not path.exists():
                    logger.error(f"Documentation path not found: {path}")
                    continue

                for file_path in path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_TYPES:
                        try:
                            content = file_path.read_text()
                            categories = self._extract_categories(content, str(file_path))
                            concepts = self._extract_key_concepts(content)

                            doc_section = "tutorial" if "step-by-step" in content.lower() else "general"
                            # Additional logic to detect code blocks
                            code_blocks = re.findall(r'```(.*?)```', content, re.DOTALL)

                            documents.append({
                                'content': content,
                                'metadata': {
                                    'source': str(file_path.relative_to(path)),
                                    'doc_type': doc_type,
                                    'categories': categories,
                                    'concepts': concepts,
                                    'file_type': self.SUPPORTED_TYPES[file_path.suffix.lower()],
                                    'doc_section': doc_section,
                                    'code_blocks': code_blocks
                                }
                            })
                        except Exception as e:
                            logger.error(f"Error processing file {file_path}: {e}")

            except Exception as e:
                logger.error(f"Error processing {doc_type} documentation: {e}")

        return documents

    async def process_server_file(self, content: str, server: str, filepath: str) -> Dict[str, Any]:
        try:
            file_type = Path(filepath).suffix.lower()
            metadata = {
                'server': server,
                'filepath': filepath,
                'file_type': self.SUPPORTED_TYPES.get(file_type, 'text'),
                'timestamp': datetime.now().isoformat()
            }

            if file_type == '.env':
                metadata.update(self._process_env_file(content))
            elif file_type in ['.yml', '.yaml', '.json']:
                metadata.update(self._process_config_file(content, file_type))

            return {
                'content': content,
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"Error processing server file: {e}")
            return {'content': content, 'metadata': {'error': str(e)}}

    def _extract_categories(self, content: str, filepath: str) -> List[str]:
        categories = set()
        path_parts = str(filepath).lower().split('/')
        for part in path_parts:
            if any(key in part for key in ['api', 'config', 'auth', 'docs', 'guide']):
                categories.add(part)

        content_lower = content.lower()
        if 'configuration' in content_lower or 'config' in content_lower:
            categories.add('configuration')
        if 'api' in content_lower:
            categories.add('api')
        if 'authentication' in content_lower or 'auth' in content_lower:
            categories.add('authentication')
        if 'jwt' in content_lower:
            categories.add('jwt')
        if 'database' in content_lower:
            categories.add('database')

        return list(categories)

    def _extract_key_concepts(self, content: str) -> Dict[str, List[str]]:
        concepts = {
            'services': [],
            'config_files': [],
            'endpoints': [],
            'dependencies': []
        }

        content_lower = content.lower()
        services = re.findall(r'(?:service|server)\s+([a-zA-Z0-9_-]+)', content_lower)
        concepts['services'].extend(services)

        config_files = re.findall(r'(?:config|configuration|env)\s+file\s+([a-zA-Z0-9_.-]+)', content_lower)
        concepts['config_files'].extend(config_files)

        endpoints = re.findall(r'(?:endpoint|api)\s+([a-zA-Z0-9_/.-]+)', content_lower)
        concepts['endpoints'].extend(endpoints)

        dependencies = re.findall(r'(?:requires|depends on|dependency)\s+([a-zA-Z0-9_-]+)', content_lower)
        concepts['dependencies'].extend(dependencies)

        return concepts

    def _process_env_file(self, content: str) -> Dict[str, Any]:
        env_vars = {}
        sensitive_vars = []
        for line in content.splitlines():
            if '=' in line and not line.startswith('#'):
                key = line.split('=')[0].strip()
                if any(sensitive in key.lower() for sensitive in ['secret', 'password', 'key', 'token']):
                    sensitive_vars.append(key)
                env_vars[key] = True
        return {
            'variables': list(env_vars.keys()),
            'sensitive_vars': sensitive_vars,
            'var_count': len(env_vars)
        }

    def _process_config_file(self, content: str, file_type: str) -> Dict[str, Any]:
        try:
            if file_type in ['.yml', '.yaml']:
                import yaml
                data = yaml.safe_load(content)
            elif file_type == '.json':
                import json
                data = json.loads(content)
            else:
                return {}

            if isinstance(data, dict):
                return {
                    'config_keys': list(data.keys()),
                    'has_nested': any(isinstance(v, dict) for v in data.values())
                }
            return {}
        except Exception:
            return {}

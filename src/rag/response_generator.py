import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ResponseGenerator:
    def __init__(self):
        self.command_pattern = r'```bash\n(.*?)```'

    def format_response(self, response: str) -> str:
        try:
            # Extract commands if present
            commands = re.findall(self.command_pattern, response, re.DOTALL)
            
            # If no commands found, return the original response
            if not commands:
                return response
                
            # Format response with highlighted commands
            formatted_response = response
            for cmd in commands:
                formatted_cmd = f"```bash\n{cmd.strip()}\n```"
                if formatted_cmd not in formatted_response:
                    formatted_response += f"\n\nCommand to execute:\n{formatted_cmd}"
                    
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return response

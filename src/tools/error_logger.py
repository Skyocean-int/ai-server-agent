import logging
from typing import Optional
from datetime import datetime

class ErrorLogger:
    def __init__(self):
        self.logger = logging.getLogger("ai_agent")
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        fh = logging.FileHandler('/var/log/ai-agent/error.log')
        fh.setLevel(logging.ERROR)
        fh.setFormatter(formatter)
        
        # Stream handler
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)

    async def log_error(self, context: str, error: Exception) -> str:
        """Log error and return formatted message"""
        error_msg = f"{context}: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        return f"Error processing request: {error_msg}"

    async def log_tool_usage(self, tool_name: str, input_str: str, 
                           success: bool, result: Optional[str] = None):
        """Log tool usage"""
        msg = (
            f"Tool: {tool_name}\n"
            f"Input: {input_str}\n"
            f"Success: {success}\n"
        )
        if result:
            msg += f"Result: {result[:200]}..."  # Truncate long results
            
        if success:
            self.logger.info(msg)
        else:
            self.logger.error(msg)

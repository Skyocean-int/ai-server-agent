import sys
import logging
import asyncio
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr

from src.core.query_handler import QueryHandler
from src.tools.file_cache_service import file_reader

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ChatInterface:
    def __init__(self):
        self.handler = None
        self.lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self):
        """Initialize the chat interface and connections."""
        if self._initialized:
            return

        async with self.lock:
            if not self._initialized:
                try:
                    # Initialize connections
                    await file_reader.initialize()
                    self.handler = QueryHandler()
                    self._initialized = True
                    logger.info("Chat interface initialized")
                except Exception as e:
                    logger.error(f"Initialization error: {str(e)}", exc_info=True)
                    raise

    async def chat(self, message: str, history=None):
        """Handle chat messages."""
        try:
            if not self._initialized:
                await self.initialize()
            
            response = await self.handler.process_query(message)
            if history is None:
                history = []
            return "", history + [(message, response)]
        except Exception as e:
            logger.error(f"Chat error: {str(e)}", exc_info=True)
            return "", history + [(message, f"Error: {str(e)}")]

    async def cleanup(self):
        """Cleanup connections on shutdown."""
        try:
            if hasattr(self, 'file_reader'):
                await self.file_reader.close()
                await asyncio.sleep(1)  # Give connections time to close
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

def create_app():
    # Create FastAPI app
    app = FastAPI()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    interface = ChatInterface()
    
    # Use FastAPI lifespan instead of @app.on_event
    @app.on_event("shutdown")
    async def shutdown_event():
        await interface.cleanup()
    
    with gr.Blocks(title="AI Agent - DKG Assistant") as demo:
        gr.Markdown("# AI Agent - OriginTrail DKG Assistant")
        
        chatbot = gr.Chatbot(
            height=600,
            show_copy_button=True,
            latex_delimiters=[]
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="Ask about server configurations, files, or troubleshooting",
                placeholder="Type your question here...",
                scale=9
            )
            submit = gr.Button("Send", scale=1)
            clear = gr.ClearButton([msg, chatbot], scale=1)

        # Wire up the interface
        msg.submit(fn=interface.chat, inputs=[msg, chatbot], outputs=[msg, chatbot])
        submit.click(fn=interface.chat, inputs=[msg, chatbot], outputs=[msg, chatbot])

        # Initialize on load
        demo.load(lambda: asyncio.run(interface.initialize()))

    return gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    
    # Create and run app
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )

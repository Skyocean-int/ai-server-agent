import gradio as gr
from ai_agent.core.query_handler import QueryHandler

handler = QueryHandler()

async def process_query(message, history):
    response = await handler.process_query(message)
    return history + [(message, response)]

demo = gr.ChatInterface(
    fn=process_query,
    title="AI Server Management",
    description="Query your servers and configurations"
)

if __name__ == "__main__":
    demo.launch()

import logging

logger = logging.getLogger(__name__)

class SimpleIndexer:
    """
    Minimal doc search example.
    In reality, adapt to your vector store e.g., Pinecone, Chroma, FAISS, etc.
    We'll store some sample docs in a list for demonstration.
    """

    def __init__(self):
        # For example, a small list of doc paragraphs
        # In reality, load from your RAG vector store
        self.docs = [
            {"content": "OriginTrail DKG docs: Setting up a V8 core node ..."},
            {"content": "ERPNext docs: Configuration steps for production environment ..."},
            {"content": "When troubleshooting MySQL, ensure correct host, user, password in .env ..."},
            {"content": "API Service Configuration: To set up the API service, update the .env file with the necessary environment variables ..."},
            # Add more docs as needed
        ]

    def search(self, query: str):
        """
        Return doc chunks that match (very naive: if query is substring).
        In reality, do actual vector similarity search or advanced logic.
        """
        results = []
        q = query.lower()
        for doc in self.docs:
            if q in doc["content"].lower():
                results.append(doc)
        return results if results else []

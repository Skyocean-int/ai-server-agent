# AI Server Management Agent

A self-hosted AI agent for server management and troubleshooting that combines RAG (Retrieval Augmented Generation) with secure file access.

## Key Features

- Secure file reading with Redis caching
- RAG-based document retrieval with vector search
- Asynchronous operations
- SSH-based file access with security controls
- Web interface for easy interaction
- Comprehensive file search and analysis

## Architecture

The agent uses a layered architecture that separates concerns:

1. File Access Layer
   - Secure SSH connections
   - Redis caching
   - Path filtering and security controls

2. Knowledge Layer
   - FAISS vector store
   - Document processing
   - Similarity search

3. Intelligence Layer
   - Claude API integration
   - Context building
   - Response generation

4. Interface Layer
   - Gradio web UI
   - Async request handling
   - Session management

## Components

```plaintext
/src
├── core/           # Core agent logic and query handling
├── tools/          # File reading and caching services
├── knowledge_base/ # Vector store and document processing
├── rag/           # Retrieval and context generation
├── server_management/ # SSH and file operations
└── ui/            # Web interface
```

## Installation

1. System Requirements:
   - Python 3.10+
   - Redis server
   - SSH access to target servers

2. Setup:
   ```bash
   # Clone repository
   git clone [repository-url]

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Configure environment
   cp .env.example .env
   # Edit .env with your settings
   ```

## Configuration

Required environment variables:
- `ANTHROPIC_API_KEY`: Your Claude API key
- Server configurations (in .env):
  ```json
  SERVERS='[
    {
      "name": "server1",
      "ip": "xxx.xxx.xxx.xxx",
      "search_paths": ["/path1", "/path2"]
    }
  ]'
  ```

## Usage

1. Start Redis server:
   ```bash
   redis-server
   ```

2. Configure SSH keys:
   ```bash
   ssh-keygen -t ed25519
   ssh-copy-id user@server
   ```

3. Start the agent:
   ```bash
   python src/ui/app.py
   ```

4. Access web interface at http://localhost:7860

## Security Features

- No direct LLM access to servers
- File content cached in Redis
- SSH key-based authentication
- Configurable excluded paths
- Path filtering and validation
- Access logging and monitoring

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

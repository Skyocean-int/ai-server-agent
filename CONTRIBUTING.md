# Contributing to AI Server Management Agent

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Fork the Repository
   ```bash
   # Clone your fork
   git clone https://github.com/yourusername/ai-agent.git
   cd ai-agent
   
   # Add upstream remote
   git remote add upstream https://github.com/original/ai-agent.git
   ```

2. Environment Setup
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest pytest-asyncio pytest-cov black flake8
   ```

3. Configure Development Environment
   - Copy .env.example to .env
   - Add required API keys and test server configurations

## Development Guidelines

### Code Style
- Follow PEP 8 standards
- Use type hints for function parameters and return values
- Include docstrings for all modules, classes, and functions
- Use async/await consistently for asynchronous code
- Maximum line length of 100 characters

### Testing
- Write unit tests for new features using pytest
- Maintain or improve test coverage
- Run tests before submitting:
  ```bash
  pytest tests/
  ```

### Pull Request Process
1. Create a new branch for your feature
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes:
   - Write clear, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. Before Submitting:
   - Run code formatting:
     ```bash
     black src/ tests/
     ```
   - Run linting:
     ```bash
     flake8 src/ tests/
     ```
   - Run tests:
     ```bash
     pytest tests/ --cov=src/
     ```

4. Submit PR:
   - Clear description of changes
   - Reference any related issues
   - Include test results
   - Document any new dependencies

## Project Structure

```plaintext
.
├── src/                    # Source code
│   ├── core/              # Core agent logic
│   ├── tools/             # Utility tools
│   ├── knowledge_base/    # Vector store and document processing
│   ├── rag/               # Retrieval and context generation
│   ├── server_management/ # Server operations
│   └── ui/                # Web interface
├── tests/                 # Test files
├── docs/                  # Documentation
└── examples/              # Example usage
```

### Key Components

1. Core Components (`src/core/`):
   - Agent initialization and management
   - Query processing
   - Response generation

2. Tools (`src/tools/`):
   - File reading and caching
   - SSH operations
   - Security controls

3. Knowledge Base (`src/knowledge_base/`):
   - Vector store implementation
   - Document processing
   - Embedding generation

4. RAG Implementation (`src/rag/`):
   - Context retrieval
   - Response enhancement
   - Query processing

## Creating Issues

When creating issues, please:
1. Use issue templates if available
2. Include detailed reproduction steps
3. Specify your environment:
   - Python version
   - Operating system
   - Dependency versions
4. Include relevant logs or error messages

## Documentation

- Update documentation for new features
- Include docstrings in code
- Update README.md if needed
- Provide examples for new functionality

## Questions?

Feel free to:
- Open an issue for questions
- Join our community discussions
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

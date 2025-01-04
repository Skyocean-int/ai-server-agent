#!/bin/bash

# Check Python version
if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10+ required"
    exit 1
fi

# Install Redis
if ! command -v redis-server &> /dev/null; then
    sudo apt update
    sudo apt install redis-server -y
fi

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/{vector_store,file_cache}

# Copy example config
cp .env.example .env

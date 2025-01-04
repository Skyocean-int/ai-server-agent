import os
from pathlib import Path
from dotenv import load_dotenv

def setup_config():
    load_dotenv()
    
    # Server config
    servers = [
        {
            "name": "webserver",
            "ip": "xxx.xxx.xxx.xxx",
            "search_paths": ["/etc/nginx", "/var/log"]
        }
    ]
    
    # Redis config
    redis_config = {
        "host": "localhost",
        "port": 6379,
        "db": 0
    }
    
    # Vector store config
    vector_config = {
        "path": str(Path.home() / "ai-agent" / "data" / "vector_store"),
        "dimension": 768
    }
    
    return {"servers": servers, "redis": redis_config, "vector": vector_config}

if __name__ == "__main__":
    config = setup_config()
    print("Configuration loaded:", config)

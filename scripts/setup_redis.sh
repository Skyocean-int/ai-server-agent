#!/bin/bash

# Configure Redis for vector storage
cat > /etc/redis/redis.conf << EOL
bind 127.0.0.1
port 6379
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
EOL

# Restart Redis
systemctl restart redis

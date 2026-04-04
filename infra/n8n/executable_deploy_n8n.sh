#!/bin/bash

echo "Deploying n8n..."
echo "Checking if n8n container is running..."
if docker ps | grep -q n8n; then
    echo "Stopping existing n8n container..."
    docker stop n8n
    sleep 2
fi

echo "Starting n8n..."
docker compose -f docker-compose.n8n.yml up -d

echo "Waiting for n8n to start..."
sleep 10

if docker ps | grep -q n8n; then
    echo "n8n started successfully!"
    echo "Server is running on http://localhost:5678"
else
    echo "Error: n8n failed to start"
    echo "Check the logs with: docker logs n8n"
    exit 1
fi

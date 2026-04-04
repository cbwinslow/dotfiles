#!/bin/bash

echo "Deploying Letta server..."
echo "Checking if Letta container is running..."
if docker ps | grep -q letta-server; then
    echo "Stopping existing Letta container..."
    docker stop letta-server
    sleep 2
fi

echo "Starting Letta server..."
docker-compose -f docker-compose.letta.yml up -d

echo "Waiting for Letta server to start..."
sleep 10

# Check if Letta is running
if docker ps | grep -q letta-server; then
    echo "Letta server started successfully!"
    echo "Server is running on http://localhost:8283"
    echo "You can now access the Letta dashboard and CLI tools"
else
    echo "Error: Letta server failed to start"
    echo "Check the logs with: docker logs letta-server"
    exit 1
fi

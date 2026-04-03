#!/usr/bin/env bash
# run_once_04-setup-docker-stacks.sh
# Prepare Docker networks and pull base images
set -euo pipefail

if ! command -v docker &>/dev/null; then
    echo "==> Docker not installed, skipping stack setup."
    exit 0
fi

echo "==> Setting up Docker environment..."

# Create shared networks
for network in proxy monitoring internal; do
    if ! docker network inspect "$network" &>/dev/null; then
        docker network create "$network"
        echo "==> Created network: $network"
    fi
done

# Pull commonly used images
IMAGES=(
    "traefik:v3.0"
    "postgres:16-alpine"
    "redis:7-alpine"
    "prom/prometheus:latest"
    "grafana/grafana:latest"
    "prom/node-exporter:latest"
)

for image in "${IMAGES[@]}"; do
    echo "==> Pulling $image..."
    docker pull "$image" || echo "==> WARNING: Failed to pull $image"
done

echo "==> Docker environment ready."

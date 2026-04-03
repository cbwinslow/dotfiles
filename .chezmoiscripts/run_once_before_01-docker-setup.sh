#!/usr/bin/env bash
# run_once_before_01-docker-setup.sh
# Install Docker Engine and Docker Compose
set -euo pipefail

if command -v docker &>/dev/null; then
    echo "==> Docker already installed: $(docker --version)"
    exit 0
fi

echo "==> Installing Docker..."

# Add Docker GPG key and repository
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -qq
sudo apt-get install -y -qq \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker "$USER"

echo "==> Docker installed: $(docker --version)"
echo "==> NOTE: Log out and back in for docker group membership to take effect."

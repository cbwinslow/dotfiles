#!/usr/bin/env bash
# run_once_before_00-system-packages.sh
# Install essential system packages before anything else
set -euo pipefail

echo "==> Installing system packages..."

# Update package lists
sudo apt-get update -qq

# Core utilities
sudo apt-get install -y -qq \
    git \
    curl \
    wget \
    htop \
    tmux \
    unzip \
    jq \
    tree \
    ncdu \
    iotop \
    build-essential \
    cmake \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https

# Development
sudo apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

# Database clients
sudo apt-get install -y -qq \
    postgresql-client \
    redis-tools

# Networking and security
sudo apt-get install -y -qq \
    nfs-common \
    cifs-utils \
    fail2ban \
    ufw \
    net-tools \
    dnsutils \
    traceroute

echo "==> System packages installed."

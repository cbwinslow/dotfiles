#!/usr/bin/env bash
# run_once_03-setup-git.sh
# Configure Git credentials and LFS
set -euo pipefail

echo "==> Configuring Git..."

# Set up credential helper if not already configured
if ! git config --global credential.helper &>/dev/null; then
    git config --global credential.helper store
fi

# Configure LFS if not present
if ! command -v git-lfs &>/dev/null; then
    echo "==> Installing Git LFS..."
    sudo apt-get install -y -qq git-lfs
    git lfs install
fi

# GitHub CLI auth (interactive - user must complete this)
if ! gh auth status &>/dev/null 2>&1; then
    echo "==> GitHub CLI not authenticated. Run: gh auth login"
fi

echo "==> Git setup complete."

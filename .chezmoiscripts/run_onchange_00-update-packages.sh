#!/usr/bin/env bash
# run_onchange_00-update-packages.sh
# Re-runs when the package list changes
set -euo pipefail

# This script re-runs when .chezmoidata.toml changes
# It updates system packages to match the declared list

echo "==> Updating system packages..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# Ensure declared packages are installed
PACKAGES=(
    git curl wget htop tmux unzip jq tree ncdu iotop
    build-essential cmake python3 python3-pip python3-venv python3-dev
    postgresql-client redis-tools nfs-common cifs-utils
    fail2ban ufw net-tools dnsutils traceroute git-lfs
)

for pkg in "${PACKAGES[@]}"; do
    if ! dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
        echo "==> Installing missing package: $pkg"
        sudo apt-get install -y -qq "$pkg"
    fi
done

echo "==> Package update complete."

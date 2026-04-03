#!/bin/bash
# Set up Bitwarden CLI integration
# This runs once on new machine setup

if command -v bw &> /dev/null; then
    echo "Bitwarden CLI found, setting up integration..."
    
    # Check if already logged in
    if ! bw status 2>/dev/null | grep -q '"status":"unlocked"'; then
        echo "Please run: bw login"
        echo "Then run: bw sync"
    fi
    
    # Create Bitwarden environment
    mkdir -p ~/.config/bitwarden
    echo "Bitwarden CLI integration ready"
else
    echo "Bitwarden CLI not found, installing..."
    if command -v snap &> /dev/null; then
        snap install bw
    elif command -v npm &> /dev/null; then
        npm install -g @bitwarden/cli
    fi
fi

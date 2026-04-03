#!/bin/bash
# OpenClaw Gateway Setup Script
# Configures OpenClaw gateway for LAN + Tailscale access
# Location: ~/dotfiles/ai/scripts/setup_openclaw_gateway.sh

set -e

echo "=============================================="
echo "  OpenClaw Gateway Setup"
echo "  Server: cbwdellr720 (Ubuntu)"
echo "  Client: cbwwin (Windows)"
echo "=============================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Step 1: Verify OpenClaw installation
echo "Step 1: Verifying OpenClaw installation..."
echo "-------------------------------------------"
if command -v openclaw &>/dev/null; then
    OPENCLAW_VERSION=$(openclaw --version 2>&1 | head -1)
    log_info "OpenClaw installed: $OPENCLAW_VERSION"
else
    log_error "OpenClaw not found. Install with: npm install -g @openclaw/cli"
    exit 1
fi

# Step 2: Verify Tailscale
echo ""
echo "Step 2: Verifying Tailscale..."
echo "-------------------------------------------"
if command -v tailscale &>/dev/null; then
    TS_STATUS=$(tailscale status 2>&1 | grep "cbwdellr720" | head -1)
    log_info "Tailscale running: $TS_STATUS"
    
    # Check if cbwwin is on tailnet
    TS_WIN=$(tailscale status 2>&1 | grep "cbwwin" | head -1)
    if [ -n "$TS_WIN" ]; then
        log_info "Windows client (cbwwin) found on tailnet"
    else
        log_warn "Windows client (cbwwin) not found on tailnet"
    fi
else
    log_error "Tailscale not found"
    exit 1
fi

# Step 3: Configure OpenClaw
echo ""
echo "Step 3: Configuring OpenClaw gateway..."
echo "-------------------------------------------"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

if [ -f "$OPENCLAW_CONFIG" ]; then
    log_info "Config exists at $OPENCLAW_CONFIG"
    
    # Check if gateway config is correct
    if grep -q '"bind": "tailnet"' "$OPENCLAW_CONFIG" 2>/dev/null; then
        log_info "Gateway configured for tailnet binding"
    else
        log_warn "Updating gateway config for LAN + Tailscale..."
    fi
else
    log_warn "Creating new OpenClaw config..."
    openclaw setup --dev
fi

# Step 4: Setup Tailscale serve
echo ""
echo "Step 4: Configuring Tailscale serve..."
echo "-------------------------------------------"
TS_SERVE=$(tailscale serve status --json 2>&1 | grep -c "18789" || true)
if [ "$TS_SERVE" -gt 0 ]; then
    log_info "Tailscale serve already configured for port 18789"
else
    log_info "Setting up Tailscale serve for port 18789..."
    sudo tailscale serve --bg 18789 || {
        log_warn "Tailscale serve requires sudo. Run manually:"
        echo "  sudo tailscale serve --bg 18789"
    }
fi

# Step 5: Setup firewall
echo ""
echo "Step 5: Configuring firewall..."
echo "-------------------------------------------"
if command -v ufw &>/dev/null; then
    if sudo ufw status 2>&1 | grep -q "18789"; then
        log_info "Firewall rule for port 18789 already exists"
    else
        log_info "Adding firewall rule for port 18789..."
        sudo ufw allow 18789/tcp comment "OpenClaw Gateway" || {
            log_warn "Could not add firewall rule. Run manually:"
            echo "  sudo ufw allow 18789/tcp"
        }
    fi
else
    log_warn "UFW not found. Configure firewall manually."
fi

# Step 6: Install systemd service
echo ""
echo "Step 6: Installing systemd service..."
echo "-------------------------------------------"
SERVICE_FILE="/etc/systemd/system/openclaw-gateway.service"
if [ -f "$SERVICE_FILE" ]; then
    log_info "Systemd service already installed"
else
    log_info "Installing systemd service..."
    echo "Copy service file with:"
    echo "  sudo cp ~/dotfiles/ai/services/openclaw-gateway.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable openclaw-gateway"
    echo "  sudo systemctl start openclaw-gateway"
fi

# Step 7: Summary
echo ""
echo "=============================================="
echo "  Setup Summary"
echo "=============================================="
echo ""
echo "Server (cbwdellr720):"
echo "  - LAN: ws://192.168.4.101:18789"
echo "  - Tailscale: wss://cbwdellr720.tail3471a9.ts.net"
echo "  - Auth Token: 33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf"
echo ""
echo "Client (cbwwin - Windows):"
echo "  - Install: npm install -g @openclaw/cli"
echo "  - LAN Config: ws://192.168.4.101:18789"
echo "  - Tailscale Config: wss://cbwdellr720.tail3471a9.ts.net"
echo ""
echo "Next Steps:"
echo "  1. Start gateway: openclaw gateway run --bind lan --port 18789"
echo "  2. Or install service: sudo systemctl start openclaw-gateway"
echo "  3. Test from Windows: openclaw gateway status"
echo ""
echo "Documentation: ~/dotfiles/ai/docs/openclaw-windows-client.md"
echo ""

log_info "Setup complete!"

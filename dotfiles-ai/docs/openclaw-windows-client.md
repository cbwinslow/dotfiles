# OpenClaw Windows Client Configuration
# For: cbwwin (Windows machine)
# Server: cbwdellr720 (Ubuntu homelab)

## Connection Details

### LAN Connection (Local Network)
- **Host**: `cbwdellr720` or `192.168.4.101`
- **Port**: `18789`
- **WebSocket URL**: `ws://192.168.4.101:18789`
- **Auth Token**: `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf`

### Tailscale Connection (Remote)
- **Host**: `cbwdellr720.tail3471a9.ts.net`
- **Port**: `443` (HTTPS)
- **WebSocket URL**: `wss://cbwdellr720.tail3471a9.ts.net`
- **Auth Token**: `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf`
- **Tailscale IP**: `100.67.203.99`

## Setup on Windows (cbwwin)

### 1. Install OpenClaw CLI on Windows

```powershell
# In PowerShell (Admin)
npm install -g @openclaw/cli
```

### 2. Configure OpenClaw for LAN Access

```powershell
# Create config directory
mkdir -p ~/.openclaw

# Create config for LAN access
cat > ~/.openclaw/openclaw.json << 'EOF'
{
  "gateway": {
    "mode": "remote",
    "url": "ws://192.168.4.101:18789",
    "auth": {
      "mode": "token",
      "token": "33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf"
    }
  }
}
EOF
```

### 3. Configure OpenClaw for Tailscale Access

```powershell
# Create config for Tailscale access
cat > ~/.openclaw/openclaw-tailscale.json << 'EOF'
{
  "gateway": {
    "mode": "remote",
    "url": "wss://cbwdellr720.tail3471a9.ts.net",
    "auth": {
      "mode": "token",
      "token": "33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf"
    }
  }
}
EOF

# Use with --profile flag
openclaw --profile tailscale gateway status
```

### 4. Test Connection

```powershell
# Test LAN connection
openclaw gateway status

# Test Tailscale connection
openclaw --profile tailscale gateway status

# Run an agent command
openclaw agent --message "Hello from Windows"
```

## Firewall Rules (Ubuntu - cbwdellr720)

If connection fails, add firewall rule on Ubuntu:

```bash
# Allow OpenClaw gateway port
sudo ufw allow 18789/tcp comment "OpenClaw Gateway LAN"

# Check status
sudo ufw status
```

## Tailscale Verification

Ensure Tailscale is running on both machines:

```powershell
# On Windows (PowerShell)
tailscale status

# Should show cbwdellr720 as connected
```

## Quick Reference

| Scenario | Command |
|----------|---------|
| LAN - Check status | `openclaw gateway status` |
| Tailscale - Check status | `openclaw --profile tailscale gateway status` |
| LAN - Run agent | `openclaw agent --message "task"` |
| Tailscale - Run agent | `openclaw --profile tailscale agent --message "task"` |
| View logs | `openclaw logs` |

## Troubleshooting

### Can't connect via LAN
1. Check Ubuntu firewall: `sudo ufw status`
2. Verify server is running: `systemctl status openclaw-gateway`
3. Test from Windows: `Test-NetConnection 192.168.4.101 -Port 18789`

### Can't connect via Tailscale
1. Check Tailscale status: `tailscale status`
2. Verify serve config: `tailscale serve status`
3. Restart Tailscale: `tailscale down && tailscale up`

### Auth errors
- Verify token matches in both configs
- Token: `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf`

# OpenClaw Gateway Setup Summary

**Server**: cbwdellr720 (Ubuntu homelab)
**Client**: cbwwin (Windows machine)
**Date**: 2026-03-24

---

## Connection Details

### LAN (Local Network)
| Setting | Value |
|---------|-------|
| Hostname | `cbwdellr720` |
| IP Address | `192.168.4.101` |
| Port | `18789` |
| WebSocket URL | `ws://192.168.4.101:18789` |
| Dashboard | `http://192.168.4.101:18789/` |
| Auth Token | `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf` |

### Tailscale (Remote)
| Setting | Value |
|---------|-------|
| Hostname | `cbwdellr720.tail3471a9.ts.net` |
| Tailscale IP | `100.67.203.99` |
| Port | `443` (HTTPS) |
| WebSocket URL | `wss://cbwdellr720.tail3471a9.ts.net` |
| Auth Token | `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf` |

---

## Server Status (cbwdellr720)

### OpenClaw Gateway
```bash
# Check status
openclaw gateway status

# Start gateway (foreground)
openclaw gateway run --bind lan --port 18789

# Start as service
systemctl --user start openclaw-gateway

# View logs
openclaw logs
```

### Tailscale Serve
```bash
# Check status
tailscale serve status

# Already configured:
# - Port 18789 forwarded to 127.0.0.1:18789
# - Funnel enabled for HTTPS access
```

### Firewall
```bash
# Check status
sudo ufw status

# Port 18789 is allowed for LAN access
```

---

## Windows Client Setup (cbwwin)

### 1. Install OpenClaw on Windows

Open PowerShell as Administrator:
```powershell
npm install -g @openclaw/cli
```

### 2. Configure for LAN Access

Create `~/.openclaw/openclaw.json`:
```json
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
```

### 3. Configure for Tailscale Access

Create `~/.openclaw/openclaw-tailscale.json`:
```json
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
```

Use with: `openclaw --profile tailscale`

### 4. Test Connection

```powershell
# Test LAN
openclaw gateway status

# Test Tailscale
openclaw --profile tailscale gateway status

# Run an agent
openclaw agent --message "Hello from Windows"
```

---

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  cbwwin         │         │  cbwwin          │
│  (Windows)      │         │  (Windows)       │
│                 │         │                  │
│  LAN Access     │         │  Tailscale       │
│  192.168.4.x    │         │  Remote          │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │ ws://192.168.4.101:18789  │ wss://cbwdellr720.tail3471a9.ts.net:443
         │                           │
         └──────────────┬────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  cbwdellr720    │
              │  (Ubuntu)       │
              │  192.168.4.101  │
              │  100.67.203.99  │
              │                 │
              │  OpenClaw       │
              │  Gateway :18789 │
              └─────────────────┘
```

---

## Quick Reference

### From Windows (cbwwin)

```powershell
# LAN - Check status
openclaw gateway status

# Tailscale - Check status
openclaw --profile tailscale gateway status

# LAN - Run agent task
openclaw agent --message "Summarize my workspace"

# Tailscale - Run agent task
openclaw --profile tailscale agent --message "Summarize my workspace"

# View logs
openclaw logs
```

### From Server (cbwdellr720)

```bash
# Check gateway status
openclaw gateway status

# Check Tailscale
tailscale serve status

# Restart gateway
systemctl --user restart openclaw-gateway

# View logs
openclaw logs
```

---

## Troubleshooting

### Can't connect via LAN from Windows

1. **Check server is running**:
   ```bash
   openclaw gateway status
   ```

2. **Test connectivity from Windows**:
   ```powershell
   Test-NetConnection 192.168.4.101 -Port 18789
   ```

3. **Check firewall on Ubuntu**:
   ```bash
   sudo ufw status
   ```

### Can't connect via Tailscale

1. **Check Tailscale on Windows**:
   ```powershell
   tailscale status
   ```

2. **Verify cbwdellr720 is visible**:
   ```powershell
   tailscale status | grep cbwdellr720
   ```

3. **Check serve config on Ubuntu**:
   ```bash
   tailscale serve status
   ```

### Auth errors

- Verify token matches in both configs
- Token: `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf`

---

## Files Reference

| File | Purpose | Location |
|------|---------|----------|
| `openclaw.json` | Main config | `~/.openclaw/openclaw.json` |
| `openclaw-gateway.service` | Systemd service | `/etc/systemd/system/` |
| `openclaw-windows-client.md` | Windows setup guide | `~/dotfiles/ai/docs/` |
| `setup_openclaw_gateway.sh` | Setup script | `~/dotfiles/ai/scripts/` |

---

## Security Notes

1. **Auth Token**: Keep the gateway token secure
2. **LAN Access**: Only available on local network
3. **Tailscale Access**: Requires Tailscale authentication
4. **Firewall**: Port 18789 open for LAN only

---

## Next Steps

1. **Install systemd service** (optional, for auto-start):
   ```bash
   sudo cp ~/dotfiles/ai/services/openclaw-gateway.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable openclaw-gateway
   sudo systemctl start openclaw-gateway
   ```

2. **Setup Windows client** - Follow the Windows setup steps above

3. **Test from Windows**:
   ```powershell
   openclaw gateway status
   ```

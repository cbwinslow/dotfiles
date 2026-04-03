# OpenClaw Windows Client Setup - AI Agent Instructions

**Target Machine**: cbwwin (Windows)
**Server**: cbwdellr720 (Ubuntu homelab at 192.168.4.101)
**Date**: 2026-03-24
**Server Status**: ✅ Gateway is RUNNING

---

## Server Status (VERIFIED)

The OpenClaw gateway on cbwdellr720 is currently:
- **Status**: ✅ Running (PID 1344095)
- **Service**: systemd (enabled)
- **Binding**: 0.0.0.0:18789 (all interfaces)
- **Auth Mode**: Token-based (no pairing required for token holders)
- **Tailscale Serve**: Configured and forwarding to localhost:18789
- **Dashboard**: http://192.168.4.101:18789/

**Auth Token**: `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf`

**The server is ready for connections from Windows using token authentication.**

---

## Task Overview

Set up OpenClaw CLI on this Windows machine to connect to the OpenClaw gateway running on the Ubuntu homelab server (cbwdellr720). Configure both LAN and Tailscale remote access.

---

## Server Details

### LAN Connection (Local Network)
- **Hostname**: `cbwdellr720`
- **IP Address**: `192.168.4.101`
- **Port**: `18789`
- **WebSocket URL**: `ws://192.168.4.101:18789`
- **Auth Token**: `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf`

### Tailscale Connection (Remote)
- **Hostname**: `cbwdellr720.tail3471a9.ts.net`
- **Tailscale IP**: `100.67.203.99`
- **Port**: `443` (HTTPS)
- **WebSocket URL**: `wss://cbwdellr720.tail3471a9.ts.net`
- **Auth Token**: `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf`

---

## Step-by-Step Instructions

### Step 1: Verify Prerequisites

Check if Node.js is installed:
```powershell
node --version
npm --version
```

If not installed, download and install from: https://nodejs.org/

Check if Tailscale is installed:
```powershell
tailscale version
```

If not installed, download from: https://tailscale.com/download

Ensure Tailscale is running and connected:
```powershell
tailscale status
```

You should see `cbwdellr720` in the list of devices on your tailnet.

### Step 2: Install OpenClaw CLI

Open PowerShell as Administrator and run:
```powershell
npm install -g @openclaw/cli
```

Verify installation:
```powershell
openclaw --version
```

Expected output: `OpenClaw 2026.3.13` (or similar version)

### Step 3: Create OpenClaw Configuration Directory

```powershell
# Create the config directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw"
```

### Step 4: Create LAN Configuration

Create the main configuration file for LAN access:

```powershell
$lanConfig = @{
    gateway = @{
        mode = "remote"
        url = "ws://192.168.4.101:18789"
        auth = @{
            mode = "token"
            token = "33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf"
        }
    }
} | ConvertTo-Json -Depth 10

$lanConfig | Out-File -FilePath "$env:USERPROFILE\.openclaw\openclaw.json" -Encoding utf8
```

### Step 5: Create Tailscale Configuration Profile

Create a separate config file for Tailscale remote access:

```powershell
$tailscaleConfig = @{
    gateway = @{
        mode = "remote"
        url = "wss://cbwdellr720.tail3471a9.ts.net"
        auth = @{
            mode = "token"
            token = "33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf"
        }
    }
} | ConvertTo-Json -Depth 10

$tailscaleConfig | Out-File -FilePath "$env:USERPROFILE\.openclaw\openclaw-tailscale.json" -Encoding utf8
```

### Step 6: Test LAN Connection

Test the connection to the gateway on LAN:

```powershell
openclaw gateway status
```

**Expected output:**
```
Service: systemd (enabled)
Runtime: running
RPC probe: ok
Listening: *:18789
```

If you see "Gateway unreachable" or connection errors, tell the user:
- "The OpenClaw gateway on cbwdellr720 is not accessible. Please check:"
- "1. Server status: `openclaw gateway status` on cbwdellr720"
- "2. Firewall: Port 18789 must be open"
- "3. Network: Windows must be on same LAN as 192.168.4.101"

### Step 7: Test Tailscale Connection

Test the connection via Tailscale:

```powershell
openclaw --profile tailscale gateway status
```

Expected output should show:
- Gateway is reachable via Tailscale
- Connection successful
- No authentication errors

### Step 8: Test Agent Functionality

Run a test agent command:

```powershell
# Via LAN
openclaw agent --message "Hello from Windows. Please confirm you can see this message."

# Via Tailscale
openclaw --profile tailscale agent --message "Hello via Tailscale. Please confirm connection."
```

### Step 9: Create Shell Aliases (Optional)

Create PowerShell profile aliases for easier access:

```powershell
# Open PowerShell profile
notepad $PROFILE

# Add these lines:
function Invoke-OpenClaw { openclaw @args }
function Invoke-OpenClawTailscale { openclaw --profile tailscale @args }
Set-Alias oc Invoke-OpenClaw
Set-Alias oct Invoke-OpenClawTailscale
```

Then reload the profile:
```powershell
. $PROFILE
```

### Step 10: Verify Setup

Run these verification commands:

```powershell
# Check OpenClaw version
openclaw --version

# Check LAN connectivity
Test-NetConnection 192.168.4.101 -Port 18789

# Check Tailscale connectivity
tailscale ping cbwdellr720

# Check gateway status (LAN)
openclaw gateway status

# Check gateway status (Tailscale)
openclaw --profile tailscale gateway status

# List available commands
openclaw --help
```

---

## Expected Results

### Success Indicators
- ✅ `openclaw --version` returns version number
- ✅ `openclaw gateway status` shows connected status
- ✅ `openclaw --profile tailscale gateway status` shows connected status
- ✅ Agent commands execute successfully
- ✅ No authentication errors

### Common Issues and Solutions

#### Issue: "Gateway unreachable"
**Solution**: 
1. Verify server is running: Check with server admin
2. Check LAN connectivity: `Test-NetConnection 192.168.4.101 -Port 18789`
3. Verify Tailscale is running: `tailscale status`

#### Issue: "Authentication failed"
**Solution**:
1. Verify token in config matches: `33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf`
2. Check config file syntax: `cat $env:USERPROFILE\.openclaw\openclaw.json`

#### Issue: "Tailscale not connected"
**Solution**:
1. Start Tailscale: `tailscale up`
2. Verify connection: `tailscale status`
3. Ensure cbwdellr720 is visible in tailnet

---

## Configuration Files Created

| File | Purpose |
|------|---------|
| `$env:USERPROFILE\.openclaw\openclaw.json` | Default LAN config |
| `$env:USERPROFILE\.openclaw\openclaw-tailscale.json` | Tailscale profile config |

---

## Quick Reference Commands

```powershell
# Check gateway status (LAN)
openclaw gateway status

# Check gateway status (Tailscale)
openclaw --profile tailscale gateway status

# Run an agent task (LAN)
openclaw agent --message "Your task here"

# Run an agent task (Tailscale)
openclaw --profile tailscale agent --message "Your task here"

# View logs
openclaw logs

# Show help
openclaw --help
```

---

## Security Notes

1. **Auth Token**: The gateway token (`33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf`) is required for all connections
2. **LAN Access**: Only works when on the same local network as cbwdellr720
3. **Tailscale Access**: Works from anywhere with Tailscale connection
4. **Config Files**: Store sensitive tokens - protect accordingly

---

## Documentation References

- Server setup guide: `\\cbwdellr720\share\docs\openclaw-gateway-setup.md` (if shared)
- Local docs: After setup, see `openclaw docs` command
- Online docs: https://docs.openclaw.ai/cli/

---

## Completion Checklist

- [ ] Node.js installed
- [ ] Tailscale installed and running
- [ ] OpenClaw CLI installed
- [ ] LAN configuration created
- [ ] Tailscale configuration created
- [ ] LAN connection tested successfully
- [ ] Tailscale connection tested successfully
- [ ] Agent command tested successfully
- [ ] Shell aliases configured (optional)

---

**End of Instructions**

If you encounter any issues not covered here, check the server documentation or contact the server administrator.

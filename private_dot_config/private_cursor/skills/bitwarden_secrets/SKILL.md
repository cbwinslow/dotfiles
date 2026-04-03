---
name: bitwarden-secrets
version: "1.0.0"
description: "Securely retrieve API keys, passwords, and secrets from Bitwarden vault for use in AI agent workflows"
category: security
agents: [claude, cline, codex, windsurf, kilocode, opencode]
tags: [bitwarden, secrets, api-keys, security, mcp]
triggers:
  - API_KEY_NEEDED
  - SECRET_REQUESTED
  - PASSWORD_REQUIRED
---

# 🔐 Bitwarden Secrets Management Skill

Securely retrieve API keys and secrets from Bitwarden for AI agents and development workflows.

## Security Model

**Zero-Knowledge by Design**: This skill never stores vault contents. All operations:
- Use the official Bitwarden CLI (`bw`)
- Require an unlocked vault session (`BW_SESSION`)
- Return secrets only to the requesting agent/process
- Leave no trace after execution (except explicit exports you create)

## Configuration

### Prerequisites

1. **Bitwarden Account** with secrets organized
2. **Bitwarden CLI** (`bw`) installed and authenticated
3. **MCP Server** configured for your agent

### Setup Steps

#### 1. Install Bitwarden CLI
```bash
# Ubuntu/Debian
sudo snap install bw

# Or download from: https://bitwarden.com/download/
```

#### 2. Login to Bitwarden
```bash
# Login (one-time setup)
bw login username@example.com

# Set session key
export BW_SESSION=$(bw unlock --raw)
```

#### 3. Organize Secrets for AI Access

Create items in Bitwarden with standardized naming:

```
📁 API Keys
  ├── OPENAI_API_KEY - Production OpenAI key
  ├── ANTHROPIC_API_KEY - Claude API key  
  ├── STRIPE_TEST_KEY - Stripe test environment
  └── STRIPE_LIVE_KEY - Stripe production (labeled carefully)

📁 Database Credentials
  ├── PROD_POSTGRES_URI - Production database
  ├── DEV_POSTGRES_URI - Development database
  └── REDIS_URI - Redis connection string

📁 External Services
  ├── GITHUB_TOKEN - GitHub personal access token
  ├── DOCKER_HUB_TOKEN - Docker Hub auth
  └── NPM_TOKEN - NPM publishing token
```

## MCP Server Configuration

### For Windsurf (windsurf/mcp_config.json)

```json
{
  "mcpServers": {
    "bitwarden": {
      "command": "npx",
      "args": ["-y", "@bitwarden/mcp-server"],
      "env": {
        "BITWARDEN_CLIENT_ID": "${BITWARDEN_CLIENT_ID}",
        "BITWARDEN_CLIENT_SECRET": "${BITWARDEN_CLIENT_SECRET}",
        "BITWARDEN_MASTER_PASSWORD": "${BITWARDEN_MASTER_PASSWORD}"
      }
    }
  }
}
```

### For Cline (cline_mcp_settings.json)

```json
{
  "mcpServers": {
    "bitwarden": {
      "command": "npx",
      "args": ["-y", "@bitwarden/mcp-server"],
      "env": {
        "BITWARDEN_CLIENT_ID": "your-client-id",
        "BITWARDEN_CLIENT_SECRET": "your-client-secret",
        "BITWARDEN_MASTER_PASSWORD": "your-master-password"
      }
    }
  }
}
```

### For Claude Code (claude_mcp_config.json)

```json
{
  "mcpServers": {
    "bitwarden": {
      "command": "npx",
      "args": ["-y", "@bitwarden/mcp-server"]
    }
  }
}
```

## Quick Start

### 1. Ensure Bitwarden CLI is installed

```bash
bw --version  # Should show version 2024.x or later
```

### 2. Unlock your vault

```bash
export BW_SESSION=$(bw unlock --raw)
```

### 3. Use the skill in Python

```python
from bitwarden_secrets import BitwardenSecrets

bw = BitwardenSecrets()
api_key = bw.get_api_key("openrouter")
print(f"Key retrieved: {api_key[:8]}...")
```

### 4. Or use shell functions

```bash
source ~/dotfiles/ai/skills/bitwarden_secrets/shell_loader.sh
bw_get_key OPENROUTER_API_KEY
```

## JSON Export (Bulk API Key Access)

Export all API keys at once as JSON for easy access and filtering.

### Commands

```bash
# Export structured JSON with metadata
python3 ~/dotfiles/ai/skills/bitwarden_secrets/bitwarden_secrets.py export > api_keys.json

# Export flat dictionary format
python3 ~/dotfiles/ai/skills/bitwarden_secrets/bitwarden_secrets.py export-flat > api_keys_flat.json

# Export as shell export commands
python3 ~/dotfiles/ai/skills/bitwarden_secrets/bitwarden_secrets.py export-env > env_exports.sh
```

### Output Formats

**Structured JSON (`export`):**
```json
{
  "export_date": "2025-03-28T18:46:00+00:00",
  "total_items": 15,
  "total_keys": 42,
  "api_keys": [
    {
      "item_name": "CBW - Dell R720 (Ubuntu Server)",
      "item_id": "xxx",
      "keys": [
        {
          "field_name": "OPENROUTER_API_KEY",
          "value": "sk-or-v1-...",
          "type": "custom_field",
          "hidden": true
        }
      ]
    }
  ]
}
```

**Flat Dictionary (`export-flat`):**
```json
{
  "OPENROUTER_API_KEY": "sk-or-v1-...",
  "OPENAI_API_KEY": "sk-...",
  "ANTHROPIC_API_KEY": "sk-ant-..."
}
```

### Using Exported Keys

**In Python:**
```python
import json

# Load flat dictionary
keys = json.load(open('api_keys_flat.json'))
openrouter_key = keys.get('OPENROUTER_API_KEY')
```

**In Shell:**
```bash
# Source the exports
source env_exports.sh

# Or use jq to get specific key
OPENROUTER_KEY=$(jq -r '.OPENROUTER_API_KEY' api_keys_flat.json)
```

**In AI Agent Code Generation:**
```python
import json

# Agent loads keys from exported JSON
with open('api_keys_flat.json') as f:
    keys = json.load(f)

# Use in generated code
api_key = keys.get('OPENROUTER_API_KEY', 'YOUR_KEY_HERE')
```

## Common Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `bw status` | Check login/lock status | Verify vault accessibility |
| `bw unlock --raw` | Unlock vault, return session key | Set `BW_SESSION` env var |
| `bw lock` | Lock vault | End session securely |
| `bw sync` | Sync vault with server | Get latest items |
| `bw list items` | List all vault items | Browse available secrets |
| `bw list items --search <query>` | Search for specific items | Find API keys by name |
| `python3 bitwarden_secrets.py get-key <NAME>` | Get specific API key | Direct key retrieval |
| `python3 bitwarden_secrets.py export-env` | Export all keys as .env | Environment setup |
| `bw_get_key <NAME>` | Shell function for single key | Quick CLI access |
| `bw_export_env [file]` | Shell function for .env export | Batch environment setup |

## Guardrails

- **Never paste secrets** into logs, chat, or code repositories.
- **Always verify vault is unlocked** before requesting secrets.
- **Use `bw_get_key` for single keys** instead of bulk export when possible.
- **Lock vault when done**: Run `bw lock` to end the session.
- **Secure exported files**: If creating `.env` files, set permissions with `chmod 600`.
- **Never commit `.env` files** to version control.
- **Prefer custom fields** over passwords for API keys (better organization).
- **Verify key name patterns** match expected format (e.g., `PROVIDER_API_KEY`).

## Troubleshooting

**Issue: "Vault is locked"**
```bash
# Solution: Unlock vault and set session
export BW_SESSION=$(bw unlock --raw)
```

**Issue: "Secret not found"**
```bash
# Check exact name
bw list items | jq '.[].name'

# Search for partial match
bw list items --search "OpenAI"
```

**Issue: "bw command not found"**
```bash
# Install Bitwarden CLI
sudo snap install bw

# Or
npm install -g @bitwarden/cli
```

## Security Checklist

- [ ] Vault uses strong master password
- [ ] Two-factor authentication enabled
- [ ] Secrets organized with clear naming
- [ ] Production keys have reprompt enabled
- [ ] Regular vault backups
- [ ] Emergency access configured
- [ ] Bitwarden CLI version kept updated
- [ ] Session keys never committed to git
- [ ] `.env` files in `.gitignore`
- [ ] Secrets never appear in shell history

## Related Skills

- `env-manager` - Environment variable management
- `secret-generator` - Generate secure passwords
- `vault-backup` - Backup Bitwarden vault

---

**Skill Version**: 1.0.0  
**Requires**: Bitwarden CLI (`bw`), MCP server access  
**Compatible With**: All agents with MCP support

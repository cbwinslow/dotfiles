# Bitwarden Secrets Skill
# Secure credential management for AI agents
# Location: ~/dotfiles/ai/skills/bitwarden/SKILL.md

name: bitwarden_secrets
description: "Secure access to Bitwarden vault for API keys, passwords, and credentials"
version: 2.0.0

## Overview

This skill provides AI agents with secure access to Bitwarden credentials. It:
- Retrieves API keys, passwords, and secrets from Bitwarden vault
- Populates .env files with credentials from Bitwarden
- Manages vault sessions with secure storage
- Guides users through vault unlock (including 2FA)
- Uses official Bitwarden MCP server when available

## Operations

### `unlock_vault`
Unlock the Bitwarden vault for credential access.

**Parameters:**
- `password` (string): Bitwarden master password
- `totp` (string, optional): 2FA code if enabled

**Returns:** Success status and session token

**Example:**
```python
bitwarden.unlock_vault(
    password="your-master-password",
    totp="123456"  # optional
)
```

### `lock_vault`
Lock the Bitwarden vault and clear session.

**Example:**
```python
bitwarden.lock_vault()
```

### `get_secret`
Retrieve a secret from Bitwarden by name.

**Parameters:**
- `name` (string): Item name in Bitwarden
- `field` (string, optional): Field to retrieve (password, username, note, uri, or custom field name)

**Returns:** Secret value (string)

**Example:**
```python
# Get API key (password field)
api_key = bitwarden.get_secret("OpenRouter API Key")

# Get username
user = bitwarden.get_secret("GitHub", field="username")

# Get custom field
secret = bitwarden.get_secret("My Service", field="API_KEY")
```

### `list_secrets`
List all secrets matching a search query.

**Parameters:**
- `search` (string, optional): Search filter

**Returns:** List of item names

**Example:**
```python
# List all secrets
all_items = bitwarden.list_secrets()

# Search for API keys
api_keys = bitwarden.list_secrets(search="API")
```

### `populate_env`
Populate a .env file with secrets from Bitwarden.

**Parameters:**
- `env_file` (string): Path to .env file
- `secrets` (list): List of secret names to include

**Example:**
```python
bitwarden.populate_env(
    env_file=".env",
    secrets=["OpenRouter API Key", "GitHub Token", "Database Password"]
)
```

### `get_login`
Retrieve full login credentials for a service.

**Parameters:**
- `service` (string): Service/item name in Bitwarden

**Returns:** Dict with name, username, password, uri

**Example:**
```python
creds = bitwarden.get_login("GitHub")
# Returns: {"name": "GitHub", "username": "user", "password": "...", "uri": "..."}
```

### `generate_password`
Generate a secure password.

**Parameters:**
- `length` (int, optional): Password length (default: 32)
- `uppercase` (bool, optional): Include uppercase (default: True)
- `numbers` (bool, optional): Include numbers (default: True)
- `special` (bool, optional): Include special chars (default: True)

**Returns:** Generated password (string)

**Example:**
```python
password = bitwarden.generate_password(length=24)
```

### `check_status`
Check current vault status.

**Returns:** Dict with status, session, server info

**Example:**
```python
status = bitwarden.check_status()
# Returns: {"status": "unlocked", "session_active": True}
```

## Automatic Behavior

When this skill is loaded, the agent can:

1. **Guide users through vault unlock** with password and 2FA
2. **Retrieve API keys** for project configuration
3. **Populate .env files** with secrets from Bitwarden
4. **Manage sessions** with secure storage

## Usage in Agent Config

```yaml
# In skills list:
skills:
  - bitwarden_secrets

# In tools list:
tools:
  - bitwarden_secrets.unlock_vault
  - bitwarden_secrets.lock_vault
  - bitwarden_secrets.get_secret
  - bitwarden_secrets.list_secrets
  - bitwarden_secrets.populate_env
  - bitwarden_secrets.get_login
  - bitwarden_secrets.generate_password
  - bitwarden_secrets.check_status
```

## Environment Variables

```bash
# Session storage (auto-managed)
export BW_SESSION="session-token"

# For API key login (bypasses 2FA)
export BW_CLIENTID="user.clientId"
export BW_CLIENTSECRET="your-secret"
```

## MCP Server Integration

The official Bitwarden MCP server (`@bitwarden/mcp-server`) is configured for agents that support it:

```json
{
  "mcpServers": {
    "bitwarden": {
      "command": "npx",
      "args": ["-y", "@bitwarden/mcp-server"],
      "env": {
        "BW_SESSION": "${BW_SESSION}"
      }
    }
  }
}
```

## Implementation

- **Python**: `~/dotfiles/ai/skills/bitwarden/bitwarden_skill.py`
- **Shell**: `~/dotfiles/ai/skills/bitwarden/bitwarden.sh`
- **MCP Config**: `~/dotfiles/ai/config/mcp/bitwarden-mcp.json`

## Non-Interactive Unlock (Automated Agents)

All agents can unlock the vault **without user intervention** using a stored master password.

### How It Works

1. Password stored in `~/dotfiles/secrets/.bw_master_password` (chmod 600)
2. Directory `~/dotfiles/secrets/` is chmod 700
3. `.bw_credentials` provides API key login (bypasses 2FA)
4. `bitwarden.sh` automatically reads the password file when no password is provided

### One-Time Setup

```bash
echo -n "Master password: " && read -s pw && echo "$pw" > ~/dotfiles/secrets/.bw_master_password && chmod 600 ~/dotfiles/secrets/.bw_master_password && unset pw
```

### Usage (No Intervention Required)

```bash
# Automatic unlock - reads password from file
export BW_SESSION=$(~/dotfiles/ai/shared/skills/bitwarden/bitwarden.sh unlock)

# Get secrets
~/dotfiles/ai/shared/skills/bitwarden/bitwarden.sh get-secret --name "API Key"

# Lock when done
~/dotfiles/ai/shared/skills/bitwarden/bitwarden.sh lock
```

### Security

- Password file: `chmod 600` (owner read/write only)
- Secrets directory: `chmod 700` (owner access only)
- No git tracking: `~/dotfiles/secrets/` is not a git repo
- Gitignore rules: `secrets/`, `.bw_master_password`, `*bw*password*` all excluded
- Session stored in `~/.config/bitwarden-ai/session.env` (chmod 600)

## Security Notes

- Session keys stored in `~/.config/bitwarden-ai/` with mode 600
- Never log or display passwords
- Use `lock_vault` when done to clear session
- Use API key login for automation (bypasses 2FA)
- Password file permissions auto-corrected to 600 on access

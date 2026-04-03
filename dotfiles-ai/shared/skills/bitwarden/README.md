# Bitwarden Integration for AI Agents

**Location**: `~/dotfiles/ai/skills/bitwarden/`

## Quick Start

### 1. Authenticate

```bash
# Login with your Bitwarden account
bw login your-email@example.com

# Or login with API key (recommended for automation)
export BW_CLIENTID="your-client-id"
export BW_CLIENTSECRET="your-client-secret"
bw login --apikey
```

### 2. Unlock Vault

```bash
# Interactive unlock
bw unlock

# Or with password from environment
BW_PASSWORD="your-master-password" bw unlock --passwordenv BW_PASSWORD

# Export session key
export BW_SESSION="your-session-key"
```

### 3. Use Skills

```bash
# List all secrets
~/dotfiles/ai/skills/bitwarden/bitwarden.sh list-secrets

# Get a specific secret
~/dotfiles/ai/skills/bitwarden/bitwarden.sh get-secret --name "OpenRouter API Key" --type password

# Get login credentials
~/dotfiles/ai/skills/bitwarden/bitwarden.sh get-login --service "GitHub"

# Populate .env file
~/dotfiles/ai/skills/bitwarden/bitwarden.sh populate-env --env-file ".env" --secrets "OpenRouter API Key,Letta API Key"

# Generate a password
~/dotfiles/ai/skills/bitwarden/bitwarden.sh generate-password --length 32
```

### 4. Lock Vault (when done)

```bash
~/dotfiles/ai/skills/bitwarden/bitwarden.sh lock
```

## Shell Integration

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Bitwarden shortcuts
alias bw-unlock='eval $(bw unlock --raw) && export BW_SESSION && echo "Vault unlocked"'
alias bw-lock='bw lock && unset BW_SESSION && echo "Vault locked"'
alias bw-status='bw status | jq .'

# Quick secret access
bw-get() {
    bw get item "$1" --session "$BW_SESSION" | jq -r '.login.password'
}

# Auto-populate .env
bw-env() {
    local env_file="${1:-.env}"
    shift
    ~/dotfiles/ai/skills/bitwarden/bitwarden.sh populate-env --env-file "$env_file" --secrets "$@"
}
```

## Store New Secrets

### API Key

```bash
bw create item '{
  "name": "OpenRouter API Key",
  "type": 2,
  "notes": "API key for OpenRouter free models",
  "fields": [
    {
      "name": "API_KEY",
      "value": "sk-or-v1-...",
      "type": 1
    }
  ]
}'
```

### Login

```bash
bw create item '{
  "name": "GitHub Login",
  "type": 1,
  "login": {
    "username": "cbwinslow",
    "password": "your-password"
  },
  "notes": "GitHub account"
}'
```

### Secure Note

```bash
bw create item '{
  "name": "Database Connection String",
  "type": 2,
  "notes": "postgresql://user:pass@localhost:5432/letta"
}'
```

## Machine Account Setup (Recommended)

For automated/CI access:

1. **Create Machine Account** in Bitwarden admin console
2. **Get Access Token**
3. **Authenticate**:
```bash
export BW_ACCESS_TOKEN="your-access-token"
bw login --accesstoken
```

## Security Notes

- Session keys expire after 1 hour
- Lock vault after use: `bw lock`
- Never commit `.env` files to git
- Use `.gitignore` to exclude sensitive files

---
description: Bitwarden vault operations workflow for AI agents
tags: [bitwarden, secrets, vault, security, workflow]
---

# Bitwarden Vault Workflow

## Overview
Standard workflow for AI agents to securely access and manage Bitwarden vault items including passwords, API keys, and secure notes.

## Prerequisites
- Bitwarden CLI installed (`bw`)
- Authenticated and vault unlocked
- `BW_SESSION` environment variable set

## Quick Start

### 1. Check Vault Status
```bash
# Verify vault is accessible
bw status
```

Expected output:
```json
{
  "serverUrl": "https://vault.bitwarden.com",
  "lastSync": "2024-01-15T10:30:00.000Z",
  "userEmail": "user@example.com",
  "userId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "unlocked"
}
```

### 2. Sync Vault
```bash
# Get latest changes from server
bw sync
```

## Common Operations

### Retrieve API Keys

#### Pattern 1: Direct Lookup
```bash
# Get API key by item name
bw get password "API Keys/OpenAI"

# Get from custom field
bw get item "API Keys" | jq -r '.fields[] | select(.name=="OPENAI_API_KEY").value'
```

#### Pattern 2: Search and Retrieve
```bash
# Search for items
bw list items --search "openai" | jq -r '.[].name'

# Get specific item
bw get password "OpenAI API Key"
```

#### Pattern 3: Batch Export
```bash
# Export all API keys to JSON
python3 ~/dotfiles/ai/skills/bitwarden_secrets/bitwarden_secrets.py export

# Export as .env format
python3 ~/dotfiles/ai/skills/bitwarden_secrets/bitwarden_secrets.py export-env
```

### Retrieve Passwords

```bash
# Get password for service
bw get password "GitHub"

# Get username and password
USER=$(bw get username "GitHub")
PASS=$(bw get password "GitHub")
echo "Username: $USER"
echo "Password: $PASS"
```

### Retrieve Database Credentials

```bash
# Get database URI from notes
bw get notes "Database/Production"

# Or from custom field
bw get item "PostgreSQL Production" | jq -r '.fields[] | select(.name=="DATABASE_URL").value'
```

## Automation Workflow

### Step 1: Setup Environment
```bash
#!/bin/bash
# setup_bitwarden_env.sh

# Check if already unlocked
STATUS=$(bw status | jq -r '.status')

if [ "$STATUS" != "unlocked" ]; then
    echo "🔐 Unlocking Bitwarden vault..."
    export BW_SESSION=$(bw unlock --raw)
fi

# Sync vault
bw sync

echo "✅ Bitwarden ready"
```

### Step 2: Load API Keys
```bash
#!/bin/bash
# load_api_keys.sh

# Source the setup
source setup_bitwarden_env.sh

# Load common API keys
export OPENAI_API_KEY=$(bw get password "API Keys/OpenAI")
export ANTHROPIC_API_KEY=$(bw get password "API Keys/Anthropic")
export GITHUB_TOKEN=$(bw get password "API Keys/GitHub")
export STRIPE_KEY=$(bw get password "API Keys/Stripe")

echo "🔑 API keys loaded"
echo "  ✓ OpenAI"
echo "  ✓ Anthropic"
echo "  ✓ GitHub"
echo "  ✓ Stripe"
```

### Step 3: Use in Application
```python
#!/usr/bin/env python3
# app_with_bitwarden.py

import os
import subprocess

def load_bitwarden_env():
    """Load secrets from Bitwarden into environment."""
    
    # Ensure vault is unlocked
    result = subprocess.run(
        ['bw', 'status'],
        capture_output=True, text=True
    )
    
    if 'unlocked' not in result.stdout:
        print("🔐 Please unlock Bitwarden first:")
        print("  export BW_SESSION=$(bw unlock --raw)")
        return False
    
    # Load API keys
    keys = {
        'OPENAI_API_KEY': 'API Keys/OpenAI',
        'ANTHROPIC_API_KEY': 'API Keys/Anthropic',
        'GITHUB_TOKEN': 'API Keys/GitHub',
    }
    
    for env_var, item_name in keys.items():
        result = subprocess.run(
            ['bw', 'get', 'password', item_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            os.environ[env_var] = result.stdout.strip()
            print(f"✓ Loaded {env_var}")
    
    return True

# Initialize
if load_bitwarden_env():
    # Now use the API keys
    import openai
    openai.api_key = os.environ['OPENAI_API_KEY']
    # ... continue with app
```

## Agent Integration Patterns

### Pattern 1: Lazy Loading
```python
class BitwardenProvider:
    """Lazy secret loading from Bitwarden."""
    
    def __init__(self):
        self._cache = {}
    
    def get_secret(self, name: str) -> str:
        """Get secret, cache for reuse."""
        if name not in self._cache:
            import subprocess
            result = subprocess.run(
                ['bw', 'get', 'password', name],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self._cache[name] = result.stdout.strip()
        return self._cache.get(name)
    
    def __getitem__(self, name: str) -> str:
        return self.get_secret(name)

# Usage
secrets = BitwardenProvider()
api_key = secrets["API Keys/OpenAI"]
```

### Pattern 2: Context Manager
```python
from contextlib import contextmanager
import os
import subprocess

@contextmanager
def bitwarden_session():
    """Context manager for Bitwarden operations."""
    # Ensure unlocked
    result = subprocess.run(
        ['bw', 'status'],
        capture_output=True, text=True
    )
    
    if 'unlocked' not in result.stdout:
        raise RuntimeError("Bitwarden vault locked")
    
    try:
        yield BitwardenVault()
    finally:
        # Optional: lock after use
        # subprocess.run(['bw', 'lock'])
        pass

class BitwardenVault:
    """Vault interface for use with context manager."""
    
    def get(self, name: str) -> str:
        result = subprocess.run(
            ['bw', 'get', 'password', name],
            capture_output=True, text=True
        )
        return result.stdout.strip() if result.returncode == 0 else None

# Usage
with bitwarden_session() as vault:
    api_key = vault.get("API Keys/OpenAI")
    # Use key...
```

### Pattern 3: Agent Memory Integration
```python
# Save Bitwarden reference to Letta memory
import subprocess

# After loading secrets, save reference
subprocess.run([
    'letta-memory-cli', 'memory', 'save',
    '--agent', 'my_agent',
    '--content', 'Loaded API keys from Bitwarden: OpenAI, Anthropic, GitHub',
    '--type', 'archival',
    '--tags', 'bitwarden,api-keys,setup'
])
```

## Multi-Skill Integration

### Chain: bitwarden → coding
```bash
# Get API key, use in code generation
API_KEY=$(bw get password "API Keys/OpenAI")

# Generate code using the key
cat > config.py << EOF
OPENAI_API_KEY = "$API_KEY"
EOF
```

### Chain: bitwarden → docker-ops
```bash
# Get registry credentials
DOCKER_USER=$(bw get username "Docker Hub")
DOCKER_PASS=$(bw get password "Docker Hub")

# Login to Docker
echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
```

### Chain: bitwarden → system-maintenance
```bash
# Get sudo password
SUDO_PASS=$(bw get password "System/sudo")

# Run maintenance with password
echo "$SUDO_PASS" | sudo -S apt update
```

## Error Handling

### Common Issues

#### Vault Locked
```python
import subprocess
import json

def ensure_unlocked():
    """Ensure Bitwarden vault is unlocked."""
    result = subprocess.run(
        ['bw', 'status'],
        capture_output=True, text=True
    )
    
    status = json.loads(result.stdout)
    
    if status['status'] == 'locked':
        print("🔐 Vault locked. Please unlock:")
        print("  export BW_SESSION=$(bw unlock --raw)")
        return False
    
    elif status['status'] == 'unauthenticated':
        print("🔐 Not logged in. Please login:")
        print("  bw login username@example.com")
        return False
    
    return True
```

#### Item Not Found
```python
import subprocess

def find_item(partial_name: str):
    """Search for item with partial name match."""
    result = subprocess.run(
        ['bw', 'list', 'items', '--search', partial_name],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        import json
        items = json.loads(result.stdout)
        if items:
            print(f"Found {len(items)} matches:")
            for item in items:
                print(f"  - {item['name']}")
            return items[0]['name']  # Return first match
    
    print(f"No items found matching '{partial_name}'")
    return None
```

#### CLI Not Installed
```python
import shutil

def check_bw_installed():
    """Check if Bitwarden CLI is installed."""
    if not shutil.which('bw'):
        print("❌ Bitwarden CLI not found")
        print("Install with:")
        print("  sudo snap install bw")
        print("  or: https://bitwarden.com/download/")
        return False
    return True
```

## Security Best Practices

### Environment Setup
```bash
# Secure permissions on session
echo 'export BW_SESSION=$(bw unlock --raw)' >> ~/.bashrc
chmod 600 ~/.bashrc

# Or use a secure env file
echo "BW_SESSION=$(bw unlock --raw)" > ~/.bw_session
chmod 600 ~/.bw_session
```

### No Hardcoded Secrets
```python
# ❌ BAD: Hardcoded secret
API_KEY = "sk-1234567890abcdef"

# ✅ GOOD: From Bitwarden
import subprocess
result = subprocess.run(
    ['bw', 'get', 'password', 'API Keys/OpenAI'],
    capture_output=True, text=True
)
API_KEY = result.stdout.strip()
```

### Lock After Use
```python
import subprocess
import atexit

def lock_vault():
    """Lock vault on exit."""
    subprocess.run(['bw', 'lock'])

# Register cleanup
atexit.register(lock_vault)
```

## Testing the Workflow

### Test Script
```bash
#!/bin/bash
# test_bitwarden_workflow.sh

echo "=== Testing Bitwarden Workflow ==="

# 1. Check status
echo -e "\n1. Checking vault status..."
bw status | jq -r '.status' || exit 1

# 2. Sync
echo -e "\n2. Syncing vault..."
bw sync

# 3. List items
echo -e "\n3. Available items:"
bw list items | jq -r '.[].name' | head -10

# 4. Test retrieval
echo -e "\n4. Testing secret retrieval..."
python3 << 'EOF'
import subprocess
result = subprocess.run(
    ['bw', 'list', 'items'],
    capture_output=True, text=True
)
if result.returncode == 0:
    print("✅ Successfully accessed vault")
else:
    print("❌ Failed to access vault")
    exit(1)
EOF

echo -e "\n✅ All tests passed!"
```

## Related Workflows
- bitwarden-secrets-management - Advanced API key management
- security-audit - Vault security review
- onboarding-setup - New agent Bitwarden setup

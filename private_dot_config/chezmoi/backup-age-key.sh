#!/bin/bash
# Backup chezmoi age key to Bitwarden
# Run this after unlocking Bitwarden with: bw login

set -e

AGE_KEY_FILE="$HOME/.config/chezmoi/key.txt"
AGE_PUBKEY=$(grep 'public key' "$AGE_KEY_FILE" | awk '{print $4}')
AGE_KEY=$(cat "$AGE_KEY_FILE")
HOSTNAME=$(hostname)

echo "=== Backing up chezmoi age key to Bitwarden ==="
echo "Public key: $AGE_PUBKEY"
echo "Hostname: $HOSTNAME"

# Check if Bitwarden is unlocked
if ! bw status 2>/dev/null | grep -q '"status":"unlocked"'; then
    echo "Bitwarden vault is locked. Run: bw login"
    exit 1
fi

# Create secure note with age key
bw get item "chezmoi-age-key-$HOSTNAME" >/dev/null 2>&1 && {
    echo "Item already exists, updating..."
    ITEM_ID=$(bw get item "chezmoi-age-key-$HOSTNAME" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
    bw delete item "$ITEM_ID" >/dev/null 2>&1
}

bw encode << BWJSON | bw create item >/dev/null 2>&1
{
  "name": "chezmoi-age-key-$HOSTNAME",
  "type": 2,
  "notes": "Age encryption key for chezmoi dotfiles repo\nPublic key: $AGE_PUBKEY\nCreated: $(date -u +%Y-%m-%dT%H:%M:%SZ)\nMachine: $HOSTNAME\n\nKEY CONTENT (DO NOT SHARE):\n$AGE_KEY"
}
BWJSON

echo "✓ Age key backed up to Bitwarden as 'chezmoi-age-key-$HOSTNAME'"

# Also backup SSH private key
SSH_KEY_FILE="$HOME/.ssh/id_ed25519"
if [ -f "$SSH_KEY_FILE" ]; then
    SSH_KEY=$(cat "$SSH_KEY_FILE")
    bw get item "ssh-key-$HOSTNAME" >/dev/null 2>&1 && {
        ITEM_ID=$(bw get item "ssh-key-$HOSTNAME" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
        bw delete item "$ITEM_ID" >/dev/null 2>&1
    }
    
    bw encode << BWJSON | bw create item >/dev/null 2>&1
{
  "name": "ssh-key-$HOSTNAME",
  "type": 2,
  "notes": "SSH private key for $HOSTNAME\nGenerated: $(date -u +%Y-%m-%dT%H:%M:%SZ)\n\nKEY CONTENT:\n$SSH_KEY"
}
BWJSON
    echo "✓ SSH key backed up to Bitwarden as 'ssh-key-$HOSTNAME'"
fi

echo ""
echo "=== Bitwarden items ==="
bw list items 2>/dev/null | python3 -c "
import sys, json
items = json.load(sys.stdin)
for item in items:
    name = item.get('name', 'Unknown')
    print(f'  - {name}')
" 2>/dev/null || echo "Could not list items"

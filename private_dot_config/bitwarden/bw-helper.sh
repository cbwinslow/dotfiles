#!/bin/bash
# Bitwarden CLI helper functions
# Usage: source this file in your shell

bw_get_secret() {
    local item_name="$1"
    local field_name="$2"
    
    if [ -z "$item_name" ] || [ -z "$field_name" ]; then
        echo "Usage: bw_get_secret <item_name> <field_name>"
        return 1
    fi
    
    # Check if unlocked
    if ! bw status 2>/dev/null | grep -q '"status":"unlocked"'; then
        echo "Bitwarden vault is locked. Run: bw login"
        return 1
    fi
    
    # Get the secret
    bw get item "$item_name" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('login',{}).get('$field_name',''))" 2>/dev/null
}

bw_unlock() {
    if bw status 2>/dev/null | grep -q '"status":"unlocked"'; then
        echo "Vault already unlocked"
        return 0
    fi
    
    echo "Unlocking Bitwarden vault..."
    export BW_SESSION=$(bw unlock --raw 2>/dev/null)
    if [ -n "$BW_SESSION" ]; then
        echo "Vault unlocked successfully"
        return 0
    else
        echo "Failed to unlock vault"
        return 1
    fi
}

bw_list_secrets() {
    if ! bw status 2>/dev/null | grep -q '"status":"unlocked"'; then
        echo "Vault is locked. Run: bw login"
        return 1
    fi
    
    bw list items 2>/dev/null | \
        python3 -c "
import sys, json
items = json.load(sys.stdin)
for item in items:
    name = item.get('name', 'Unknown')
    item_type = item.get('type', 'unknown')
    print(f'  {name} ({item_type})')
"
}

#!/bin/bash
# Bitwarden Skills for AI Agents
# Location: ~/dotfiles/ai/skills/bitwarden/
# 
# Merged version: Original bitwarden.sh + interactive/session features
# AI agents can use this to guide users through vault access

set -e

BW_CMD="bw"
BW_SESSION_VAR="BW_SESSION"
BW_DIR="$HOME/.config/bitwarden-ai"
SESSION_FILE="$BW_DIR/session.env"

# Create secure directory for session storage
mkdir -p "$BW_DIR"
chmod 700 "$BW_DIR" 2>/dev/null || true

# ============================================================================
# Session Management
# ============================================================================

# Check if session is valid (auto-login and auto-unlock if needed)
check_session() {
    # First check environment variable
    if [ -n "${!BW_SESSION_VAR}" ]; then
        if $BW_CMD status --session "${!BW_SESSION_VAR}" 2>/dev/null | grep -q '"status":"unlocked"'; then
            return 0
        fi
    fi
    
    # Try loading from session file
    if [ -f "$SESSION_FILE" ]; then
        source "$SESSION_FILE" 2>/dev/null
        if [ -n "$BW_SESSION" ] && $BW_CMD status --session "$BW_SESSION" 2>/dev/null | grep -q '"status":"unlocked"'; then
            export BW_SESSION
            return 0
        fi
    fi
    
    # Auto-login if not authenticated
    local status=$($BW_CMD status 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$status" = "unauthenticated" ]; then
        bw_login || return 1
    fi
    
    # Auto-unlock if locked
    if [ "$status" = "locked" ] || [ "$status" = "unauthenticated" ]; then
        bw_unlock || return 1
        return 0
    fi
    
    echo "Error: Vault is locked. Run '$0 unlock' first." >&2
    return 1
}

# Save session to file securely
save_session() {
    local session="$1"
    chmod 700 "$BW_DIR" 2>/dev/null || true
    cat > "$SESSION_FILE" << EOF
export BW_SESSION="$session"
export BW_LAST_UNLOCK="$(date +%s)"
EOF
    chmod 600 "$SESSION_FILE"
}

# Load session from file
load_session() {
    if [ -f "$SESSION_FILE" ]; then
        source "$SESSION_FILE" 2>/dev/null
        export BW_SESSION
        return 0
    fi
    return 1
}

# ============================================================================
# Core Functions
# ============================================================================

# Get a secret from Bitwarden
bw_get_secret() {
    local name=""
    local field=""
    local type="password"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --name|-n) name="$2"; shift 2 ;;
            --field|-f) field="$2"; shift 2 ;;
            --type|-t) type="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    if [ -z "$name" ]; then
        echo "Error: --name required" >&2
        return 1
    fi
    
    check_session || return 1
    
    case $type in
        password)
            $BW_CMD get item "$name" --session "$BW_SESSION" | jq -r '.login.password // empty'
            ;;
        username)
            $BW_CMD get item "$name" --session "$BW_SESSION" | jq -r '.login.username // empty'
            ;;
        note)
            $BW_CMD get item "$name" --session "$BW_SESSION" | jq -r '.notes // empty'
            ;;
        field)
            if [ -z "$field" ]; then
                echo "Error: --field required for type 'field'" >&2
                return 1
            fi
            $BW_CMD get item "$name" --session "$BW_SESSION" | jq -r ".fields[] | select(.name==\"$field\") | .value // empty"
            ;;
        uri)
            $BW_CMD get item "$name" --session "$BW_SESSION" | jq -r '.login.uris[0].uri // empty'
            ;;
        *)
            echo "Error: Unknown type '$type'" >&2
            return 1
            ;;
    esac
}

# List secrets
bw_list_secrets() {
    local search=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --search|-s) search="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    check_session || return 1
    
    if [ -n "$search" ]; then
        $BW_CMD list items --search "$search" --session "$BW_SESSION" | jq -r '.[].name'
    else
        $BW_CMD list items --session "$BW_SESSION" | jq -r '.[].name'
    fi
}

# Get login credentials
bw_get_login() {
    local service=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --service|-s) service="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    if [ -z "$service" ]; then
        echo "Error: --service required" >&2
        return 1
    fi
    
    check_session || return 1
    
    $BW_CMD get item "$service" --session "$BW_SESSION" | jq '{
        name: .name,
        username: .login.username,
        password: .login.password,
        uri: .login.uris[0].uri
    }'
}

# Generate password
bw_generate_password() {
    local length=32
    local uppercase=true
    local numbers=true
    local special=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --length|-l) length="$2"; shift 2 ;;
            --no-uppercase) uppercase=false; shift ;;
            --no-numbers) numbers=false; shift ;;
            --no-special) special=false; shift ;;
            *) shift ;;
        esac
    done
    
    $BW_CMD generate --length "$length" \
        $([ "$uppercase" = true ] && echo "--uppercase") \
        $([ "$numbers" = true ] && echo "--numbers") \
        $([ "$special" = true ] && echo "--special")
}

# Populate .env file
bw_populate_env() {
    local env_file=".env"
    local secrets=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env-file|-e) env_file="$2"; shift 2 ;;
            --secrets|-s) 
                IFS=',' read -ra secrets <<< "$2"
                shift 2
                ;;
            *) shift ;;
        esac
    done
    
    check_session || return 1
    
    if [ ${#secrets[@]} -eq 0 ]; then
        echo "Error: --secrets required" >&2
        return 1
    fi
    
    # Backup existing .env
    if [ -f "$env_file" ]; then
        cp "$env_file" "${env_file}.bak.$(date +%s)"
    fi
    
    # Create new .env
    > "$env_file"
    
    for secret_name in "${secrets[@]}"; do
        # Try to get password first, then field
        value=$($BW_CMD get item "$secret_name" --session "$BW_SESSION" | jq -r '
            if .login.password then
                .login.password
            elif .fields then
                .fields[0].value // ""
            else
                ""
            end
        ')
        
        if [ -n "$value" ]; then
            # Convert name to env var format
            var_name=$(echo "$secret_name" | tr '[:lower:]' '[:upper:]' | tr ' -' '__')
            echo "${var_name}=${value}" >> "$env_file"
            echo "Added $secret_name -> $var_name"
        else
            echo "Not found: $secret_name" >&2
        fi
    done
    
    echo "Populated $env_file with ${#secrets[@]} secrets"
}

# ============================================================================
# Vault Management
# ============================================================================

# Unlock vault (saves session)
bw_unlock() {
    local password="${1:-}"
    local totp="${2:-}"
    local pass_file="${HOME}/dotfiles/secrets/.bw_master_password"

    if [ -z "$password" ]; then
        if [ -n "$BW_PASSWORD" ]; then
            password="$BW_PASSWORD"
        elif [ -f "$pass_file" ]; then
            password=$(cat "$pass_file" | tr -d '\n')
        else
            echo "Error: Password required" >&2
            return 1
        fi
    fi
    
    export BW_PASSWORD="$password"
    if [ -n "$totp" ]; then
        export BW_TOTP="$totp"
    fi
    
    local output
    if output=$($BW_CMD unlock --passwordenv BW_PASSWORD ${totp:+--totpenv BW_TOTP} --raw 2>&1); then
        export BW_SESSION="$output"
        save_session "$output"
        unset BW_PASSWORD BW_TOTP
        echo "Vault unlocked. Session saved."
        return 0
    else
        echo "Error: $output" >&2
        unset BW_PASSWORD BW_TOTP
        return 1
    fi
}

# Lock vault (clears session)
bw_lock() {
    $BW_CMD lock 2>/dev/null || true
    if [ -f "$SESSION_FILE" ]; then
        shred -u "$SESSION_FILE" 2>/dev/null || rm -f "$SESSION_FILE"
    fi
    unset BW_SESSION
    echo "Vault locked"
}

# Show status
bw_status() {
    local session="${!BW_SESSION_VAR}"
    if [ -z "$session" ]; then
        load_session && session="$BW_SESSION"
    fi
    
    if [ -n "$session" ] && $BW_CMD status --session "$session" 2>/dev/null | grep -q '"status":"unlocked"'; then
        $BW_CMD status --session "$session" | jq '{
            server: .server,
            lastSync: .lastSync,
            user: .userEmail,
            vaultStatus: .status
        }'
    else
        echo '{"status": "locked"}'
    fi
}

# Login with API key (bypasses 2FA for login)
bw_login() {
    local client_id="${BW_CLIENTID:-}"
    local client_secret="${BW_CLIENTSECRET:-}"
    local cred_file="${SKILL_DIR}/.bw_credentials"
    
    # Auto-source credentials from skill directory
    if [ -z "$client_id" ] && [ -f "$cred_file" ]; then
        source "$cred_file"
        client_id="${BW_CLIENTID:-}"
        client_secret="${BW_CLIENTSECRET:-}"
    fi
    
    if [ -z "$client_id" ] || [ -z "$client_secret" ]; then
        echo "Error: Set BW_CLIENTID and BW_CLIENTSECRET environment variables or create .bw_credentials" >&2
        return 1
    fi
    
    export BW_CLIENTID="$client_id"
    export BW_CLIENTSECRET="$client_secret"
    
    if $BW_CMD login --apikey 2>&1; then
        echo "Logged in."
        return 0
    else
        return 1
    fi
}

# ============================================================================
# Interactive Mode for AI Agents
# ============================================================================

# Interactive unlock - AI agents can call this to walk users through
bw_interactive() {
    echo "=== Bitwarden Vault Unlock ==="
    echo ""
    
    # Check if already unlocked
    if check_session 2>/dev/null; then
        echo "Vault is already unlocked!"
        return 0
    fi
    
    echo "The vault is currently locked."
    echo ""
    
    # Get password
    read -p "Enter your Bitwarden master password: " -s password
    echo ""
    
    # Get TOTP (optional)
    read -p "Enter 2FA code (or press Enter to skip): " totp
    echo ""
    
    # Attempt unlock
    if bw_unlock "$password" "$totp"; then
        echo ""
        echo "Success! Vault is now unlocked."
    else
        echo ""
        echo "Unlock failed. Please check your credentials."
    fi
    
    unset password totp
}

# Setup guide
bw_setup() {
    cat << 'EOF'
=== Bitwarden Setup for AI Agents ===

To use Bitwarden with AI agents:

1. Get your API Key (recommended):
   - Go to: https://vault.bitwarden.com/#/settings/api-key
   - Click "View API Key"
   - Copy your Client ID and Client Secret

2. Set environment variables:
   export BW_CLIENTID="user.clientId"
   export BW_CLIENTSECRET="your-secret"

3. Login (bypasses 2FA):
   ~/dotfiles/ai/skills/bitwarden/bitwarden.sh login

4. Unlock with master password:
   ~/dotfiles/ai/skills/bitwarden/bitwarden.sh unlock "your-master-password" "2fa-code"

Session is saved to: ~/.config/bitwarden-ai/session.env

Commands:
  unlock <password> [totp]   - Unlock vault
  lock                        - Lock vault
  login                       - Login with API key
  get-secret --name <name>    - Get a secret
  list-secrets [--search <q>] - List secrets
  populate-env                - Populate .env file
  status                      - Show vault status
  interactive                 - Interactive unlock wizard
EOF
}

# ============================================================================
# Main Command Dispatcher
# ============================================================================

case "${1:-help}" in
    # Original commands
    get-secret) shift; bw_get_secret "$@" ;;
    list-secrets) shift; bw_list_secrets "$@" ;;
    get-login) shift; bw_get_login "$@" ;;
    generate-password) shift; bw_generate_password "$@" ;;
    populate-env) shift; bw_populate_env "$@" ;;
    unlock) shift; bw_unlock "$@" ;;
    lock) shift; bw_lock "$@" ;;
    status) shift; bw_status "$@" ;;
    login) shift; bw_login "$@" ;;
    
    # New commands
    interactive) bw_interactive ;;
    setup|help|--help|-h)
        if [ "${1:-help}" = "setup" ]; then
            shift; bw_setup "$@"
        else
            cat << EOF
Bitwarden Skills for AI Agents

Usage: $0 <command> [options]

Commands:
  get-secret          Get a secret from Bitwarden
  list-secrets        List available secrets
  get-login           Get login credentials
  generate-password   Generate a secure password
  populate-env        Populate .env file from secrets
  unlock              Unlock the vault (saves session)
  lock                Lock the vault (clears session)
  status              Show Bitwarden status
  login               Login with API key (bypasses 2FA)
  interactive         Interactive unlock wizard
  setup               Show setup guide

Examples:
  $0 unlock "my-password" "123456"
  $0 get-secret --name "OpenRouter API Key" --type password
  $0 list-secrets --search "API"
  $0 populate-env --env-file ".env" --secrets "OpenRouter,Letta"
  $0 interactive

EOF
        fi
        ;;
    *)
        echo "Unknown command: $1. Run '$0 help' for usage." >&2
        exit 1
        ;;
esac
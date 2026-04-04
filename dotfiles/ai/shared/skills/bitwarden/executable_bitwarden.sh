#!/bin/bash
# Bitwarden Secrets Skill - Free Password Manager Edition
# Version: 2.0
# Supports: Bitwarden Password Manager CLI (bw) only - free plan
# Workflow: config server → login → unlock → use session → lock

set -euo pipefail

BW_CMD="bw"
BW_SESSION_VAR="BW_SESSION"
BW_DIR="$HOME/.config/bitwarden-ai"
SESSION_FILE="$BW_DIR/session.env"
DEFAULT_MAP_FILE="bitwarden-env-map.json"
DEFAULT_ENV_FILE=".env"

# ============================================================================
# Security & Dependency Checks
# ============================================================================

require() {
    if ! command -v "$1" &>/dev/null; then
        echo "Error: Required command not found: $1" >&2
        echo "Install: https://bitwarden.com/help/article/cli/#install-the-cli" >&2
        return 1
    fi
}

check_auth_env() {
    # Required for non-interactive operation
    : "${BW_CLIENTID:?Set BW_CLIENTID environment variable}"
    : "${BW_CLIENTSECRET:?Set BW_CLIENTSECRET environment variable}"
    : "${BW_PASSWORD:?Set BW_PASSWORD environment variable}"
}

# ============================================================================
# Server Configuration (Self-Hosted Support)
# ============================================================================

configure_server() {
    if [[ -n "${BW_SERVER_URL:-}" ]]; then
        # Self-hosted Bitwarden instance
        echo "Configuring self-hosted server: $BW_SERVER_URL"
        if ! $BW_CMD config server "$BW_SERVER_URL" 2>/dev/null; then
            echo "Warning: Failed to configure server (may already be set)" >&2
        fi
    fi
}

# ============================================================================
# Authentication: Login + Unlock
# ============================================================================

 bitwarden_login() {
     check_auth_env
     configure_server
     
     echo "Logging in with API key..."
     local login_output
     if ! login_output=$($BW_CMD login --apikey --nointeraction 2>&1); then
         # If already logged in, treat as success
         if echo "$login_output" | grep -qi "already logged in"; then
             echo "Already logged in."
             return 0
         else
             echo "Error: Login failed. Check BW_CLIENTID and BW_CLIENTSECRET." >&2
             return 1
         fi
     fi
     echo "Logged in successfully."
 }

bitwarden_unlock() {
    check_auth_env
    
    # Unlock and capture session token
    local session
    if ! session=$($BW_CMD unlock --passwordenv BW_PASSWORD --raw 2>&1); then
        echo "Error: Unlock failed. Check BW_PASSWORD." >&2
        return 1
    fi
    
    export BW_SESSION="$session"
    # Save session for reuse
    mkdir -p "$BW_DIR"
    chmod 700 "$BW_DIR" 2>/dev/null || true
    cat > "$SESSION_FILE" << EOF
export BW_SESSION="$session"
export BW_LAST_UNLOCK="$(date +%s)"
EOF
    chmod 600 "$SESSION_FILE"
    
    echo "Vault unlocked. Session saved to: $SESSION_FILE"
}

ensure_session() {
    # Check if we have a valid session
    local session="${BW_SESSION:-}"
    
    # Try loading from file if not in environment
    if [[ -z "$session" ]] && [[ -f "$SESSION_FILE" ]]; then
        source "$SESSION_FILE" 2>/dev/null || true
        session="$BW_SESSION"
    fi
    
    # Validate session
    if [[ -n "$session" ]]; then
        if $BW_CMD status --session "$session" 2>/dev/null | grep -q '"status":"unlocked"'; then
            export BW_SESSION="$session"
            return 0
        fi
    fi
    
    # Need to re-authenticate
    echo "Vault is locked. Attempting login + unlock..." >&2
    if ! bitwarden_login; then
        return 1
    fi
    if ! bitwarden_unlock; then
        return 1
    fi
    
    return 0
}

bitwarden_lock() {
    $BW_CMD lock 2>/dev/null || true
    [[ -f "$SESSION_FILE" ]] && rm -f "$SESSION_FILE"
    unset BW_SESSION
    echo "Vault locked and session cleared."
}

bitwarden_logout() {
    $BW_CMD logout 2>/dev/null || true
    [[ -f "$SESSION_FILE" ]] && rm -f "$SESSION_FILE"
    unset BW_SESSION
    echo "Logged out and session cleared."
}

# ============================================================================
# Secret Retrieval
# ============================================================================

get_secret_field() {
    local item_name="$1"
    local field="$2"
    
    ensure_session || return 1
    
    # Get full item JSON
    local item_json
    if ! item_json=$($BW_CMD get item "$item_name" --session "$BW_SESSION" 2>/dev/null); then
        echo "Error: Item not found: $item_name" >&2
        return 1
    fi
    
    # Extract requested field
    case "$field" in
        password)
            echo "$item_json" | jq -r '.login.password // empty'
            ;;
        username)
            echo "$item_json" | jq -r '.login.username // empty'
            ;;
        note|notes)
            echo "$item_json" | jq -r '.notes // empty'
            ;;
        uri)
            echo "$item_json" | jq -r '.login.uris[0].uri // empty'
            ;;
        *)
            # Custom field - require exact name match
            echo "$item_json" | jq -r --arg f "$field" '.fields[]? | select(.name==$f) | .value // empty'
            ;;
    esac
}

get_secret_by_id() {
    local item_id="$1"
    local field="${2:-password}"
    
    ensure_session || return 1
    
    local item_json
    if ! item_json=$($BW_CMD get item "$item_id" --session "$BW_SESSION" 2>/dev/null); then
        echo "Error: Item ID not found: $item_id" >&2
        return 1
    fi
    
    case "$field" in
        password) echo "$item_json" | jq -r '.login.password // empty' ;;
        username) echo "$item_json" | jq -r '.login.username // empty' ;;
        note|notes) echo "$item_json" | jq -r '.notes // empty' ;;
        uri) echo "$item_json" | jq -r '.login.uris[0].uri // empty' ;;
        *) echo "$item_json" | jq -r --arg f "$field" '.fields[]? | select(.name==$f) | .value // empty' ;;
    esac
}

list_items() {
    local search="${1:-}"
    
    ensure_session || return 1
    
    if [[ -n "$search" ]]; then
        $BW_CMD list items --search "$search" --session "$BW_SESSION" 2>/dev/null | jq -r '.[].name'
    else
        # Security: Refuse to list entire vault without explicit request
        if [[ -z "${BITWARDEN_LIST_ALL:-}" ]]; then
            echo "Error: Listing entire vault is disabled for security." >&2
            echo "Provide a search term or set BITWARDEN_LIST_ALL=1 to override." >&2
            return 1
        fi
        $BW_CMD list items --session "$BW_SESSION" 2>/dev/null | jq -r '.[].name'
    fi
}

# ============================================================================
# Mapping File Support
# ============================================================================

parse_mapping_file() {
    local map_file="${1:-$DEFAULT_MAP_FILE}"
    
    if [[ ! -f "$map_file" ]]; then
        echo "Error: Mapping file not found: $map_file" >&2
        return 1
    fi
    
    # Validate JSON
    if ! jq empty "$map_file" 2>/dev/null; then
        echo "Error: Invalid JSON in mapping file" >&2
        return 1
    fi
    
    # Extract configuration with defaults
    local env_file create_backup write_mode
    env_file=$(jq -r '.env_file // ".env"' "$map_file")
    create_backup=$(jq -r '.create_backup // true' "$map_file")
    write_mode=$(jq -r '.write_mode // "merge"' "$map_file")
    
    # Validate write_mode
    case "$write_mode" in
        merge|replace|ephemeral) ;;
        *)
            echo "Error: Invalid write_mode '$write_mode'. Use merge, replace, or ephemeral." >&2
            return 1
            ;;
    esac
    
    # Output config as JSON for downstream processing
    jq -n \
        --arg env_file "$env_file" \
        --argjson create_backup "$create_backup" \
        --arg write_mode "$write_mode" \
        --argjson secrets "$(jq '.secrets // []' "$map_file")" \
        '{env_file: $env_file, create_backup: $create_backup, write_mode: $write_mode, secrets: $secrets}'
}

backup_env_file() {
    local env_file="$1"
    
    if [[ -f "$env_file" ]] && [[ -s "$env_file" ]]; then
        local backup="${env_file}.bak.$(date +%Y%m%d%H%M%S)"
        cp "$env_file" "$backup"
        chmod 600 "$backup" 2>/dev/null || true
        echo "Created backup: $backup"
    fi
}

upsert_env_merge() {
    local env_file="$1"
    local key="$2"
    local value="$3"
    
    touch "$env_file"
    
    if grep -qE "^${key}=" "$env_file"; then
        # Update existing
        python3 - "$env_file" "$key" "$value" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
k = sys.argv[2]
v = sys.argv[3]
lines = p.read_text().splitlines()
out = []
done = False
for line in lines:
    if line.startswith(k + "="):
        out.append(f"{k}={v}")
        done = True
    else:
        out.append(line)
if not done:
    out.append(f"{k}={v}")
p.write_text("\n".join(out) + "\n")
PY
    else
        # Append new
        printf '%s=%s\n' "$key" "$value" >> "$env_file"
    fi
}

# ============================================================================
# Populate .env from Mapping File
# ============================================================================

populate_from_map() {
    local map_file="${1:-$DEFAULT_MAP_FILE}"
    
    local config_json
    config_json=$(parse_mapping_file "$map_file") || return 1
    
    local env_file write_mode create_backup
    env_file=$(jq -r '.env_file' <<<"$config_json")
    write_mode=$(jq -r '.write_mode' <<<"$config_json")
    create_backup=$(jq -r '.create_backup' <<<"$config_json")
    
    # Ephemeral mode should use inject-env instead
    if [[ "$write_mode" == "ephemeral" ]]; then
        echo "Error: write_mode=ephemeral requires inject-env, not populate-env." >&2
        return 1
    fi
    
    # Backup if requested
    if [[ "$create_backup" == "true" ]]; then
        backup_env_file "$env_file"
    fi
    
    # For replace mode, build fresh content
    local new_content=""
    if [[ "$write_mode" == "replace" ]]; then
        new_content="# Environment variables generated from Bitwarden\n"
        new_content="${new_content}# Generated: $(date -Iseconds)\n\n"
    fi
    
    local total_secrets updated_count=0 failed_secrets=()
    
    # Process each secret mapping
    jq -c '.secrets[]?' <<<"$config_json" | while read -r secret_map; do
        local env_var field source item_id search_term secret_value
        
        env_var=$(jq -r '.env' <<<"$secret_map")
        source=$(jq -r '.source // "item_field"' <<<"$secret_map")
        field=$(jq -r '.field // "password"' <<<"$secret_map")
        item_id=$(jq -r '.id // ""' <<<"$secret_map")
        search_term=$(jq -r '.search // ""' <<<"$secret_map")
        
        # Retrieve secret
        if [[ -n "$item_id" ]] && [[ "$item_id" != "null" ]]; then
            # Use exact ID
            secret_value=$(get_secret_by_id "$item_id" "$field") || {
                failed_secrets+=("$env_var (id lookup failed)")
                continue
            }
        else
            # Use search term (must be non-empty)
            if [[ -z "$search_term" ]] || [[ "$search_term" == "null" ]]; then
                failed_secrets+=("$env_var (missing search or id)")
                continue
            fi
            secret_value=$(get_secret_field "$search_term" "$field") || {
                failed_secrets+=("$env_var (not found)")
                continue
            }
        fi
        
        if [[ -z "$secret_value" ]]; then
            failed_secrets+=("$env_var (empty value)")
            continue
        fi
        
        # Write based on mode
        if [[ "$write_mode" == "merge" ]]; then
            upsert_env_merge "$env_file" "$env_var" "$secret_value"
        else
            new_content="${new_content}${env_var}=${secret_value}"$'\n'
        fi
        
        updated_count=$((updated_count + 1))
    done
    
    # Write replace mode content
    if [[ "$write_mode" == "replace" ]]; then
        printf '%s' "$new_content" > "$env_file"
    fi
    
    # Set secure permissions
    chmod 600 "$env_file" 2>/dev/null || true
    
    echo "Populated $env_file: $updated_count secrets ($write_mode mode)"
    
    if [[ ${#failed_secrets[@]} -gt 0 ]]; then
        echo "Failed retrievals:" >&2
        for failed in "${failed_secrets[@]}"; do
            echo "  $failed" >&2
        done
        return 1
    fi
    
    return 0
}

# ============================================================================
# Runtime Injection (Ephemeral)
# ============================================================================

inject_env_from_map() {
    local map_file="${1:-$DEFAULT_MAP_FILE}"
    local command="${2:-}"
    
    local config_json
    config_json=$(parse_mapping_file "$map_file") || return 1
    
    local write_mode
    write_mode=$(jq -r '.write_mode' <<<"$config_json")
    
    if [[ "$write_mode" != "ephemeral" ]]; then
        echo "Warning: write_mode should be 'ephemeral' for injection." >&2
    fi
    
    # Build environment variables
    local env_vars=() failed_secrets=()
    
    jq -c '.secrets[]?' <<<"$config_json" | while read -r secret_map; do
        local env_var field source item_id search_term secret_value
        
        env_var=$(jq -r '.env' <<<"$secret_map")
        source=$(jq -r '.source // "item_field"' <<<"$secret_map")
        field=$(jq -r '.field // "password"' <<<"$secret_map")
        item_id=$(jq -r '.id // ""' <<<"$secret_map")
        search_term=$(jq -r '.search // ""' <<<"$secret_map")
        
        if [[ -n "$item_id" ]] && [[ "$item_id" != "null" ]]; then
            secret_value=$(get_secret_by_id "$item_id" "$field") || {
                failed_secrets+=("$env_var")
                continue
            }
        else
            if [[ -z "$search_term" ]] || [[ "$search_term" == "null" ]]; then
                failed_secrets+=("$env_var (missing search/id)")
                continue
            fi
            secret_value=$(get_secret_field "$search_term" "$field") || {
                failed_secrets+=("$env_var")
                continue
            }
        fi
        
        if [[ -z "$secret_value" ]]; then
            failed_secrets+=("$env_var (empty)")
            continue
        fi
        
        env_vars+=("${env_var}=${secret_value}")
    done
    
    if [[ ${#failed_secrets[@]} -gt 0 ]]; then
        echo "Failed to retrieve secrets: ${failed_secrets[*]}" >&2
        return 1
    fi
    
    # If no command, output export statements
    if [[ -z "$command" ]]; then
        for var in "${env_vars[@]}"; do
            echo "export $var"
        done
        return 0
    fi
    
    # Create temporary env file and run command
    local temp_env
    temp_env=$(mktemp)
    chmod 600 "$temp_env"
    
    for var in "${env_vars[@]}"; do
        echo "export $var" >> "$temp_env"
    done
    
    # Source and execute
    source "$temp_env"
    rm -f "$temp_env"
    
    # Run with cleanup trap
    trap 'bitwarden_lock' EXIT
    
    bash -c "$command"
    local exit_code=$?
    
    # Cleanup env vars
    for var in "${env_vars[@]}"; do
        unset "${var%%=*}" 2>/dev/null || true
    done
    
    return $exit_code
}

# ============================================================================
# Legacy Functions (backward compatibility)
# ============================================================================

populate_legacy() {
    local env_file="${1:-$DEFAULT_ENV_FILE}"
    shift
    local IFS=','
    local secrets=($*)
    
    if [[ ${#secrets[@]} -eq 0 ]]; then
        echo "Error: At least one secret name required" >&2
        return 1
    fi
    
    backup_env_file "$env_file"
    
    ensure_session || return 1
    
    local content="" failed=()
    
    for secret_name in "${secrets[@]}"; do
        local value
        value=$(get_secret_field "$secret_name" "password") || {
            failed+=("$secret_name")
            continue
        }
        
        local var_name
        var_name=$(echo "$secret_name" | tr '[:lower:]' '[:upper:]' | tr ' -' '__')
        content="${content}${var_name}=${value}"$'\n'
    done
    
    printf '%s' "$content" > "$env_file"
    chmod 600 "$env_file" 2>/dev/null || true
    
    echo "Populated $env_file with $(( ${#secrets[@]} - ${#failed[@]} )) secrets"
    
    if [[ ${#failed[@]} -gt 0 ]]; then
        echo "Failed: ${failed[*]}" >&2
        return 1
    fi
    
     return 0
 }
 
 # ============================================================================
 # Main Command Dispatcher
 # ============================================================================

case "${1:-help}" in
    # Mapping-file commands
    populate-env-from-map|populate-from-map)
        shift
        populate_from_map "$@"
        ;;
     inject-env|inject)
         shift
         map_file="$DEFAULT_MAP_FILE"
         command=""
         
         # Optional map_file as first positional (if not '--')
         if [[ $# -gt 0 ]] && [[ "$1" != "--" ]]; then
             map_file="$1"
             shift
         fi
         
         # Optional '--' followed by command
         if [[ $# -gt 0 ]] && [[ "$1" == "--" ]]; then
             shift
             command="$*"
         fi
         
         inject_env_from_map "$map_file" "$command"
         ;;
     # Legacy commands
     get-secret)
         shift
         name=""
         field="${2:-password}"
         while [[ $# -gt 0 ]]; do
             case $1 in
                 --name|-n) name="$2"; shift 2 ;;
                 --field|-f) field="$2"; shift 2 ;;
                 *) shift ;;
             esac
         done
         [[ -z "$name" ]] && { echo "Error: --name required" >&2; exit 1; }
         field="${field:-password}"
         get_secret_field "$name" "$field"
         ;;
     list-secrets)
         shift
         search=""
         while [[ $# -gt 0 ]]; do
             case $1 in
                 --search|-s) search="$2"; shift 2 ;;
                 *) shift ;;
             esac
         done
         list_items "$search"
         ;;
     get-login)
         shift
         service=""
         while [[ $# -gt 0 ]]; do
             case $1 in
                 --service|-s) service="$2"; shift 2 ;;
                 *) shift ;;
             esac
         done
         [[ -z "$service" ]] && { echo "Error: --service required" >&2; exit 1; }
         ensure_session || exit 1
         $BW_CMD get item "$service" --session "$BW_SESSION" 2>/dev/null | jq '{
             name: .name,
             username: .login.username,
             password: .login.password,
             uri: .login.uris[0].uri
         }'
         ;;
     generate-password)
         shift
         length=32
         while [[ $# -gt 0 ]]; do
             case $1 in
                 --length|-l) length="$2"; shift 2 ;;
                 *) shift ;;
             esac
         done
         $BW_CMD generate --length "$length" --uppercase --numbers --special
         ;;
    unlock)
        shift
        bitwarden_unlock
        ;;
    lock)
        bitwarden_lock
        ;;
    status)
        if ensure_session 2>/dev/null; then
            $BW_CMD status --session "$BW_SESSION" 2>/dev/null | jq '{
                server: .server,
                lastSync: .lastSync,
                user: .userEmail,
                vaultStatus: .status
            }' || echo '{"status": "unlocked"}'
        else
            echo '{"status": "locked"}'
        fi
        ;;
     login)
         bitwarden_login
         ;;
         
     create-template)
         shift
         mode="password-manager"
         output="$DEFAULT_MAP_FILE"
         
         while [[ $# -gt 0 ]]; do
             case "$1" in
                 --mode|-m) mode="$2"; shift 2 ;;
                 --output|-o) output="$2"; shift 2 ;;
                 *) echo "Unknown option: $1" >&2; exit 1 ;;
             esac
         done
         
         # Generate template
         if [[ "$mode" == "secrets-manager" ]]; then
             echo "Note: This skill supports Password Manager only. Use mode 'password-manager'." >&2
             mode="password-manager"
         fi
         
         template=$(jq -n \
             --arg env_file ".env" \
             --argjson create_backup true \
             --arg write_mode "merge" \
             '{
                 env_file: $env_file,
                 create_backup: $create_backup,
                 write_mode: $write_mode,
                 secrets: [
                     {
                         env: "EXAMPLE_API_KEY",
                         source: "item_field",
                         search: "Example Service API Key",
                         field: "password"
                     }
                 ]
             }')
         
          printf '%s\n' "$template" > "$output"
          chmod 600 "$output"
          
          echo "Created mapping template: $output"
         echo "NOTE: This skill uses Bitwarden Password Manager (free plan)."
         ;;
         
     # Help
     help|--help|-h|setup)
        cat << 'EOF'
Bitwarden Secrets Skill - Free Password Manager Edition

WORKFLOW (CLI-based):
  1. Login with API key:         bw login --apikey --nointeraction
  2. Unlock with master password via BW_PASSWORD env var
  3. BW_SESSION is used for all vault operations
  4. Lock when finished:          bw lock

REQUIRED ENVIRONMENT VARIABLES:
  BW_CLIENTID        - Your Bitwarden API key client ID
  BW_CLIENTSECRET    - Your Bitwarden API key client secret
  BW_PASSWORD        - Your Bitwarden master password (for unlock)
OPTIONAL:
  BW_SERVER_URL      - Self-hosted Bitwarden server URL

IMPORTANT:
  - API key login authenticates the CLI session but does NOT replace unlock.
  - You must unlock the vault to read secrets.
  - The agent will have access to your personal vault - use narrow lookups only.
  - This is a convenience automation, not a least-privilege secrets platform.

 NEW COMMANDS:
   populate-env-from-map [file]   Populate .env from bitwarden-env-map.json
   inject-env [file] [-- command] Inject secrets and run command (no .env written)
   create-template [--mode password-manager] [--output file]
                                   Create mapping file template

LEGACY COMMANDS:
  get-secret --name <name> [--field password|username|note|notes|uri|<custom>]
  list-secrets [--search <query>]
  get-login --service <name>
  generate-password [--length <n>]
  unlock
  lock
  status
  login

MAPPING FILE (bitwarden-env-map.json):
{
  "env_file": ".env",
  "create_backup": true,
  "write_mode": "merge",
  "secrets": [
    {
      "env": "OPENAI_API_KEY",
      "source": "item_field",
      "id": "optional-exact-item-uuid",
      "search": "OpenAI API Key",
      "field": "password"
    }
  ]
}

FIELD TYPES:
  password  → login.password
  username  → login.username
  note/notes → item notes
  uri       → first login.uri
  <other>   → custom field with that name

SECURITY RULES:
  - Never commit .env files
  - Only retrieve specific needed secrets
  - Backup .env before overwriting (configurable)
  - .env created with 600 permissions
  - Vault auto-locks after operations when using inject mode
  - Never print secret values except to target file/process

EXAMPLES:
  # Populate .env from mapping
  bitwarden.sh populate-env-from-map
  
  # Run with injection (no .env written)
  bitwarden.sh inject-env -- npm start
  
  # Legacy: get specific secret
  bitwarden.sh get-secret --name "My API Key" --field password

EOF
        ;;
    *)
        echo "Unknown command: $1. Run '$0 help' for usage." >&2
        exit 1
        ;;
esac

#!/bin/bash
# Secure Bitwarden Environment Setup for AI Agents
# Source this file before running AI agents that need API keys
# Usage: source ~/.bash_secrets

# ============================================================================
# BITWARDEN SECRETS LOADER
# ============================================================================
# This script securely loads API keys and secrets from Bitwarden vault
# into environment variables for AI agents to use during code generation.
#
# SECURITY NOTES:
# - Never commit this file or .env files with real secrets
# - Secrets stay in Bitwarden vault, only loaded at runtime
# - Session expires when shell closes
# - Add .bash_secrets to .gitignore
# ============================================================================

# Check if Bitwarden CLI is installed
if ! command -v bw &> /dev/null; then
    echo "⚠️  Bitwarden CLI not found. Install with:"
    echo "   sudo snap install bw"
    echo "   or: npm install -g @bitwarden/cli"
    return 1
fi

# Function to get secret from Bitwarden
_bw_get_secret() {
    local item_name="$1"
    local field="${2:-password}"
    local pass_file="$HOME/dotfiles/secrets/.bw_master_password"

    # Ensure vault is unlocked
    if ! bw status | grep -q "Unlocked"; then
        # Try non-interactive unlock first
        if [ -f "$pass_file" ]; then
            chmod 600 "$pass_file" 2>/dev/null || true
            export BW_SESSION=$(bw unlock --raw < "$pass_file" 2>/dev/null)
        fi
        # Fall back to interactive if needed
        if ! bw status 2>/dev/null | grep -q '"status":"unlocked"'; then
            echo "🔐 Unlocking Bitwarden vault..."
            export BW_SESSION=$(bw unlock --raw 2>/dev/null)
            if [ -z "$BW_SESSION" ]; then
                echo "❌ Failed to unlock vault. Check your master password."
                return 1
            fi
        fi
    fi
    
    # Retrieve secret
    bw get "$field" "$item_name" 2>/dev/null
}

# Function to load API keys
load_api_keys() {
    echo "🔐 Loading API keys from Bitwarden..."
    
    # OpenAI
    OPENAI_API_KEY=$(_bw_get_secret "API Keys/OpenAI API Key")
    [ -n "$OPENAI_API_KEY" ] && export OPENAI_API_KEY && echo "✓ OPENAI_API_KEY"
    
    # Anthropic/Claude
    ANTHROPIC_API_KEY=$(_bw_get_secret "API Keys/Anthropic API Key")
    [ -n "$ANTHROPIC_API_KEY" ] && export ANTHROPIC_API_KEY && echo "✓ ANTHROPIC_API_KEY"
    
    # GitHub
    GITHUB_TOKEN=$(_bw_get_secret "External Services/GitHub Token")
    [ -n "$GITHUB_TOKEN" ] && export GITHUB_TOKEN && echo "✓ GITHUB_TOKEN"
    
    # GitLab
    GITLAB_TOKEN=$(_bw_get_secret "External Services/GitLab Token")
    [ -n "$GITLAB_TOKEN" ] && export GITLAB_TOKEN && echo "✓ GITLAB_TOKEN"
    
    # AWS
    AWS_ACCESS_KEY_ID=$(_bw_get_secret "Cloud Credentials/AWS Access Key ID")
    [ -n "$AWS_ACCESS_KEY_ID" ] && export AWS_ACCESS_KEY_ID && echo "✓ AWS_ACCESS_KEY_ID"
    
    AWS_SECRET_ACCESS_KEY=$(_bw_get_secret "Cloud Credentials/AWS Secret Key")
    [ -n "$AWS_SECRET_ACCESS_KEY" ] && export AWS_SECRET_ACCESS_KEY && echo "✓ AWS_SECRET_ACCESS_KEY"
    
    # Database URLs
    DEV_DATABASE_URL=$(_bw_get_secret "Database Credentials/Development PostgreSQL" "notes")
    [ -n "$DEV_DATABASE_URL" ] && export DEV_DATABASE_URL && echo "✓ DEV_DATABASE_URL"
    
    PROD_DATABASE_URL=$(_bw_get_secret "Database Credentials/Production PostgreSQL" "notes")
    [ -n "$PROD_DATABASE_URL" ] && export PROD_DATABASE_URL && echo "✓ PROD_DATABASE_URL (PRODUCTION!)"
    
    echo ""
    echo "✅ API keys loaded. Ready for AI agent coding."
}

# Function to load specific secret
load_secret() {
    local name="$1"
    local env_var="${2:-$1}"
    local field="${3:-password}"
    
    local value=$(_bw_get_secret "$name" "$field")
    if [ -n "$value" ]; then
        export "$env_var"="$value"
        echo "✓ $env_var loaded from '$name'"
    else
        echo "⚠️  Could not load '$name'"
        return 1
    fi
}

# Function to check Bitwarden status
check_bitwarden() {
    echo "🔐 Bitwarden Status:"
    bw status
}

# Function to list available secrets
list_secrets() {
    local category="${1:-API Keys}"
    echo "📋 Available secrets in '$category':"
    bw list items --search "$category" | jq -r '.[].name' 2>/dev/null || \
    bw list items --search "$category" | grep "name" || \
    echo "Run: bw list items --search \"$category\""
}

# Quick setup for common development environment
setup_dev_env() {
    echo "🚀 Setting up development environment..."
    load_api_keys
    
    # Additional dev tools
    NPM_TOKEN=$(_bw_get_secret "Package Registries/NPM Token")
    [ -n "$NPM_TOKEN" ] && export NPM_TOKEN && echo "✓ NPM_TOKEN"
    
    DOCKER_HUB_TOKEN=$(_bw_get_secret "Package Registries/Docker Hub Token")
    [ -n "$DOCKER_HUB_TOKEN" ] && export DOCKER_HUB_TOKEN && echo "✓ DOCKER_HUB_TOKEN"
    
    # Python
    PYPI_TOKEN=$(_bw_get_secret "Package Registries/PyPI Token")
    [ -n "$PYPI_TOKEN" ] && export PYPI_TOKEN && echo "✓ PYPI_TOKEN"
    
    echo ""
    echo "✅ Development environment ready!"
    echo ""
    echo "Loaded variables:"
    env | grep -E "^(OPENAI|ANTHROPIC|GITHUB|GITLAB|AWS|DEV_DATABASE|NPM|DOCKER|PYPI)" | cut -d= -f1 | sed 's/^/  - /'
}

# ============================================================================
# AI AGENT INTEGRATION
# ============================================================================

# Function to export secrets for AI agents in a controlled way
export_for_agent() {
    local agent_name="${1:-ai-agent}"
    local output_file="/tmp/${agent_name}_env.sh"
    
    echo "# Auto-generated environment for $agent_name" > "$output_file"
    echo "# Generated: $(date)" >> "$output_file"
    echo "" >> "$output_file"
    
    # Export only non-production secrets for safety
    [ -n "$OPENAI_API_KEY" ] && echo "export OPENAI_API_KEY='$OPENAI_API_KEY'" >> "$output_file"
    [ -n "$ANTHROPIC_API_KEY" ] && echo "export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'" >> "$output_file"
    [ -n "$GITHUB_TOKEN" ] && echo "export GITHUB_TOKEN='$GITHUB_TOKEN'" >> "$output_file"
    [ -n "$DEV_DATABASE_URL" ] && echo "export DATABASE_URL='$DEV_DATABASE_URL'" >> "$output_file"
    
    echo "✅ Environment exported to: $output_file"
    echo "   Source it in agent: source $output_file"
    
    # Set restrictive permissions
    chmod 600 "$output_file"
}

# Function to export all API keys as JSON
bw_export_keys() {
    local format="${1:-structured}"  # structured, flat, or env
    local output_file="${2:-}"
    
    local skill_dir="$HOME/dotfiles/ai/skills/bitwarden_secrets"
    
    # Ensure vault is unlocked
    ensure_unlocked
    
    case "$format" in
        structured)
            echo "🔐 Exporting all API keys (structured JSON)..."
            if [ -n "$output_file" ]; then
                python3 "$skill_dir/bitwarden_secrets.py" export > "$output_file"
                echo "✅ Exported to: $output_file"
            else
                python3 "$skill_dir/bitwarden_secrets.py" export
            fi
            ;;
        flat)
            echo "🔐 Exporting all API keys (flat dictionary)..."
            if [ -n "$output_file" ]; then
                python3 "$skill_dir/bitwarden_secrets.py" export-flat > "$output_file"
                echo "✅ Exported to: $output_file"
                echo "   Use: jq -r '.OPENROUTER_API_KEY' $output_file"
            else
                python3 "$skill_dir/bitwarden_secrets.py" export-flat
            fi
            ;;
        env)
            echo "🔐 Exporting all API keys (shell format)..."
            if [ -n "$output_file" ]; then
                python3 "$skill_dir/bitwarden_secrets.py" export-env > "$output_file"
                chmod 600 "$output_file"
                echo "✅ Exported to: $output_file"
                echo "   Source with: source $output_file"
            else
                python3 "$skill_dir/bitwarden_secrets.py" export-env
            fi
            ;;
        *)
            echo "Usage: bw_export_keys [structured|flat|env] [output_file]"
            echo ""
            echo "Examples:"
            echo "  bw_export_keys flat ~/api_keys.json"
            echo "  bw_export_keys env /tmp/exports.sh"
            echo "  bw_export_keys structured | jq '.api_keys[0].item_name'"
            return 1
            ;;
    esac
}

# Quick function to get a specific API key from exported JSON
bw_get_key() {
    local key_name="$1"
    local json_file="${2:-$HOME/.bw_api_keys.json}"
    
    if [ -z "$key_name" ]; then
        echo "Usage: bw_get_key <KEY_NAME> [json_file]"
        echo "Example: bw_get_key OPENROUTER_API_KEY"
        return 1
    fi
    
    # Export if file doesn't exist
    if [ ! -f "$json_file" ]; then
        echo "🔐 API keys file not found. Exporting..."
        bw_export_keys flat "$json_file"
    fi
    
    # Get the key
    jq -r ".${key_name}" "$json_file" 2>/dev/null || echo "Key not found: $key_name"
}

# ============================================================================
# SAFETY FEATURES
# ============================================================================

# Warn if production secrets are loaded
if [ -n "$PROD_DATABASE_URL" ]; then
    echo "⚠️  WARNING: Production database credentials are loaded!"
    echo "   Be extremely careful with database operations."
fi

# Clear secrets function (call before exiting)
clear_secrets() {
    echo "🧹 Clearing loaded secrets..."
    unset OPENAI_API_KEY ANTHROPIC_API_KEY GITHUB_TOKEN GITLAB_TOKEN
    unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
    unset DEV_DATABASE_URL PROD_DATABASE_URL
    unset NPM_TOKEN DOCKER_HUB_TOKEN PYPI_TOKEN
    unset BW_SESSION
    echo "✅ Secrets cleared from environment"
}

# Auto-clear on exit (optional - uncomment if desired)
# trap clear_secrets EXIT

# ============================================================================
# USAGE EXAMPLES
# ============================================================================
# 
# Load all API keys:
#   $ load_api_keys
#
# Load specific secret:
#   $ load_secret "API Keys/OpenAI API Key" "OPENAI_API_KEY"
#
# Setup full dev environment:
#   $ setup_dev_env
#
# Export for AI agent:
#   $ export_for_agent "windsurf"
#
# Clear all secrets:
#   $ clear_secrets
#
# Check Bitwarden status:
#   $ check_bitwarden
#
# List available secrets:
#   $ list_secrets "API Keys"

# ============================================================================

# If run directly (not sourced), show help
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    echo "🔐 Bitwarden Secrets Loader for AI Agents"
    echo ""
    echo "This script should be SOURCED, not executed:"
    echo "  source ${BASH_SOURCE[0]}"
    echo ""
    echo "Available functions:"
    echo "  load_api_keys      - Load common API keys"
    echo "  setup_dev_env      - Load full development environment"
    echo "  load_secret <name> [env_var] [field] - Load specific secret"
    echo "  export_for_agent   - Export secrets for AI agent"
    echo "  clear_secrets      - Remove all secrets from environment"
    echo "  check_bitwarden    - Check vault status"
    echo "  list_secrets       - List available secrets"
    echo ""
    echo "Example:"
    echo "  source ${BASH_SOURCE[0]}"
    echo "  load_api_keys"
    exit 1
fi

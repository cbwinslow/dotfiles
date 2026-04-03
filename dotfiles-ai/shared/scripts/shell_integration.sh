# AI Skills System - Shell Integration
# Includes Bitwarden integration for secure secret management
# Add this to your ~/.zshrc or ~/.bashrc
# Location: ~/dotfiles/ai/scripts/shell_integration.sh

# =============================================================================
# Environment Variables
# =============================================================================

export AI_SKILLS_ROOT="$HOME/dotfiles/ai"
export LETTA_SERVER_URL="${LETTA_SERVER_URL:-http://localhost:8283}"

# =============================================================================
# Agent Aliases (with automatic global rules loading)
# =============================================================================

# OpenCode with global rules
alias opencode="opencode --init-rules \$AI_SKILLS_ROOT/global_rules 2>/dev/null || opencode"

# Cline (uses centralized config via symlink)
alias cline="cline"

# Gemini CLI with global rules
alias gemini="gemini --init-rules \$AI_SKILLS_ROOT/global_rules 2>/dev/null || gemini"

# KiloCode
alias kilocode="kilocode"

# =============================================================================
# Letta Memory Management Aliases
# =============================================================================

alias memory-cli="letta-memory-cli"
alias letta-health="letta-memory-cli health"
alias letta-stats="letta-memory-cli stats"
alias letta-backup="letta-memory-cli backup"
alias letta-search="letta-memory-cli search"
alias letta-save="letta-memory-cli save"
alias letta-list="letta-memory-cli list"

# Quick memory shortcuts
alias save-note="letta-memory-cli save --type generic --memory-type archival --tags note"
alias save-decision="letta-memory-cli save --type decision"
alias save-action="letta-memory-cli save --type action_item"
alias find-memory="letta-memory-cli search --query"

# =============================================================================
# AI Config Management
# =============================================================================

alias ai-validate="python3 \$AI_SKILLS_ROOT/scripts/validate_configs.py"
alias ai-symlinks="bash \$AI_SKILLS_ROOT/scripts/create_symlinks.sh"
alias ai-status="python3 \$AI_SKILLS_ROOT/scripts/monitor_system.py --report"

# =============================================================================
# Quick Navigation
# =============================================================================

alias ai-cd="cd \$AI_SKILLS_ROOT"
alias ai-agents="cd \$AI_SKILLS_ROOT/agents"
alias ai-skills="cd \$AI_SKILLS_ROOT/skills"
alias ai-tools="cd \$AI_SKILLS_ROOT/tools"
alias ai-base="cd \$AI_SKILLS_ROOT/base"

# =============================================================================
# Utility Functions
# =============================================================================

# Search all agent memories
search-all-agents() {
    if [ -z "$1" ]; then
        echo "Usage: search-all-agents <query>"
        return 1
    fi
    python3 -c "
from letta_integration import LettaIntegration
letta = LettaIntegration()
results = letta.search_all_agents('$1')
import json
print(json.dumps(results, indent=2))
"
}

# Quick health check for all systems
ai-health() {
    echo "=== AI Skills System Health Check ==="
    echo ""
    
    echo "1. Letta Server:"
    letta-health
    echo ""
    
    echo "2. Environment Variables:"
    echo "   AI_SKILLS_ROOT: $AI_SKILLS_ROOT"
    echo "   LETTA_SERVER_URL: $LETTA_SERVER_URL"
    echo "   OPENROUTER_API_KEY: ${OPENROUTER_API_KEY:+[SET]}"
    echo "   LETTA_API_KEY: ${LETTA_API_KEY:+[SET]}"
    echo ""
    
    echo "3. Configuration Validation:"
    ai-validate --verbose
}

# Backup all AI memories
ai-backup-all() {
    echo "Backing up all AI memories..."
    letta-backup
    echo "Backup complete!"
}

# =============================================================================
# Auto-initialization (run on shell start)
# =============================================================================

_ai_init() {
    # Check if Letta server is accessible
    if command -v curl &> /dev/null; then
        curl -s -o /dev/null -w "" "$LETTA_SERVER_URL/v1/health" 2>/dev/null || \
            echo "[AI] Warning: Letta server not accessible at $LETTA_SERVER_URL"
    fi
}

# Run initialization (uncomment to enable)
# _ai_init

# =============================================================================
# Bitwarden Integration
# =============================================================================

# Bitwarden shortcuts
alias bw-unlock='eval $(bw unlock --raw) && export BW_SESSION && echo "Vault unlocked"'
alias bw-lock='bw lock && unset BW_SESSION && echo "Vault locked"'
alias bw-status='bw status | jq .'

# Quick secret access via Bitwarden
bw-get() {
    bw get item "$1" --session "$BW_SESSION" | jq -r '.login.password // .fields[0].value // empty'
}

# Auto-populate .env from Bitwarden
bw-env() {
    local env_file="${1:-.env}"
    shift
    $AI_SKILLS_ROOT/skills/bitwarden/bitwarden.sh populate-env --env-file "$env_file" --secrets "$@"
}

# List Bitwarden secrets
bw-list() {
    bw list items --session "$BW_SESSION" | jq -r '.[].name'
}

# =============================================================================
# Help
# =============================================================================

ai-help() {
    cat << EOF
AI Skills System - Quick Reference

Navigation:
  ai-cd          Go to AI skills root
  ai-agents      Go to agents directory
  ai-skills      Go to skills directory
  ai-tools       Go to tools directory

Letta Memory:
  letta-health   Check server health
  letta-stats    Get memory statistics
  letta-backup   Backup memories
  letta-search   Search memories
  letta-save     Save memory
  save-note      Quick save note
  save-decision  Save important decision
  save-action    Save action item
  find-memory    Search for memory

Bitwarden Secrets:
  bw-unlock      Unlock Bitwarden vault
  bw-lock        Lock vault
  bw-status      Show status
  bw-get <name>  Get secret by name
  bw-list        List all secrets
  bw-env         Populate .env from secrets

Management:
  ai-validate    Validate configurations
  ai-symlinks    Create/update symlinks
  ai-status      System status report
  ai-health      Full health check
  ai-backup-all  Backup all memories

Search:
  search-all-agents <query>  Search across all agents

EOF
}

alias ai-help="ai-help"

echo "[AI] AI Skills System loaded. Type 'ai-help' for commands."

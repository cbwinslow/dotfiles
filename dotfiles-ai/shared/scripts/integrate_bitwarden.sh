#!/bin/bash
# Integrate Bitwarden skill into all AI agents
# Uses official @bitwarden/mcp-server + fallback bitwarden.sh script

set -e

AI_DIR="/home/cbwinslow/dotfiles/ai"
SKILL="$AI_DIR/skills/bitwarden/bitwarden.sh"
CONFIG_DIR="$AI_DIR/config/agents"
MCP_CONFIG="$AI_DIR/config/mcp"

echo "=== Bitwarden Integration for AI Agents ==="
echo ""

# Make scripts executable
chmod +x "$SKILL"

# Update base_agent.yaml
if ! grep -q "bitwarden" "$AI_DIR/base/base_agent.yaml"; then
    echo "Adding bitwarden skill to base_agent.yaml..."
    sed -i 's/  - cbw_rag/  - bitwarden_secrets\n  - cbw_rag/' "$AI_DIR/base/base_agent.yaml"
fi

# Create MCP server config directory
mkdir -p "$MCP_CONFIG"

# Create MCP server config for agents that support it
cat > "$MCP_CONFIG/bitwarden-mcp.json" << 'EOF'
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
EOF
echo "  Created: $MCP_CONFIG/bitwarden-mcp.json"

# Generate agent configs
mkdir -p "$CONFIG_DIR"

for agent in cline opencode codex gemini kilocode openclaw qwen vscode windsurf; do
    config_file="$CONFIG_DIR/${agent}.yaml"
    cat > "$config_file" << EOF
# Config for $agent - Bitwarden skill
# Uses official MCP server when available, falls back to bitwarden.sh

mcp_servers:
  bitwarden:
    command: npx
    args: ["-y", "@bitwarden/mcp-server"]
    env:
      BW_SESSION: "\${BW_SESSION}"
    description: "Official Bitwarden MCP server for vault access"

skills:
  - name: bitwarden
    script: $SKILL
    description: "Fallback script for Bitwarden access"

# Agent instructions for Bitwarden
instructions: |
  You have access to Bitwarden for secret management.

  ## Using the MCP Server (Preferred)
  If you have MCP tools available, use the bitwarden MCP server.
  It provides tools like: list-items, get-item, create-item, etc.

  ## Using the Shell Script (Fallback)
  If MCP is not available, use: $SKILL

  To unlock:
    $SKILL unlock <password> [totp]

  To get secrets:
    $SKILL get-secret --name "Secret Name"

  To list secrets:
    $SKILL list-secrets

  To populate .env:
    $SKILL populate-env --env-file .env --secrets "Key1,Key2"

  To interactively unlock:
    $SKILL interactive

  ## Security Rules
  - NEVER log or display passwords
  - Tell user to run 'lock' when done
  - Use environment variables, not hard-coded values
  - Session stored in ~/.config/bitwarden-ai/session.env
EOF
    echo "  Generated: $config_file"
done

# Add aliases to shell config
SHELL_RC="$HOME/.zshrc"
[ ! -f "$SHELL_RC" ] && SHELL_RC="$HOME/.bashrc"

if ! grep -q "# Bitwarden AI Agent Skill" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" << 'EOF'

# Bitwarden AI Agent Skill
# Official MCP server: @bitwarden/mcp-server
# Fallback script: ~/dotfiles/ai/skills/bitwarden/bitwarden.sh
alias bw='~/dotfiles/ai/skills/bitwarden/bitwarden.sh'
alias bw-unlock='~/dotfiles/ai/skills/bitwarden/bitwarden.sh unlock'
alias bw-lock='~/dotfiles/ai/skills/bitwarden/bitwarden.sh lock'
alias bw-get='~/dotfiles/ai/skills/bitwarden/bitwarden.sh get-secret'
alias bw-list='~/dotfiles/ai/skills/bitwarden/bitwarden.sh list-secrets'
alias bw-env='~/dotfiles/ai/skills/bitwarden/bitwarden.sh populate-env'
alias bw-status='~/dotfiles/ai/skills/bitwarden/bitwarden.sh status'
alias bw-interactive='~/dotfiles/ai/skills/bitwarden/bitwarden.sh interactive'
alias bw-setup='~/dotfiles/ai/skills/bitwarden/bitwarden.sh setup'
alias bw-login='~/dotfiles/ai/skills/bitwarden/bitwarden.sh login'
alias bw-generate='~/dotfiles/ai/skills/bitwarden/bitwarden.sh generate-password'
EOF
    echo "  Added aliases to $SHELL_RC"
fi

echo ""
echo "=== Testing Bitwarden Skill ==="
echo ""

# Test syntax
if bash -n "$SKILL"; then
    echo "  bitwarden.sh: Syntax OK"
else
    echo "  bitwarden.sh: SYNTAX ERROR"
fi

# Test status
echo "  Vault status:"
$SKILL status 2>&1 || true

# Test help
echo "  Help output:"
$SKILL help 2>&1 | grep -c "Commands:" && echo "  Help: OK"

echo ""
echo "=== Integration Complete ==="
echo ""
echo "Two access methods available:"
echo ""
echo "1. Official MCP Server (preferred for agents):"
echo "   npx -y @bitwarden/mcp-server"
echo "   Config: $MCP_CONFIG/bitwarden-mcp.json"
echo ""
echo "2. Shell Script (fallback):"
echo "   $SKILL <command>"
echo ""
echo "Usage:"
echo "  bw unlock <password> [totp]"
echo "  bw get-secret --name 'API Key'"
echo "  bw populate-env --env-file .env --secrets 'Key1,Key2'"
echo "  bw interactive  (walks user through unlock)"
echo "  bw login  (API key login, bypasses 2FA)"

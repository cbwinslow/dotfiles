#!/bin/bash
# Create Symlinks Script
# Creates symlinks from dotfile locations to centralized AI configs
# Location: ~/dotfiles/ai/scripts/create_symlinks.sh

set -e

AI_ROOT="$HOME/dotfiles/ai"
AGENTS_DIR="$AI_ROOT/agents"

echo "Creating symlinks for AI agent configurations..."

# Backup existing directories
backup_existing() {
    local path="$1"
    if [ -e "$path" ] && [ ! -L "$path" ]; then
        local backup_name="${path}.backup.$(date +%Y%m%d-%H%M%S)"
        echo "Backing up $path to $backup_name"
        mv "$path" "$backup_name"
    fi
}

# Create symlink for OpenCode
echo "Setting up OpenCode..."
backup_existing "$HOME/.opencode/agents/main"
mkdir -p "$HOME/.opencode/agents"
ln -sf "$AGENTS_DIR/opencode" "$HOME/.opencode/agents/main"

# Create symlink for Cline
echo "Setting up Cline..."
backup_existing "$HOME/.cline"
# Keep .cline as data directory symlink
mkdir -p "$AI_ROOT/.cline/data"
ln -sf "$AI_ROOT/.cline/data" "$HOME/.cline"

# Create symlink for OpenClaw
echo "Setting up OpenClaw..."
if [ -L "$HOME/.openclaw" ]; then
    echo "  OpenClaw symlink already exists"
else
    backup_existing "$HOME/.openclaw"
    ln -sf "$AGENTS_DIR/openclaw/config.yaml" "$HOME/.openclaw"
fi

# Create global rules symlink for all agents
echo "Setting up global rules..."
for agent_dir in "$HOME"/.opencode "$HOME"/.openclaw; do
    if [ -d "$agent_dir" ]; then
        backup_existing "$agent_dir/instructions.md"
        ln -sf "$AI_ROOT/global_rules/agent_init_rules.md" "$agent_dir/instructions.md" 2>/dev/null || true
    fi
done

echo "Symlinks created successfully!"
echo ""
echo "Summary:"
echo "  ~/.opencode/agents/main -> $AGENTS_DIR/opencode"
echo "  ~/.cline -> $AI_ROOT/.cline/data"
echo "  ~/.openclaw/config.yaml -> $AGENTS_DIR/openclaw/config.yaml"
echo ""
echo "Global rules linked:"
echo "  */instructions.md -> $AI_ROOT/global_rules/agent_init_rules.md"

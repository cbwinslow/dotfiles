#!/bin/bash
# Quick setup script for cbw organization tools

echo "Setting up CBW Organization Tools..."

# Make all scripts executable
chmod +x ~/dotfiles/ai/scripts/*.py
chmod +x ~/dotfiles/ai/scripts/*.sh

# Check if shell integration is sourced
if ! grep -q "cbw-shell-integration.sh" ~/.zshrc 2>/dev/null; then
    echo ""
    echo "Add this to your ~/.zshrc:"
    echo "source ~/dotfiles/ai/scripts/cbw-shell-integration.sh"
    echo ""
fi

# Run initial agents.md generation
echo "Generating agents.md files..."
python3 ~/dotfiles/ai/scripts/generate_agents_md.py ~/dotfiles/ai --recursive --depth 4

echo ""
echo "✅ Setup complete!"
echo ""
echo "Available commands:"
echo "  cbw-help 'your question'     - Knowledge base query"
echo "  cbw-pattern                  - Show code patterns"
echo "  cbw-reuse --report           - Find reuse opportunities"
echo "  cbw-tasks --scan             - Scan for TODOs"
echo "  cbw-validate                 - Validate configs"
echo "  cbw-agents-md                - Regenerate agents.md"
echo ""
echo "Key files:"
echo "  ~/dotfiles/ai/AGENT_RULES.md - Rules for AI agents"
echo "  ~/dotfiles/ai/agents.md      - This directory's guide"
echo ""

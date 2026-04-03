#!/bin/bash
# Setup script to enable Letta skills for all AI agents
# Run this once to configure your shell environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="${HOME}/dotfiles"
SKILL_DIR="${DOTFILES_DIR}/ai/skills/letta_integration"

echo "=============================================="
echo "  Letta Skill Auto-Loader Setup"
echo "=============================================="
echo ""

# Create .bashrc if it doesn't exist
if [ ! -f "${HOME}/.bashrc" ]; then
    echo "Creating ~/.bashrc..."
    touch "${HOME}/.bashrc"
fi

# Check if already configured
if grep -q "letta_integration" "${HOME}/.bashrc" 2>/dev/null; then
    echo "✓ Letta loader already configured in .bashrc"
else
    echo "Adding Letta loader to ~/.bashrc..."
    cat >> "${HOME}/.bashrc" << 'EOF'

# Letta AI Skills Auto-Loader
if [ -f ~/dotfiles/ai/skills/letta_integration/shell_loader.sh ]; then
    source ~/dotfiles/ai/skills/letta_integration/shell_loader.sh
fi
EOF
    echo "✓ Added to .bashrc"
fi

# Make scripts executable
echo "Setting up executable permissions..."
chmod +x "${SKILL_DIR}/shell_loader.sh" 2>/dev/null || true
chmod +x "${SKILL_DIR}/agent_initializer.py" 2>/dev/null || true
chmod +x "${DOTFILES_DIR}/ai/packages/letta_integration/test_all_features.py" 2>/dev/null || true

echo "✓ Permissions set"

# Test Python path
echo ""
echo "Testing Python path setup..."
python3 << PYEOF
import sys
sys.path.insert(0, "${HOME}/dotfiles/ai/packages/letta_integration")
try:
    from letta_integration import LettaIntegration
    print("✓ Letta integration importable")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    print("  Note: Install with: pip install letta-client")
PYEOF

echo ""
echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "To activate in current terminal:"
echo "  source ~/.bashrc"
echo ""
echo "Available commands:"
echo "  letta-health     - Check Letta server status"
echo "  letta-agents     - List all agents"
echo "  init_letta_agent - Initialize new agent"
echo "  letta-log        - Log conversation"
echo ""
echo "For any agent to use Letta:"
echo "  source ~/dotfiles/ai/skills/letta_integration/shell_loader.sh"
echo ""

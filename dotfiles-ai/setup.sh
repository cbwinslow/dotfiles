#!/bin/bash
# AI Dotfiles Setup Script
# This script bootstraps the ~/.config/ai directory structure

set -e

DOTFILES_AI="$HOME/dotfiles/ai"
CONFIG_AI="$HOME/.config/ai"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up AI dotfiles structure...${NC}"

# ============================================
# Step 1: Create ~/.config/ai symlink
# ============================================
echo -e "${YELLOW}Step 1: Creating ~/.config/ai symlink...${NC}"

if [ -L "$CONFIG_AI" ]; then
    echo -e "${YELLOW}  ~/.config/ai already exists as symlink${NC}"
elif [ -d "$CONFIG_AI" ]; then
    echo -e "${RED}  Warning: ~/.config/ai exists as directory${NC}"
    echo -e "${YELLOW}  Backing up to ~/.config/ai.backup...${NC}"
    mv "$CONFIG_AI" "$CONFIG_AI.backup.$(date +%Y%m%d%H%M%S)"
    ln -s "$DOTFILES_AI" "$CONFIG_AI"
    echo -e "${GREEN}  Created symlink: ~/.config/ai -> ~/dotfiles/ai${NC}"
else
    ln -s "$DOTFILES_AI" "$CONFIG_AI"
    echo -e "${GREEN}  Created symlink: ~/.config/ai -> ~/dotfiles/ai${NC}"
fi

# ============================================
# Step 2: Create tool-specific symlinks
# ============================================
echo -e "${YELLOW}Step 2: Setting up tool-specific configurations...${NC}"

# Cline CLI
if [ -d "$HOME/.cline" ]; then
    echo -e "${GREEN}  Cline directory exists${NC}"
    if [ ! -L "$HOME/.cline/config.json" ]; then
        ln -sf "$CONFIG_AI/tools/cline.json" "$HOME/.cline/config.json" 2>/dev/null || true
        echo -e "${GREEN}  Linked Cline config${NC}"
    fi
fi

# KiloCode
if [ ! -d "$HOME/.kilocode" ]; then
    mkdir -p "$HOME/.kilocode"
fi
if [ ! -L "$HOME/.kilocode/config.json" ]; then
    ln -sf "$CONFIG_AI/tools/kilocode.json" "$HOME/.kilocode/config.json" 2>/dev/null || true
    echo -e "${GREEN}  Linked KiloCode config${NC}"
fi

# OpenClaw
if [ ! -d "$HOME/.openclaw" ]; then
    mkdir -p "$HOME/.openclaw/skills"
fi
if [ ! -L "$HOME/.openclaw/config.yaml" ]; then
    ln -sf "$CONFIG_AI/tools/openclaw.yaml" "$HOME/.openclaw/config.yaml" 2>/dev/null || true
    echo -e "${GREEN}  Linked OpenClaw config${NC}"
fi

# Symlink skills to OpenClaw
if [ -d "$CONFIG_AI/skills" ]; then
    for skill in "$CONFIG_AI/skills"/*/*; do
        if [ -d "$skill" ]; then
            skill_name=$(basename "$skill")
            if [ ! -L "$HOME/.openclaw/skills/$skill_name" ]; then
                ln -sf "$skill" "$HOME/.openclaw/skills/$skill_name" 2>/dev/null || true
            fi
        fi
    done
    echo -e "${GREEN}  Linked skills to OpenClaw${NC}"
fi

# ============================================
# Step 3: Create logs directory
# ============================================
echo -e "${YELLOW}Step 3: Creating logs directory...${NC}"
mkdir -p "$HOME/.local/state/ai/logs"
echo -e "${GREEN}  Created: ~/.local/state/ai/logs${NC}"

# ============================================
# Step 4: Check environment file
# ============================================
echo -e "${YELLOW}Step 4: Checking environment configuration...${NC}"

if [ -f "$HOME/.env.ai" ]; then
    echo -e "${GREEN}  ~/.env.ai exists${NC}"
else
    echo -e "${YELLOW}  Creating ~/.env.ai from template...${NC}"
    cp "$DOTFILES_AI/.env.example" "$HOME/.env.ai"
    echo -e "${RED}  ⚠️  IMPORTANT: Edit ~/.env.ai and add your API keys!${NC}"
fi

# ============================================
# Step 5: Verify structure
# ============================================
echo -e "${YELLOW}Step 5: Verifying structure...${NC}"

errors=0

# Check critical directories
dirs=("agents" "skills" "tools" "workflows" "configs")
for dir in "${dirs[@]}"; do
    if [ -d "$CONFIG_AI/$dir" ]; then
        echo -e "${GREEN}  ✓ $dir/ exists${NC}"
    else
        echo -e "${RED}  ✗ $dir/ missing${NC}"
        ((errors++))
    fi
done

# Check critical files
files=("config.yaml" ".env.example")
for file in "${files[@]}"; do
    if [ -f "$CONFIG_AI/$file" ]; then
        echo -e "${GREEN}  ✓ $file exists${NC}"
    else
        echo -e "${RED}  ✗ $file missing${NC}"
        ((errors++))
    fi
done

# ============================================
# Step 6: Setup shell integration for auto-loading
# ============================================
echo -e "${YELLOW}Step 6: Setting up shell integration...${NC}"

# Add shell loader to bashrc if not already present
if [ -f "$HOME/.bashrc" ]; then
    if ! grep -q "shell_loader.sh" "$HOME/.bashrc" 2>/dev/null; then
        echo "" >> "$HOME/.bashrc"
        echo "# AI Agent Auto-Loading" >> "$HOME/.bashrc"
        echo "if [ -f \"$CONFIG_AI/skills/shell_loader.sh\" ]; then" >> "$HOME/.bashrc"
        echo "    source \"$CONFIG_AI/skills/shell_loader.sh\"" >> "$HOME/.bashrc"
        echo "fi" >> "$HOME/.bashrc"
        echo -e "${GREEN}  Added shell loader to ~/.bashrc${NC}"
    else
        echo -e "${GREEN}  Shell loader already in ~/.bashrc${NC}"
    fi
fi

# Also add for zsh
if [ -f "$HOME/.zshrc" ]; then
    if ! grep -q "shell_loader.sh" "$HOME/.zshrc" 2>/dev/null; then
        echo "" >> "$HOME/.zshrc"
        echo "# AI Agent Auto-Loading" >> "$HOME/.zshrc"
        echo "if [ -f \"$CONFIG_AI/skills/shell_loader.sh\" ]; then" >> "$HOME/.zshrc"
        echo "    source \"$CONFIG_AI/skills/shell_loader.sh\"" >> "$HOME/.zshrc"
        echo "fi" >> "$HOME/.zshrc"
        echo -e "${GREEN}  Added shell loader to ~/.zshrc${NC}"
    fi
fi

# ============================================
# Step 7: Verify Letta integration
# ============================================
echo -e "${YELLOW}Step 7: Verifying Letta integration...${NC}"

if [ -d "$CONFIG_AI/packages/letta_integration" ]; then
    echo -e "${GREEN}  ✓ Letta integration package exists${NC}"
    
    # Check if autonomous_memory.py exists
    if [ -f "$CONFIG_AI/packages/letta_integration/autonomous_memory.py" ]; then
        echo -e "${GREEN}  ✓ Autonomous memory module ready${NC}"
    else
        echo -e "${YELLOW}  ⚠ autonomous_memory.py not found${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ Letta integration package not found${NC}"
fi

# Check environment variables
if [ -f "$HOME/.env.ai" ]; then
    if grep -q "LETTA_SERVER_URL" "$HOME/.env.ai"; then
        echo -e "${GREEN}  ✓ Letta environment configured${NC}"
    else
        echo -e "${YELLOW}  ⚠ LETTA_SERVER_URL not in ~/.env.ai${NC}"
    fi
fi

# ============================================
# Step 8: Summary
# ============================================
echo ""
echo "============================================"
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✓ Setup complete!${NC}"
else
    echo -e "${YELLOW}⚠ Setup completed with $errors warnings${NC}"
fi
echo "============================================"
echo ""
echo "Letta Memory System:"
echo "  Server: http://localhost:8283"
echo "  Database: PostgreSQL 16 (bare-metal)"
echo "  Auto-load: Enabled for all agents"
echo ""
echo "To verify Letta is running:"
echo "  curl http://localhost:8283/v1/health"
echo ""
echo "Quick test:"
echo "  python3 -c \"from letta_integration.autonomous_memory import get_memory; print(get_memory())\""
echo ""
echo "Available commands:"
echo "  - Cline CLI: Uses ~/.cline/config.json"
echo "  - KiloCode CLI: Uses ~/.kilocode/config.json"
echo "  - OpenClaw: Uses ~/.openclaw/config.yaml"
echo ""
echo "Agent configs available:"
for agent in "$CONFIG_AI/agents"/*.yaml; do
    if [ -f "$agent" ]; then
        name=$(basename "$agent" .yaml)
        echo "  - $name"
    fi
done
echo ""
echo "Skills available:"
find "$CONFIG_AI/skills" -name "SKILL.md" -exec dirname {} \; | xargs -n1 basename | sort -u | head -10 | while read skill; do
    echo "  - $skill"
done
echo ""

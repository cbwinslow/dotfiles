#!/bin/bash
# Fix AI Agent Installations and Symlinks
# Location: ~/dotfiles/ai/scripts/fix_agent_installs.sh

set -e

AI_ROOT="$HOME/dotfiles/ai"
AGENTS_DIR="$AI_ROOT/agents"

echo "=============================================="
echo "  Fixing AI Agent Installations"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Backup and remove incorrect symlinks
fix_symlink() {
    local path="$1"
    local target="$2"
    local type="${3:-dir}"  # dir or file
    
    if [ -L "$path" ]; then
        current=$(readlink "$path")
        if [ "$current" != "$target" ]; then
            log_warn "$path points to $current, fixing..."
            rm "$path"
        fi
    fi
    
    if [ ! -e "$path" ]; then
        if [ "$type" = "dir" ]; then
            mkdir -p "$target"
            ln -sf "$target" "$path"
            log_info "Created directory symlink: $path -> $target"
        else
            ln -sf "$target" "$path"
            log_info "Created file symlink: $path -> $target"
        fi
    else
        log_info "$path already exists"
    fi
}

# Create data directories in AI_ROOT
echo "Step 1: Creating data directories..."
echo "-------------------------------------------"
mkdir -p "$AI_ROOT/.cline/data"
mkdir -p "$AI_ROOT/.gemini/data"
mkdir -p "$AI_ROOT/.openclaw/data"
mkdir -p "$AI_ROOT/.kilocode/data"
mkdir -p "$AI_ROOT/.opencode/data"
mkdir -p "$AI_ROOT/.codex/data"
log_info "Data directories created in $AI_ROOT/"

# Fix symlinks
echo ""
echo "Step 2: Fixing symlinks..."
echo "-------------------------------------------"

# Cline - data directory
fix_symlink "$HOME/.cline" "$AI_ROOT/.cline/data" "dir"

# Gemini - needs to be a directory, not config file
if [ -L "$HOME/.gemini" ]; then
    target=$(readlink "$HOME/.gemini")
    if [[ "$target" == *"config.yaml" ]]; then
        log_warn ".gemini is symlink to config file, fixing..."
        rm "$HOME/.gemini"
    fi
fi
fix_symlink "$HOME/.gemini" "$AI_ROOT/.gemini/data" "dir"

# OpenClaw - needs to be a directory, not config file
if [ -L "$HOME/.openclaw" ]; then
    target=$(readlink "$HOME/.openclaw")
    if [[ "$target" == *"config.yaml" ]]; then
        log_warn ".openclaw is symlink to config file, fixing..."
        rm "$HOME/.openclaw"
    fi
fi
fix_symlink "$HOME/.openclaw" "$AI_ROOT/.openclaw/data" "dir"

# KiloCode - create data directory
fix_symlink "$HOME/.kilocode" "$AI_ROOT/.kilocode/data" "dir"

# OpenCode - keep existing, just ensure data dir exists
mkdir -p "$HOME/.opencode/data"
log_info "OpenCode data directory ensured"

# Codex - create if needed (VS Code extension, may not have CLI)
if command -v codex &> /dev/null; then
    fix_symlink "$HOME/.codex" "$AI_ROOT/.codex/data" "dir"
fi

# Link global rules to agent directories
echo ""
echo "Step 3: Linking global rules..."
echo "-------------------------------------------"

# OpenCode instructions
if [ -d "$HOME/.opencode" ]; then
    if [ ! -L "$HOME/.opencode/instructions.md" ]; then
        ln -sf "$AI_ROOT/global_rules/agent_init_rules.md" "$HOME/.opencode/instructions.md" 2>/dev/null || true
        log_info "Linked global rules to OpenCode"
    fi
fi

# Copy config files to data directories for agents that read from there
echo ""
echo "Step 4: Copying configs to data directories..."
echo "-------------------------------------------"

# Gemini config
if [ -f "$AGENTS_DIR/gemini/config.yaml" ]; then
    cp "$AGENTS_DIR/gemini/config.yaml" "$AI_ROOT/.gemini/data/config.yaml" 2>/dev/null || true
    log_info "Copied Gemini config to data directory"
fi

# OpenClaw config
if [ -f "$AGENTS_DIR/openclaw/config.yaml" ]; then
    # OpenClaw uses openclaw.json, create from YAML
    cat > "$AI_ROOT/.openclaw/data/openclaw.json" << 'EOF'
{
  "name": "openclaw",
  "framework": "langchain",
  "provider": "openrouter",
  "model": "openrouter/free",
  "memory_backend": "letta_server",
  "letta_server_url": "${LETTA_SERVER_URL:-http://localhost:8283}",
  "auto_save": true,
  "auto_memory": true
}
EOF
    log_info "Created OpenClaw config in data directory"
fi

# KiloCode config
if [ -f "$AGENTS_DIR/kilocode/config.yaml" ]; then
    cp "$AGENTS_DIR/kilocode/config.yaml" "$AI_ROOT/.kilocode/data/config.yaml" 2>/dev/null || true
    log_info "Copied KiloCode config to data directory"
fi

echo ""
echo "=============================================="
echo "  Testing Agent Launches"
echo "=============================================="
echo ""

# Test each agent
test_agent() {
    local cmd="$1"
    local name="$2"
    
    echo -n "Testing $name... "
    if $cmd --help &>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

test_agent "cline" "Cline"
test_agent "opencode" "OpenCode"
test_agent "kilocode" "KiloCode"
test_agent "gemini" "Gemini"
test_agent "openclaw" "OpenClaw"

echo ""
echo "=============================================="
echo "  Summary"
echo "=============================================="
echo ""
echo "Data directories:"
ls -la "$AI_ROOT"/.*/data 2>/dev/null | grep "^d" || true

echo ""
echo "Symlinks:"
ls -la ~/.cline ~/.gemini ~/.openclaw ~/.kilocode 2>/dev/null || true

echo ""
log_info "Agent installations fixed!"
echo ""
echo "Next: Set your API keys in ~/dotfiles/ai/.env"
echo "Then: source ~/.zshrc (or restart shell)"

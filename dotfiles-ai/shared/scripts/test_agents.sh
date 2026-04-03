#!/bin/bash
# Test All AI Agents
# Location: ~/dotfiles/ai/scripts/test_agents.sh

set -e

echo "=============================================="
echo "  AI Agents Installation Test"
echo "=============================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0

test_agent() {
    local cmd="$1"
    local name="$2"
    local expected="$3"
    
    echo -n "Testing $name... "
    
    if command -v "$cmd" &>/dev/null; then
        version=$($cmd --version 2>&1 | head -1)
        echo -e "${GREEN}✓${NC} $version"
        ((pass++))
    else
        echo -e "${RED}✗${NC} Not installed"
        ((fail++))
    fi
}

test_config() {
    local path="$1"
    local name="$2"
    
    echo -n "Checking $name config... "
    
    if [ -f "$path" ]; then
        echo -e "${GREEN}✓${NC} Exists"
        ((pass++))
    elif [ -d "$path" ]; then
        echo -e "${GREEN}✓${NC} Directory exists"
        ((pass++))
    else
        echo -e "${RED}✗${NC} Missing"
        ((fail++))
    fi
}

test_symlink() {
    local path="$1"
    local name="$2"
    
    echo -n "Checking $name symlink... "
    
    if [ -L "$path" ]; then
        target=$(readlink "$path")
        echo -e "${GREEN}✓${NC} -> $target"
        ((pass++))
    else
        echo -e "${RED}✗${NC} Not a symlink"
        ((fail++))
    fi
}

echo "Step 1: Testing Agent Commands"
echo "-------------------------------------------"
test_agent "cline" "Cline"
test_agent "opencode" "OpenCode"
test_agent "kilocode" "KiloCode"
test_agent "gemini" "Gemini"
test_agent "openclaw" "OpenClaw"

echo ""
echo "Step 2: Testing Symlinks"
echo "-------------------------------------------"
test_symlink "$HOME/.cline" "Cline"
test_symlink "$HOME/.gemini" "Gemini"
test_symlink "$HOME/.openclaw" "OpenClaw"
test_symlink "$HOME/.kilocode" "KiloCode"

echo ""
echo "Step 3: Testing Config Files"
echo "-------------------------------------------"
AI_ROOT="$HOME/dotfiles/ai"

test_config "$AI_ROOT/agents/cline/config.yaml" "Cline config"
test_config "$AI_ROOT/agents/opencode/config.yaml" "OpenCode config"
test_config "$AI_ROOT/agents/kilocode/config.yaml" "KiloCode config"
test_config "$AI_ROOT/agents/gemini/config.yaml" "Gemini config"
test_config "$AI_ROOT/agents/openclaw/config.yaml" "OpenClaw config"

test_config "$AI_ROOT/base/base_agent.yaml" "Base agent config"
test_config "$AI_ROOT/base/providers.yaml" "Providers config"
test_config "$AI_ROOT/base/memory.yaml" "Memory config"

echo ""
echo "Step 4: Testing Letta Integration"
echo "-------------------------------------------"
test_config "$AI_ROOT/packages/letta_integration" "Letta package"

if command -v letta-memory-cli &>/dev/null; then
    echo -e "${GREEN}✓${NC} letta-memory-cli installed"
    ((pass++))
else
    echo -e "${RED}✗${NC} letta-memory-cli not found"
    ((fail++))
fi

echo ""
echo "Step 5: Testing Environment"
echo "-------------------------------------------"

check_env() {
    local var="$1"
    local name="$2"
    
    echo -n "Checking $name... "
    
    if [ -n "${!var}" ]; then
        echo -e "${GREEN}✓${NC} Set"
        ((pass++))
    else
        echo -e "${YELLOW}!${NC} Not set (optional for testing)"
    fi
}

check_env "LETTA_SERVER_URL" "LETTA_SERVER_URL"
check_env "LETTA_API_KEY" "LETTA_API_KEY"
check_env "OPENROUTER_API_KEY" "OPENROUTER_API_KEY"

echo ""
echo "=============================================="
echo "  Test Summary"
echo "=============================================="
echo -e "${GREEN}Passed: $pass${NC}"
echo -e "${RED}Failed: $fail${NC}"
echo ""

if [ $fail -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}! Some tests failed. Run 'bash ~/dotfiles/ai/scripts/fix_agent_installs.sh' to fix.${NC}"
    exit 1
fi

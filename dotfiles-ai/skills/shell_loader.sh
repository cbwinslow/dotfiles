#!/bin/bash
# Shell integration for automatic AI agent memory loading
# Source this in ~/.bashrc or ~/.zshrc

# Auto-detect if we're in an AI agent terminal
_detect_ai_agent() {
    # Check various environment variables set by AI agents
    if [[ -n "$WINDSURF_AGENT" ]] || [[ -n "$KILOCODE_AGENT" ]] || [[ -n "$CLINE_AGENT" ]]; then
        return 0
    fi
    
    # Check terminal program
    if [[ "$TERM_PROGRAM" == *"code"* ]] || [[ "$TERM_PROGRAM" == *"vscode"* ]]; then
        return 0
    fi
    
    # Check for AI-specific env vars
    if [[ -n "$AI_AGENT_NAME" ]] || [[ -n "$AGENT_ID" ]]; then
        return 0
    fi
    
    return 1
}

# Auto-load Letta memory integration
_load_letta_memory() {
    local AI_PACKAGES="${HOME}/dotfiles/ai/packages"
    
    # Add to PYTHONPATH
    if [[ -d "$AI_PACKAGES" ]]; then
        if [[ ":$PYTHONPATH:" != *":$AI_PACKAGES:"* ]]; then
            export PYTHONPATH="${AI_PACKAGES}:${PYTHONPATH}"
        fi
    fi
    
    # Add skills directory
    local AI_SKILLS="${HOME}/dotfiles/ai/skills"
    if [[ -d "$AI_SKILLS" ]]; then
        if [[ ":$PYTHONPATH:" != *":$AI_SKILLS:"* ]]; then
            export PYTHONPATH="${AI_SKILLS}:${PYTHONPATH}"
        fi
    fi
    
    # Source environment if exists
    if [[ -f "${HOME}/.env.ai" ]]; then
        source "${HOME}/.env.ai"
    fi
    
    # Auto-initialize if Letta is available
    if command -v python3 &> /dev/null; then
        local LETTA_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8283/v1/health 2>/dev/null || echo "000")
        if [[ "$LETTA_HEALTH" == "200" ]] || [[ "$LETTA_HEALTH" == "000" ]]; then
            export LETTA_AVAILABLE=true
            
            # Auto-initialize memory on shell startup (silent)
            python3 -c "
import sys
sys.path.insert(0, '${AI_PACKAGES}')
try:
    from letta_integration.autonomous_memory import auto_init_memory
    mem = auto_init_memory()
    if mem and mem._initialized:
        print('\033[0;32m✓ Letta memory active\033[0m', file=sys.stderr)
except Exception:
    pass
" 2>&1 | grep -v "^$" || true
        else
            export LETTA_AVAILABLE=false
            echo "⚠ Letta server not responding (port 8283)" >&2
        fi
    fi
}

# Setup aliases for memory operations
setup_letta_aliases() {
    alias letta-status='curl -s http://localhost:8283/v1/health 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "Letta server not available"'
    alias letta-agents='python3 -c "from letta_client import Letta; c=Letta(base_url=\"http://localhost:8283\"); [print(a.name, a.id) for a in c.agents.list()]" 2>/dev/null || echo "Could not list agents"'
    alias letta-search='python3 -c "
import sys, os
sys.path.insert(0, os.path.expanduser(\"~/dotfiles/ai/packages\"))
from letta_integration.autonomous_memory import get_memory
m = get_memory()
if m: 
    results = m.search_memories(\" \".join(sys.argv[1:]), limit=5)
    for r in results: print(r)
"'
}

# Main initialization
if _detect_ai_agent; then
    _load_letta_memory
    setup_letta_aliases
fi

# Export detection function for scripts
export -f _detect_ai_agent 2>/dev/null || true
export -f _load_letta_memory 2>/dev/null || true

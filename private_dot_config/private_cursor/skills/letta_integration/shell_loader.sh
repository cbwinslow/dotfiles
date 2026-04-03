#!/bin/bash
# Letta Skill Auto-Loader
# Source this file in .bashrc to make Letta skills available to all terminal AI agents

# Add letta_integration to Python path
export PYTHONPATH="${PYTHONPATH}:${HOME}/dotfiles/ai/packages/letta_integration"

# Letta environment variables
export LETTA_SERVER_URL="${LETTA_SERVER_URL:-http://localhost:8283}"
export LETTA_DEFAULT_MODEL="${LETTA_DEFAULT_MODEL:-letta/letta-free}"
export LETTA_DEFAULT_EMBEDDING="${LETTA_DEFAULT_EMBEDDING:-ollama/bge-m3:latest}"

# Skill directories for easy access
export LETTA_SKILL_DIR="${HOME}/dotfiles/ai/skills/letta_integration"
export LETTA_SCRIPTS_DIR="${HOME}/dotfiles/ai/shared/scripts"

# Function to load Letta integration in Python scripts
letta_python() {
    python3 -c "
import sys
sys.path.insert(0, '${HOME}/dotfiles/ai/packages/letta_integration')
from letta_integration import LettaIntegration
letta = LettaIntegration(agent_name='${1:-terminal}')
print(f'Letta loaded: {letta.server_url}')
" 2>&1
}

# Quick alias for testing Letta connection
alias letta-health='python3 -c "
import sys
sys.path.insert(0, \"${HOME}/dotfiles/ai/packages/letta_integration\")
from letta_integration import LettaIntegration
letta = LettaIntegration(agent_name=\"test\")
health = letta.check_server_health()
print(f\"Status: {health[chr(39)+chr(39)+chr(39)+chr(39)]}\" + chr(39)+chr(39) + f\"{health[chr(39)+chr(39)]}\" + chr(39)+chr(39) + f\"{health.get(\"error\", \"\")}\")
"'

# Alias to list all agents
alias letta-agents='python3 -c "
import sys
sys.path.insert(0, \"${HOME}/dotfiles/ai/packages/letta_integration\")
from letta_integration import LettaIntegration
letta = LettaIntegration(agent_name=\"list\")
agents = letta.list_agents()
print(f\"Found {len(agents)} agents:\")
for a in agents[:10]:
    print(f\"  - {a.name} ({a.id[:8]}...)\")
"'

# Quick conversation logger using integrated module
letta-log() {
    local user_input="$1"
    local agent_response="$2"
    local agent_name="${3:-windsurf}"
    
    python3 << PYEOF
import sys
sys.path.insert(0, "${HOME}/dotfiles/ai/packages/letta_integration")
from letta_integration import quick_log

session = quick_log("""$user_input""", """$agent_response""", agent_name="$agent_name")
print(f"Logged to session: {session}")
PYEOF
}

# Export functions
export -f letta_python
export -f letta-log

echo "Letta skills loaded. Available:"
echo "  - letta-health  : Check server status"
echo "  - letta-agents  : List all agents"
echo "  - letta-log     : Log conversation"
echo "  - letta_python  : Load Letta in Python"

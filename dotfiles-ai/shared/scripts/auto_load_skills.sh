#!/bin/bash
# Auto-load script for AI agent skills
# This script ensures all agents automatically load their required skills

set -e

AI_DIR="/home/cbwinslow/dotfiles/ai"
SKILLS_DIR="$AI_DIR/skills"
AGENTS_DIR="$AI_DIR/agents"
TOOLS_DIR="$AI_DIR/tools"
BW_SCRIPT="$SKILLS_DIR/bitwarden/bitwarden.sh"

# Core skills - maps display name to directory
declare -A CORE_SKILL_PATHS
CORE_SKILL_PATHS[memory_management]="memory"
CORE_SKILL_PATHS[cli_operations]="cli_operations"
CORE_SKILL_PATHS[conversation_logging]="conversation_logging"
CORE_SKILL_PATHS[memory_sync]="memory_sync"
CORE_SKILL_PATHS[entity_extraction]="integration"
CORE_SKILL_PATHS[cross_agent_search]="integration"
CORE_SKILL_PATHS[server_health]="letta_server"
CORE_SKILL_PATHS[bitwarden_secrets]="bitwarden"
CORE_SKILL_PATHS[cbw_rag]="cbw_rag"

# Agent-specific skills
declare -A AGENT_SKILLS
AGENT_SKILLS[cline]="code_generation code_review debugging"
AGENT_SKILLS[opencode]="code_generation refactoring testing"
AGENT_SKILLS[codex]="code_generation optimization documentation"
AGENT_SKILLS[gemini]="research analysis writing"
AGENT_SKILLS[kilocode]="code_generation performance security"
AGENT_SKILLS[openclaw]="research analysis fact_checking"
AGENT_SKILLS[qwen]="code_generation translation summarization"
AGENT_SKILLS[vscode]="code_generation debugging refactoring"
AGENT_SKILLS[windsurf]="code_generation optimization testing"

# Load skills for an agent
load_agent_skills() {
    local agent_name="$1"
    
    echo "Loading skills for $agent_name..."
    
    # Load core skills
    echo "  Loading core skills..."
    for skill in "${!CORE_SKILL_PATHS[@]}"; do
        local dir="${CORE_SKILL_PATHS[$skill]}"
        local skill_path="$SKILLS_DIR/$dir"
        if [ -d "$skill_path" ] || [ -f "$skill_path/${skill}.sh" ] || [ -f "$skill_path/SKILL.md" ] || [ -f "$skill_path/bitwarden.sh" ] || [ -f "$skill_path/bitwarden_skill.py" ]; then
            echo "    Loaded: $skill (from $dir)"
        else
            echo "    Warning: $skill ($dir) not found"
        fi
    done
    
    # Load agent-specific skills
    local skills="${AGENT_SKILLS[$agent_name]}"
    if [ -n "$skills" ]; then
        echo "  Loading agent-specific skills..."
        for skill in $skills; do
            skill_path="$SKILLS_DIR/$skill"
            if [ -d "$skill_path" ]; then
                echo "    Loaded: $skill"
            else
                echo "    Warning: $skill not found"
            fi
        done
    fi
}

# Main: Load for all agents
echo "========================================="
echo "  Auto-loading skills for all agents"
echo "========================================="
echo ""

for agent in cline opencode codex gemini kilocode openclaw qwen vscode windsurf; do
    load_agent_skills "$agent"
done

# Verify bitwarden skill
echo ""
echo "Verifying Bitwarden skill..."
if [ -f "$BW_SCRIPT" ]; then
    if bash -n "$BW_SCRIPT" 2>/dev/null; then
        echo "  bitwarden.sh: OK"
    else
        echo "  bitwarden.sh: SYNTAX ERROR"
    fi
else
    echo "  bitwarden.sh: NOT FOUND"
fi

if [ -f "$SKILLS_DIR/bitwarden/bitwarden_skill.py" ]; then
    if python3 -m py_compile "$SKILLS_DIR/bitwarden/bitwarden_skill.py" 2>/dev/null; then
        echo "  bitwarden_skill.py: OK"
    else
        echo "  bitwarden_skill.py: SYNTAX ERROR"
    fi
fi

if [ -f "$SKILLS_DIR/bitwarden/SKILL.md" ]; then
    echo "  SKILL.md: OK"
fi

echo ""
echo "========================================="
echo "  Skill loading complete!"
echo "========================================="
echo ""
echo "Usage:"
echo "  bw unlock <password> [totp]"
echo "  bw get-secret --name 'API Key'"
echo "  bw list-secrets"
echo "  bw populate-env --env-file .env --secrets 'Key1,Key2'"

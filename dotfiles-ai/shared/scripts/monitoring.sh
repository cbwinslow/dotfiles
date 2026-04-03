#!/bin/bash
# Monitoring script for AI agent system
# This script checks the health and status of the entire system

set -e

AI_DIR="/home/cbwinslow/dotfiles/ai"
LOG_FILE="$AI_DIR/monitoring.log"

# Function to check Letta server health
check_letta_health() {
    echo "Checking Letta server health..."
    
    # Check if Letta server is running
    if pgrep -f "letta" > /dev/null; then
        echo "  Letta server is running"
    else
        echo "  Letta server is NOT running"
        return 1
    fi
    
    # Check Letta API endpoint
    if curl -s http://localhost:8283/health > /dev/null; then
        echo "  Letta API is responsive"
    else
        echo "  Letta API is NOT responsive"
        return 1
    fi
    
    # Check memory usage
    memory_usage=$(curl -s http://localhost:8283/stats | jq -r '.memory_usage')
    echo "  Memory usage: $memory_usage MB"
    
    return 0
}

# Function to check agent configurations
check_agent_configs() {
    echo "Checking agent configurations..."
    
    AGENTS_DIR="$AI_DIR/agents"
    for agent in cline opencode codex gemini kilocode openclaw qwen vscode windsurf; do
        config_file="$AGENTS_DIR/$agent/config.yaml"
        
        if [ -f "$config_file" ]; then
            echo "  $agent: Config exists"
            
            # Check for required fields
            if grep -q "extends: ../../base/base_agent.yaml" "$config_file"; then
                echo "    - Inherits from base config"
            else
                echo "    - Warning: Does not inherit from base config"
            fi
            
            if grep -q "skills:" "$config_file"; then
                echo "    - Has skills defined"
            else
                echo "    - Warning: No skills defined"
            fi
        else
            echo "  $agent: Config NOT found"
        fi
    done
}

# Function to check skill availability
check_skills() {
    echo "Checking skill availability..."
    
    SKILLS_DIR="$AI_DIR/skills"
    required_skills=("memory_management" "entity_extraction" "conversation_logging" "cross_agent_search" "server_health" "bitwarden_integration")
    
    for skill in "${required_skills[@]}"; do
        if [ -d "$SKILLS_DIR/$skill" ]; then
            echo "  $skill: Available"
        else
            echo "  $skill: MISSING"
        fi
    done
}

# Function to check tool availability
check_tools() {
    echo "Checking tool availability..."
    
    TOOLS_DIR="$AI_DIR/tools"
    required_tools=("file_system" "terminal" "search")
    
    for tool in "${required_tools[@]}"; do
        if [ -d "$TOOLS_DIR/$tool" ]; then
            echo "  $tool: Available"
        else
            echo "  $tool: MISSING"
        fi
    done
}

# Function to check framework integrations
check_frameworks() {
    echo "Checking framework integrations..."
    
    FRAMEWORKS_DIR="$AI_DIR/frameworks"
    frameworks=("langchain" "crewai" "autogen")
    
    for framework in "${frameworks[@]}"; do
        if [ -d "$FRAMEWORKS_DIR/$framework" ]; then
            echo "  $framework: Available"
        else
            echo "  $framework: MISSING"
        fi
    done
}

# Function to check scripts and automation
check_automation() {
    echo "Checking automation scripts..."
    
    SCRIPTS_DIR="$AI_DIR/scripts"
    required_scripts=("auto_load_skills.sh" "agent_prompts.sh" "monitoring.sh")
    
    for script in "${required_scripts[@]}"; do
        if [ -f "$SCRIPTS_DIR/$script" ]; then
            echo "  $script: Available"
            if [ -x "$SCRIPTS_DIR/$script" ]; then
                echo "    - Executable"
            else
                echo "    - Not executable, fixing..."
                chmod +x "$SCRIPTS_DIR/$script"
            fi
        else
            echo "  $script: MISSING"
        fi
    done
}

# Main monitoring function
main() {
    echo "Starting AI Agent System Monitoring..."
    echo "Timestamp: $(date)"
    echo "----------------------------------------"
    
    # Run all checks
    check_letta_health
    echo ""
    check_agent_configs
    echo ""
    check_skills
    echo ""
    check_tools
    echo ""
    check_frameworks
    echo ""
    check_automation
    
    echo "----------------------------------------"
    echo "Monitoring completed!"
}

# Run monitoring
main
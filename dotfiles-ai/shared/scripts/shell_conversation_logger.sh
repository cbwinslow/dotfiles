#!/bin/bash
# Shell Conversation Logger Integration
# Automatically logs AI agent conversations from terminal
# 
# Usage: Source this in your shell profile:
#   source ~/dotfiles/ai/shared/scripts/shell_conversation_logger.sh
#
# Then use the logging functions in AI tool wrappers

# Configuration
CONVERSATION_LOG_DIR="${HOME}/dotfiles/ai/logs/conversations"
CONVERSATION_LOGGER_SCRIPT="${HOME}/dotfiles/ai/shared/scripts/universal_conversation_logger.py"

# Ensure log directory exists
mkdir -p "$CONVERSATION_LOG_DIR"

# Function to log AI interaction
log_ai_interaction() {
    local tool="$1"
    local user_input="$2"
    local agent_response="$3"
    local agent_name="${4:-$tool}"
    
    python3 "$CONVERSATION_LOGGER_SCRIPT" << EOF
import sys
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')
from universal_conversation_logger import log_shell_interaction
log_shell_interaction(
    user_input="""$user_input""",
    agent_response="""$agent_response""",
    tool="$tool",
    agent_name="$agent_name"
)
EOF
}

# Wrapper for OpenClaw (terminal AI)
openclaw_with_logging() {
    local user_input="$*"
    
    # Call actual openclaw and capture response
    local response=$(openclaw "$user_input" 2>&1)
    
    # Log the interaction
    log_ai_interaction "openclaw" "$user_input" "$response" "openclaw"
    
    # Output the response
    echo "$response"
}

# Wrapper for Windsurf CLI
windsurf_cli_with_logging() {
    local user_input="$*"
    
    # Call windsurf and capture response
    local response=$(windsurf "$user_input" 2>&1)
    
    # Log the interaction
    log_ai_interaction "windsurf" "$user_input" "$response" "windsurf"
    
    echo "$response"
}

# Generic AI tool wrapper
ai_with_logging() {
    local tool="$1"
    shift
    local user_input="$*"
    
    # Determine actual command
    local cmd="$tool"
    
    # Call the AI tool and capture response
    local response=$($cmd "$user_input" 2>&1)
    
    # Log the interaction
    log_ai_interaction "$tool" "$user_input" "$response" "$tool"
    
    echo "$response"
}

# Function to search conversations from shell
search_conversations() {
    local query="$1"
    
    python3 << EOF
import sys
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')
from universal_conversation_logger import search_conversations
results = search_conversations("$query")
for r in results[:10]:
    print(f"[{r['agent']}] {r['content'][:80]}...")
EOF
}

# Function to resume a conversation
resume_conversation() {
    local session_id="$1"
    local agent_name="${2:-windsurf}"
    
    python3 << EOF
import sys
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')
from universal_conversation_logger import resume_any_conversation
if resume_any_conversation("$session_id", "$agent_name"):
    print(f"Resumed session: $session_id")
else:
    print(f"Failed to resume session: $session_id")
EOF
}

# Auto-logging for command-line AI interactions
# Use this to wrap any AI command
with_conversation_logging() {
    local agent_name="$1"
    shift
    local cmd="$*"
    
    # Execute command and capture both input and output
    echo "[LOGGING] Agent: $agent_name"
    echo "[LOGGING] Command: $cmd"
    
    # Run the command
    local output=$(eval "$cmd" 2>&1)
    local exit_code=$?
    
    # Log to file for now (Letta logging happens via Python)
    echo "$(date -Iseconds) | $agent_name | $cmd | ${output:0:200}" >> "$CONVERSATION_LOG_DIR/shell_ai_interactions.log"
    
    # Output the result
    echo "$output"
    return $exit_code
}

# Export functions
export -f log_ai_interaction
export -f openclaw_with_logging
export -f windsurf_cli_with_logging
export -f ai_with_logging
export -f search_conversations
export -f resume_conversation
export -f with_conversation_logging

# Aliases for easy access
alias ai-log='log_ai_interaction'
alias ai-search='search_conversations'
alias ai-resume='resume_conversation'
alias ai-openclaw='openclaw_with_logging'
alias ai-windsurf='windsurf_cli_with_logging'

echo "[Conversation Logger] Shell integration loaded"
echo "[Conversation Logger] Available commands:"
echo "  ai-log <tool> <input> <response> - Log an interaction"
echo "  ai-search <query> - Search conversations"
echo "  ai-resume <session_id> - Resume a conversation"
echo "  ai-openclaw <input> - Run openclaw with logging"
echo "  ai-windsurf <input> - Run windsurf with logging"

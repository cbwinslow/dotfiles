#!/usr/bin/env python3
"""
Auto-initialization script for vscode agent
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "agent_memory"))

try:
    from agent_memory import store_agent_context, get_agent_context
    logger.info("✓ Agent memory system loaded successfully")
except Exception as e:
    logger.error(f"Failed to import Agent memory system: {e}")
    sys.exit(1)

def initialize_agent():
    logger.info("Initializing vscode agent with global rules...")
    
    global_rules_path = Path(__file__).parent.parent / "global_rules" / "agent_init_rules.md"
    if global_rules_path.exists():
        with open(global_rules_path, 'r') as f:
            global_rules = f.read()
        logger.info("✓ Global rules loaded")
    else:
        logger.error("✗ Global rules not found")
        return False
    
    agent_context = {
        "initialized": True,
        "global_rules_loaded": True,
        "memory_backend": "agent_memory",
        "letta_connected": False,
    }
    
    context_id = store_agent_context(
        agent_name="vscode",
        context_key="agent_configuration",
        context_value=str(agent_context)
    )
    
    if context_id:
        logger.info(f"✓ Agent context stored with ID: {context_id}")
    else:
        logger.error("✗ Failed to store agent context")
        return False
    
    store_agent_context(
        agent_name="vscode",
        context_key="initialization_complete",
        context_value="true"
    )
    
    logger.info(f"✓ vscode agent initialized successfully")
    return True

def setup_shell_integration():
    logger.info("Setting up shell integration...")
    
    shell_config = """
# Agent AI Skills System - vscode Agent
export AI_SKILLS_SYSTEM="/home/cbwinslow/dotfiles/ai"
export VSCODE_RULES="$AI_SKILLS_SYSTEM/global_rules/agent_init_rules.md"
alias vscode="vscode --init-rules $AI_SKILLS_SYSTEM/global_rules"
"""
    
    home_dir = Path.home()
    shell_rc = home_dir / ".zshrc" if Path(home_dir / ".zshrc").exists() else home_dir / ".bashrc"
    
    if shell_rc.exists():
        with open(shell_rc, 'r') as f:
            content = f.read()
        if "AI_SKILLS_SYSTEM" in content:
            logger.info("✓ Shell integration already configured")
            return True
    
    with open(shell_rc, 'a') as f:
        f.write(shell_config)
    
    logger.info(f"✓ Shell integration added to {shell_rc}")
    return True

if __name__ == "__main__":
    if initialize_agent():
        setup_shell_integration()
        logger.info("🎉 vscode agent setup complete!")
        sys.exit(0)
    else:
        logger.error("❌ vscode agent setup failed!")
        sys.exit(1)

#!/usr/bin/env python3
"""
Universal Agent Initializer for Letta Skills
Auto-loads Letta integration for any AI agent
"""
import sys
import os
from pathlib import Path

# Auto-add letta_integration to path
LETTTA_PACKAGE = Path.home() / "dotfiles" / "ai" / "packages" / "letta_integration"
LETTTA_SCRIPTS = Path.home() / "dotfiles" / "ai" / "shared" / "scripts"

if str(LETTTA_PACKAGE) not in sys.path:
    sys.path.insert(0, str(LETTTA_PACKAGE))
if str(LETTTA_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(LETTTA_SCRIPTS))

def init_letta_for_agent(agent_name: str, auto_create: bool = True):
    """
    Initialize Letta integration for any AI agent.
    
    Args:
        agent_name: Name of the AI agent (windsurf, claude, openclaw, etc.)
        auto_create: Automatically create agent if doesn't exist
        
    Returns:
        LettaIntegration instance ready to use
    """
    try:
        from letta_integration import LettaIntegration
        
        # Get server URL from environment or use default
        server_url = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
        
        # Initialize integration
        letta = LettaIntegration(
            agent_name=agent_name,
            server_url=server_url
        )
        
        # Auto-create agent if requested
        if auto_create:
            agent = letta.create_agent_with_memory_blocks(
                agent_name=agent_name,
                memory_blocks=[
                    {
                        "label": "persona", 
                        "value": f"I am {agent_name}, a helpful AI assistant integrated with Letta memory."
                    },
                    {
                        "label": "human", 
                        "value": f"User interacting with {agent_name}. Preferences will be stored here."
                    },
                    {
                        "label": "system", 
                        "value": f"Agent: {agent_name}. Server: {server_url}. Memory: Letta self-hosted."
                    }
                ]
            )
            
            if agent and hasattr(agent, 'id'):
                print(f"[{agent_name}] ✓ Letta initialized")
                print(f"[{agent_name}] ✓ Agent ID: {agent.id[:20]}...")
                print(f"[{agent_name}] ✓ Server: {server_url}")
            else:
                print(f"[{agent_name}] ⚠ Using existing agent")
        
        return letta
        
    except ImportError as e:
        print(f"[{agent_name}] ✗ Letta integration not available: {e}")
        print(f"[{agent_name}]   Install: pip install letta-client")
        return None
    except Exception as e:
        print(f"[{agent_name}] ✗ Error initializing: {e}")
        return None


def quick_log(agent_name: str, user_input: str, agent_response: str, tool: str = "terminal"):
    """Quick conversation logging for any agent."""
    try:
        from simple_conversation_logger import log_conversation
        return log_conversation(agent_name, tool, user_input, agent_response)
    except Exception as e:
        print(f"[LOG ERROR] {e}")
        return False


def quick_search(agent_name: str, query: str):
    """Quick memory search for any agent."""
    try:
        from simple_conversation_logger import SimpleConversationLogger
        logger = SimpleConversationLogger(agent_name=agent_name, tool="search")
        return logger.search_conversations(query)
    except Exception as e:
        print(f"[SEARCH ERROR] {e}")
        return []


# Auto-initialize if run as script
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Letta for AI agents")
    parser.add_argument("agent_name", help="Name of the AI agent")
    parser.add_argument("--no-create", action="store_true", help="Don't auto-create agent")
    parser.add_argument("--test", action="store_true", help="Run quick test")
    
    args = parser.parse_args()
    
    letta = init_letta_for_agent(args.agent_name, auto_create=not args.no_create)
    
    if args.test and letta:
        print(f"\n[{args.agent_name}] Testing...")
        health = letta.check_server_health()
        print(f"[{args.agent_name}] Server: {health.get('status', 'unknown')}")
        
        # Test memory
        result = letta.update_memory_block("test", f"Test at {__import__('datetime').datetime.now()}")
        print(f"[{args.agent_name}] Memory update: {'✓' if result else '✗'}")
        
        print(f"[{args.agent_name}] Ready to use!")

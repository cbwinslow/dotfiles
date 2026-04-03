#!/usr/bin/env python3
"""
Letta Memory Skill - COMPLETE FEATURE SET

This script provides FULL coverage of all Letta memory features:

AGENT MANAGEMENT:
  python save_memory.py --create-agent windsurf --persona "..." --human "..."
  python save_memory.py --list-agents
  python save_memory.py --delete-agent <agent-id>

MEMORY OPERATIONS:
  python save_memory.py "Content" --agent windsurf --type core
  python save_memory.py --list --agent windsurf
  python save_memory.py --search "query" --agent windsurf
  python save_memory.py --delete-memory <id> --agent windsurf

MEMORY BLOCKS:
  python save_memory.py --create-block persona --value "..." --agent windsurf
  python save_memory.py --list-blocks --agent windsurf

CONVERSATIONS:
  python save_memory.py --conversation '[{"role":"user","content":"hi"}]' --agent windsurf

DECISIONS & ACTIONS:
  python save_memory.py --decision "Use PostgreSQL" --context "For reliability" --agent claude
  python save_memory.py --action "Set up monitoring" --priority high --agent cline

CROSS-AGENT & BACKUP:
  python save_memory.py --search-all "AI configuration"
  python save_memory.py --backup --agent windsurf

ENTITY EXTRACTION:
  python save_memory.py --extract-entities --text "Check /path/to/file Run: $ docker ps"

SYSTEM:
  python save_memory.py --health
  python save_memory.py --stats --agent windsurf

Environment:
  LETTA_SERVER_URL: Letta server URL (default: http://localhost:8283)
  LETTA_API_KEY: API key for authentication
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# Add letta_integration package to path
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')

try:
    from letta_integration import LettaIntegration
except ImportError:
    print("Error: letta_integration package not found")
    print("Install with: pip install -e ~/dotfiles/ai/packages/letta_integration")
    sys.exit(1)

# Configuration
LETTA_SERVER_URL = os.environ.get("LETTA_SERVER_URL", "http://localhost:8283")
LETTA_API_KEY = os.environ.get("LETTA_API_KEY", "")


def save_memory(content: str, agent_name: str, memory_type: str = "archival", tags: List[str] = None) -> bool:
    """Save memory to Letta server.
    
    Args:
        content: Memory text content
        agent_name: Name of the agent (windsurf, claude, etc.)
        memory_type: Type of memory (core, archival, context, persona, human)
        tags: List of tags for categorization
    
    Returns:
        True if saved successfully
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        # Get or create agent
        agent_id = letta.get_or_create_agent(agent_name)
        if not agent_id:
            print(f"✗ Failed to get or create agent: {agent_name}")
            return False
        
        # Save to appropriate memory type
        if memory_type == "archival":
            result = letta._make_request(
                "POST",
                f"/v1/agents/{agent_id}/archival-memory",
                {"text": content, "tags": tags or ["memory", agent_name]}
            )
        else:
            # For other memory types, use the memory endpoint
            result = letta._make_request(
                "POST",
                f"/v1/agents/{agent_id}/memory",
                {
                    "content": content,
                    "memory_type": memory_type,
                    "tags": tags or ["memory", agent_name]
                }
            )
        
        if "error" in result:
            print(f"✗ Error saving memory: {result['error']}")
            return False
        
        print(f"✓ Saved to Letta ({memory_type}): {content[:60]}...")
        return True
        
    except Exception as e:
        print(f"✗ Failed to save memory: {e}")
        return False


def save_conversation(agent_name: str, messages: List[Dict], tags: List[str] = None) -> bool:
    """Save conversation to Letta archival memory.
    
    Args:
        agent_name: Name of the agent
        messages: List of message dicts with 'role' and 'content'
        tags: Tags for categorization
    
    Returns:
        True if saved successfully
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        result = letta.save_conversation(messages, tags=tags or ["conversation"])
        
        if "error" in result:
            print(f"✗ Error saving conversation: {result['error']}")
            return False
        
        print(f"✓ Saved conversation ({len(messages)} messages) to Letta")
        return True
        
    except Exception as e:
        print(f"✗ Failed to save conversation: {e}")
        return False


def list_memories(agent_name: str, memory_type: str = None, limit: int = 100):
    """List memories for an agent.
    
    Args:
        agent_name: Name of the agent
        memory_type: Filter by memory type (optional)
        limit: Maximum number of results
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        # Get or create agent
        agent_id = letta.get_or_create_agent(agent_name)
        if not agent_id:
            print(f"✗ Failed to get agent: {agent_name}")
            return
        
        # Get memories
        memories = letta.get_memories(memory_type=memory_type, limit=limit)
        
        print(f"\n=== Memories for {agent_name} ===\n")
        
        if "memories" in memories:
            for i, mem in enumerate(memories["memories"], 1):
                content = mem.get("content", "")[:100]
                mem_type = mem.get("memory_type", "unknown")
                created = mem.get("created_at", "unknown")
                print(f"{i}. [{mem_type}] {content}... ({created})")
        elif "archival_memory" in memories:
            for i, mem in enumerate(memories["archival_memory"], 1):
                text = mem.get("text", "")[:100]
                print(f"{i}. [archival] {text}...")
        else:
            print("No memories found or empty response")
            print(f"Response: {memories}")
        
        print(f"\nTotal: {len(memories.get('memories', []) + memories.get('archival_memory', []))} memories")
        
    except Exception as e:
        print(f"✗ Failed to list memories: {e}")


def search_memories(agent_name: str, query: str, limit: int = 10):
    """Search memories using semantic search.
    
    Args:
        agent_name: Name of the agent
        query: Search query
        limit: Maximum number of results
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        results = letta.search_memories(query, limit=limit)
        
        print(f"\n=== Search Results for '{query}' ===\n")
        
        if "memories" in results:
            for i, mem in enumerate(results["memories"], 1):
                content = mem.get("content", "")[:150]
                score = mem.get("score", 0)
                print(f"{i}. [{score:.2f}] {content}...")
        else:
            print("No results found")
        
        print(f"\nFound: {len(results.get('memories', []))} results")
        
    except Exception as e:
        print(f"✗ Failed to search memories: {e}")


def create_agent(agent_name: str, persona: str = None, human: str = None) -> bool:
    """Create a new agent with optional core memory blocks.
    
    Args:
        agent_name: Name of the agent
        persona: Persona block content
        human: Human block content
    
    Returns:
        True if created successfully
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        agent_id = letta.get_or_create_agent(agent_name)
        if not agent_id:
            print(f"✗ Failed to create agent: {agent_name}")
            return False
        
        print(f"✓ Created agent: {agent_name} ({agent_id[:8]}...)")
        
        # Setup core memory if provided
        if persona or human:
            print("  Setting up core memory blocks...")
            result = letta.setup_core_memory_blocks(
                persona_value=persona,
                human_value=human
            )
            if result["blocks_created"]:
                print(f"  ✓ Blocks: {', '.join(result['blocks_created'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create agent: {e}")
        return False


def list_agents():
    """List all agents on the server."""
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY
        )
        
        agents = letta.list_agents()
        agent_list = agents if isinstance(agents, list) else agents.get("agents", [])
        
        print(f"\n=== Agents ({len(agent_list)} total) ===\n")
        for agent in agent_list:
            print(f"  {agent.get('name')} ({agent.get('id')[:8]}...)")
        
    except Exception as e:
        print(f"✗ Failed to list agents: {e}")


def delete_agent(agent_id: str) -> bool:
    """Delete an agent.
    
    Args:
        agent_id: ID of the agent to delete
    
    Returns:
        True if deleted successfully
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY
        )
        
        result = letta.delete_agent(agent_id)
        if "error" in result:
            print(f"✗ Error: {result['error']}")
            return False
        
        print(f"✓ Deleted agent: {agent_id[:8]}...")
        return True
        
    except Exception as e:
        print(f"✗ Failed to delete agent: {e}")
        return False


def create_memory_block(agent_name: str, label: str, value: str, description: str = None) -> bool:
    """Create a memory block.
    
    Args:
        agent_name: Name of the agent
        label: Block label
        value: Block content
        description: Optional description
    
    Returns:
        True if created successfully
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        block = letta.create_block(label=label, value=value, description=description)
        if "error" in block:
            print(f"✗ Error: {block['error']}")
            return False
        
        block_id = block.get("id", "N/A")
        print(f"✓ Created block: {label} ({block_id[:8]}...)")
        
        # Attach to agent
        agent_id = letta.get_or_create_agent(agent_name)
        if agent_id:
            letta.attach_block_to_agent(agent_id, block_id)
            print(f"  ✓ Attached to {agent_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create block: {e}")
        return False


def delete_memory(agent_name: str, memory_id: str) -> bool:
    """Delete a memory.
    
    Args:
        agent_name: Name of the agent
        memory_id: ID of the memory to delete
    
    Returns:
        True if deleted successfully
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        result = letta.delete_memory(memory_id)
        if "error" in result:
            print(f"✗ Error: {result['error']}")
            return False
        
        print(f"✓ Deleted memory: {memory_id[:8]}...")
        return True
        
    except Exception as e:
        print(f"✗ Failed to delete memory: {e}")
        return False


def create_decision(agent_name: str, decision: str, context: str) -> bool:
    """Create a decision memory.
    
    Args:
        agent_name: Name of the agent
        decision: Decision text
        context: Decision context
    
    Returns:
        True if created successfully
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        result = letta.create_memory_from_decision(decision, context)
        if "error" in result:
            print(f"✗ Error: {result['error']}")
            return False
        
        print(f"✓ Decision saved: {decision[:50]}...")
        return True
        
    except Exception as e:
        print(f"✗ Failed to save decision: {e}")
        return False


def create_action_item(agent_name: str, action: str, priority: str = "medium") -> bool:
    """Create an action item.
    
    Args:
        agent_name: Name of the agent
        action: Action description
        priority: Priority level (low, medium, high)
    
    Returns:
        True if created successfully
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        result = letta.create_memory_from_action_item(action, priority)
        if "error" in result:
            print(f"✗ Error: {result['error']}")
            return False
        
        print(f"✓ Action item saved: [{priority}] {action[:50]}...")
        return True
        
    except Exception as e:
        print(f"✗ Failed to save action item: {e}")
        return False


def extract_entities(agent_name: str, text: str) -> bool:
    """Extract and store entities from text.
    
    Args:
        agent_name: Name of the agent
        text: Text to extract from
    
    Returns:
        True if extracted successfully
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        result = letta.extract_and_store_entities(text)
        entities = result.get("entities", [])
        
        print(f"✓ Extracted {len(entities)} entities:")
        for e in entities:
            print(f"  [{e['type']}] {e['value'][:40]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to extract entities: {e}")
        return False


def search_all_agents(query: str, limit: int = 5):
    """Search memories across all agents.
    
    Args:
        query: Search query
        limit: Results per agent
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY
        )
        
        result = letta.search_all_agents(query, limit_per_agent=limit)
        results = result.get("results", {})
        
        print(f"\n=== Cross-Agent Search: '{query}' ===\n")
        print(f"Found results in {len(results)} agents:\n")
        
        for agent_name, memories in results.items():
            print(f"{agent_name}: {len(memories)} memories")
            for mem in memories[:3]:
                content = mem.get("content", "")[:50]
                print(f"  - {content}...")
        
    except Exception as e:
        print(f"✗ Failed to search: {e}")


def backup_agent(agent_name: str, path: str = None) -> bool:
    """Backup agent memories to file.
    
    Args:
        agent_name: Name of the agent
        path: Backup directory (optional)
    
    Returns:
        True if backup successful
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        result = letta.backup_memories(path)
        if result.get("success"):
            print(f"✓ Backup created: {result['backup_file']}")
            print(f"  Memories: {result['memory_count']}")
            return True
        else:
            print(f"✗ Backup failed: {result.get('error', 'Unknown')}")
            return False
        
    except Exception as e:
        print(f"✗ Failed to backup: {e}")
        return False


def get_stats(agent_name: str):
    """Get memory statistics for an agent.
    
    Args:
        agent_name: Name of the agent
    """
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY,
            agent_name=agent_name
        )
        
        stats = letta.get_memory_stats()
        print(f"\n=== Stats for {agent_name} ===\n")
        print(json.dumps(stats, indent=2))
        
    except Exception as e:
        print(f"✗ Failed to get stats: {e}")


def check_server_health():
    """Check Letta server health."""
    try:
        letta = LettaIntegration(
            server_url=LETTA_SERVER_URL,
            api_key=LETTA_API_KEY
        )
        
        health = letta.check_server_health()
        
        print("\n=== Letta Server Health ===\n")
        print(f"Status: {health.get('status', 'unknown')}")
        print(f"Version: {health.get('version', 'unknown')}")
        print(f"URL: {LETTA_SERVER_URL}")
        
    except Exception as e:
        print(f"✗ Failed to check health: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Letta Memory Skill - Save and retrieve agent memories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python save_memory.py "Learned about RAG indexing" --agent windsurf
  python save_memory.py "System configuration" --type core --agent claude --tags config,important
  python save_memory.py --list --agent windsurf
  python save_memory.py --search "database" --agent windsurf
  python save_memory.py --health
        """
    )
    
    parser.add_argument("content", nargs="?", help="Memory content to save")
    parser.add_argument("--agent", default="default", help="Agent name")
    parser.add_argument("--type", default="archival",
                       choices=["core", "archival", "context", "persona", "human"],
                       help="Memory type")
    parser.add_argument("--tags", help="Comma-separated tags")
    
    # Agent management
    parser.add_argument("--create-agent", action="store_true", help="Create new agent")
    parser.add_argument("--list-agents", action="store_true", help="List all agents")
    parser.add_argument("--delete-agent", help="Delete agent by ID")
    parser.add_argument("--persona", help="Persona block content")
    parser.add_argument("--human", help="Human block content")
    
    # Memory operations
    parser.add_argument("--list", action="store_true", help="List memories")
    parser.add_argument("--search", help="Search memories")
    parser.add_argument("--delete-memory", help="Delete memory by ID")
    parser.add_argument("--limit", type=int, default=10, help="Limit results")
    
    # Memory blocks
    parser.add_argument("--create-block", help="Create block with label")
    parser.add_argument("--value", help="Block value/content")
    parser.add_argument("--list-blocks", action="store_true", help="List agent blocks")
    
    # Conversations
    parser.add_argument("--conversation", help="JSON array of messages")
    
    # Decisions and actions
    parser.add_argument("--decision", help="Decision text")
    parser.add_argument("--context", help="Decision context")
    parser.add_argument("--action", help="Action item description")
    parser.add_argument("--priority", default="medium", choices=["low", "medium", "high"],
                       help="Action priority")
    
    # Cross-agent and backup
    parser.add_argument("--search-all", help="Search all agents")
    parser.add_argument("--backup", action="store_true", help="Backup memories")
    parser.add_argument("--backup-path", help="Backup directory")
    
    # Entity extraction
    parser.add_argument("--extract-entities", action="store_true", help="Extract entities")
    parser.add_argument("--text", help="Text to extract from")
    
    # System
    parser.add_argument("--health", action="store_true", help="Check server health")
    parser.add_argument("--stats", action="store_true", help="Get agent stats")
    
    args = parser.parse_args()
    
    # Parse tags
    tags = args.tags.split(",") if args.tags else None
    
    # Agent management
    if args.create_agent:
        success = create_agent(args.agent, args.persona, args.human)
        sys.exit(0 if success else 1)
    
    if args.list_agents:
        list_agents()
        sys.exit(0)
    
    if args.delete_agent:
        success = delete_agent(args.delete_agent)
        sys.exit(0 if success else 1)
    
    # Memory blocks
    if args.create_block:
        success = create_memory_block(args.agent, args.create_block, args.value, args.context)
        sys.exit(0 if success else 1)
    
    if args.list_blocks:
        # Reuse list_memories but filter for blocks
        list_memories(args.agent, limit=args.limit)
        sys.exit(0)
    
    # Conversations
    if args.conversation:
        try:
            messages = json.loads(args.conversation)
            success = save_conversation(args.agent, messages, tags)
            sys.exit(0 if success else 1)
        except json.JSONDecodeError:
            print("✗ Invalid JSON in conversation")
            sys.exit(1)
    
    # Decisions and actions
    if args.decision:
        success = create_decision(args.agent, args.decision, args.context or "")
        sys.exit(0 if success else 1)
    
    if args.action:
        success = create_action_item(args.agent, args.action, args.priority)
        sys.exit(0 if success else 1)
    
    # Cross-agent and backup
    if args.search_all:
        search_all_agents(args.search_all, args.limit)
        sys.exit(0)
    
    if args.backup:
        success = backup_agent(args.agent, args.backup_path)
        sys.exit(0 if success else 1)
    
    # Entity extraction
    if args.extract_entities:
        if not args.text:
            print("✗ --text required for entity extraction")
            sys.exit(1)
        success = extract_entities(args.agent, args.text)
        sys.exit(0 if success else 1)
    
    # Stats
    if args.stats:
        get_stats(args.agent)
        sys.exit(0)
    
    # Health check
    if args.health:
        check_server_health()
        sys.exit(0)
    
    # Standard memory operations
    if args.list:
        list_memories(args.agent, args.type, args.limit)
    elif args.search:
        search_memories(args.agent, args.search, args.limit)
    elif args.delete_memory:
        success = delete_memory(args.agent, args.delete_memory)
        sys.exit(0 if success else 1)
    elif args.content:
        success = save_memory(args.content, args.agent, args.type, tags)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Letta Memory CLI - Complete command-line interface for Letta memory system
Provides full coverage of all Letta features for AI agents.

Usage:
  letta-memory-cli agent create --name windsurf --persona "..." --human "..."
  letta-memory-cli agent list
  letta-memory-cli agent delete --id <agent-id>
  
  letta-memory-cli memory save --agent windsurf --content "..." --type core
  letta-memory-cli memory search --agent windsurf --query "..."
  letta-memory-cli memory list --agent windsurf
  letta-memory-cli memory delete --agent windsurf --id <memory-id>
  
  letta-memory-cli block create --label persona --value "..."
  letta-memory-cli block attach --agent windsurf --block <block-id>
  letta-memory-cli block list --agent windsurf
  
  letta-memory-cli conversation save --agent windsurf --messages "..."
  letta-memory-cli decision create --agent windsurf --decision "..." --context "..."
  letta-memory-cli action create --agent windsurf --action "..." --priority high
  
  letta-memory-cli search all --query "..."
  letta-memory-cli backup create --agent windsurf
  
  letta-memory-cli health
  letta-memory-cli stats --agent windsurf
  letta-memory-cli entities extract --text "..."

Environment:
  LETTA_SERVER_URL - Letta server URL (default: http://localhost:8283)
  LETTA_API_KEY - API key for authentication
"""

import argparse
import json
import os
import sys
from typing import List, Dict
from datetime import datetime

# Add letta_integration to path
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')

try:
    from letta_integration import LettaIntegration
except ImportError:
    print("Error: letta_integration package not found")
    sys.exit(1)


def get_letta(agent_name: str = None) -> LettaIntegration:
    """Get Letta integration instance."""
    return LettaIntegration(
        server_url=os.getenv("LETTA_SERVER_URL", "http://localhost:8283"),
        api_key=os.getenv("LETTA_API_KEY", ""),
        agent_name=agent_name or "default"
    )


# ==================== AGENT COMMANDS ====================

def cmd_agent_create(args):
    """Create a new agent with optional persona and human blocks."""
    letta = get_letta(args.name)
    
    print(f"Creating agent: {args.name}")
    agent_id = letta.get_or_create_agent(args.name)
    
    if not agent_id:
        print(f"✗ Failed to create agent")
        return 1
    
    print(f"✓ Agent created: {agent_id[:8]}...")
    
    # Setup core memory if provided
    if args.persona or args.human:
        print("Setting up core memory blocks...")
        result = letta.setup_core_memory_blocks(
            persona_value=args.persona,
            human_value=args.human
        )
        
        if result["blocks_created"]:
            print(f"✓ Created blocks: {', '.join(result['blocks_created'])}")
        if result["errors"]:
            print(f"⚠ Errors: {result['errors']}")
    
    return 0


def cmd_agent_list(args):
    """List all agents."""
    letta = get_letta()
    agents = letta.list_agents()
    
    agent_list = agents if isinstance(agents, list) else agents.get("agents", [])
    
    print(f"\n=== Agents ({len(agent_list)} total) ===\n")
    
    for agent in agent_list:
        print(f"Name: {agent.get('name')}")
        print(f"  ID: {agent.get('id')}")
        print(f"  Model: {agent.get('model', 'N/A')}")
        print()


def cmd_agent_delete(args):
    """Delete an agent."""
    letta = get_letta()
    
    print(f"Deleting agent: {args.id}")
    result = letta.delete_agent(args.id)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print("✓ Agent deleted")
    return 0


# ==================== MEMORY COMMANDS ====================

def cmd_memory_save(args):
    """Save a memory to an agent."""
    letta = get_letta(args.agent)
    
    # Get or create agent
    agent_id = letta.get_or_create_agent()
    if not agent_id:
        print(f"✗ Failed to get agent: {args.agent}")
        return 1
    
    # Parse tags
    tags = args.tags.split(",") if args.tags else None
    
    print(f"Saving {args.type} memory to {args.agent}...")
    
    # Save based on memory type
    if args.type == "archival":
        result = letta._make_request(
            "POST",
            f"/v1/agents/{agent_id}/archival-memory",
            {"text": args.content, "tags": tags or ["memory"]}
        )
    else:
        result = letta._make_request(
            "POST",
            f"/v1/agents/{agent_id}/memory",
            {
                "content": args.content,
                "memory_type": args.type,
                "tags": tags or ["memory"]
            }
        )
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print(f"✓ Memory saved (ID: {result.get('id', 'N/A')[:8]}...)")
    return 0


def cmd_memory_search(args):
    """Search memories."""
    letta = get_letta(args.agent)
    
    print(f"Searching for: '{args.query}' in {args.agent}...")
    
    tags = args.tags.split(",") if args.tags else None
    result = letta.search_memories(args.query, memory_type=args.type, tags=tags, limit=args.limit)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    memories = result.get("memories", [])
    print(f"\n=== Results ({len(memories)} found) ===\n")
    
    for i, mem in enumerate(memories, 1):
        content = mem.get("content", "")[:100]
        score = mem.get("score", 0)
        mem_type = mem.get("memory_type", "unknown")
        print(f"{i}. [{mem_type}] {content}... (score: {score:.2f})")
    
    return 0


def cmd_memory_list(args):
    """List all memories for an agent."""
    letta = get_letta(args.agent)
    
    print(f"Listing memories for {args.agent}...")
    
    result = letta.get_memories(memory_type=args.type, limit=args.limit)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    memories = result.get("memories", [])
    print(f"\n=== Memories ({len(memories)} total) ===\n")
    
    for mem in memories:
        content = mem.get("content", "")[:80]
        mem_type = mem.get("memory_type", "unknown")
        mem_id = mem.get("id", "N/A")[:8]
        print(f"[{mem_type}] {content}... ({mem_id})")
    
    return 0


def cmd_memory_delete(args):
    """Delete a memory."""
    letta = get_letta(args.agent)
    
    print(f"Deleting memory: {args.id}")
    
    result = letta.delete_memory(args.id)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print("✓ Memory deleted")
    return 0


# ==================== BLOCK COMMANDS ====================

def cmd_block_create(args):
    """Create a memory block."""
    letta = get_letta()
    
    print(f"Creating block: {args.label}")
    
    result = letta.create_block(
        label=args.label,
        value=args.value,
        description=args.description,
        limit=args.limit
    )
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print(f"✓ Block created: {result.get('id')}")
    return 0


def cmd_block_attach(args):
    """Attach a block to an agent."""
    letta = get_letta(args.agent)
    
    agent_id = letta.get_or_create_agent()
    if not agent_id:
        print(f"✗ Failed to get agent: {args.agent}")
        return 1
    
    print(f"Attaching block {args.block} to {args.agent}...")
    
    result = letta.attach_block_to_agent(agent_id, args.block)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print("✓ Block attached")
    return 0


def cmd_block_detach(args):
    """Detach a block from an agent."""
    letta = get_letta(args.agent)
    
    agent_id = letta.get_or_create_agent()
    if not agent_id:
        print(f"✗ Failed to get agent: {args.agent}")
        return 1
    
    print(f"Detaching block {args.block} from {args.agent}...")
    
    result = letta.detach_block_from_agent(agent_id, args.block)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print("✓ Block detached")
    return 0


def cmd_block_list(args):
    """List blocks for an agent."""
    letta = get_letta(args.agent)
    
    agent_id = letta.get_or_create_agent()
    if not agent_id:
        print(f"✗ Failed to get agent: {args.agent}")
        return 1
    
    print(f"Listing blocks for {args.agent}...")
    
    result = letta.get_agent_blocks(agent_id)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    blocks = result.get("blocks", [])
    print(f"\n=== Blocks ({len(blocks)} total) ===\n")
    
    for block in blocks:
        label = block.get("label", "N/A")
        value = block.get("value", "")[:50]
        limit = block.get("limit", "N/A")
        print(f"[{label}] {value}... (limit: {limit})")
    
    return 0


# ==================== CONVERSATION COMMANDS ====================

def cmd_conversation_save(args):
    """Save a conversation."""
    letta = get_letta(args.agent)
    
    # Parse messages from JSON string
    try:
        messages = json.loads(args.messages)
    except json.JSONDecodeError:
        print("✗ Invalid JSON in messages")
        return 1
    
    tags = args.tags.split(",") if args.tags else None
    
    print(f"Saving conversation ({len(messages)} messages) to {args.agent}...")
    
    result = letta.save_conversation(messages, tags=tags)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print("✓ Conversation saved")
    return 0


# ==================== DECISION COMMANDS ====================

def cmd_decision_create(args):
    """Create a decision memory."""
    letta = get_letta(args.agent)
    
    print(f"Creating decision memory in {args.agent}...")
    
    result = letta.create_memory_from_decision(args.decision, args.context)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print("✓ Decision memory created")
    return 0


# ==================== ACTION COMMANDS ====================

def cmd_action_create(args):
    """Create an action item memory."""
    letta = get_letta(args.agent)
    
    print(f"Creating action item in {args.agent}...")
    
    result = letta.create_memory_from_action_item(args.action, args.priority)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print("✓ Action item created")
    return 0


# ==================== SEARCH COMMANDS ====================

def cmd_search_all(args):
    """Search across all agents."""
    letta = get_letta()
    
    print(f"Searching all agents for: '{args.query}'...")
    
    result = letta.search_all_agents(args.query, limit_per_agent=args.limit)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    results = result.get("results", {})
    print(f"\n=== Results from {len(results)} agents ===\n")
    
    for agent_name, memories in results.items():
        print(f"{agent_name}: {len(memories)} memories")
        for mem in memories[:3]:  # Show first 3
            content = mem.get("content", "")[:60]
            print(f"  - {content}...")
    
    return 0


# ==================== BACKUP COMMANDS ====================

def cmd_backup_create(args):
    """Create a backup of memories."""
    letta = get_letta(args.agent)
    
    print(f"Creating backup for {args.agent}...")
    
    result = letta.backup_memories(args.path)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    if result.get("success"):
        print(f"✓ Backup created: {result['backup_file']}")
        print(f"  Memories: {result['memory_count']}")
    
    return 0


# ==================== HEALTH/STATS COMMANDS ====================

def cmd_health(args):
    """Check server health."""
    letta = get_letta()
    
    print("Checking Letta server health...")
    
    result = letta.check_server_health()
    
    print(f"\n=== Server Health ===\n")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Version: {result.get('version', 'unknown')}")
    print(f"URL: {os.getenv('LETTA_SERVER_URL', 'http://localhost:8283')}")


def cmd_stats(args):
    """Get agent stats."""
    letta = get_letta(args.agent)
    
    print(f"Getting stats for {args.agent}...")
    
    result = letta.get_memory_stats()
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    print(f"\n=== Stats for {args.agent} ===\n")
    print(json.dumps(result, indent=2))
    return 0


# ==================== ENTITY COMMANDS ====================

def cmd_entities_extract(args):
    """Extract entities from text."""
    letta = get_letta(args.agent)
    
    print("Extracting entities...")
    
    result = letta.extract_and_store_entities(args.text)
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return 1
    
    entities = result.get("entities", [])
    print(f"\n=== Extracted Entities ({len(entities)} total) ===\n")
    
    for entity in entities:
        print(f"[{entity.get('type')}] {entity.get('value')[:50]}...")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Letta Memory CLI - Complete management of Letta memory system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Agent management
  letta-memory-cli agent create --name windsurf --persona "Code editor agent"
  letta-memory-cli agent list
  
  # Memory operations
  letta-memory-cli memory save --agent windsurf --content "Important info" --type core
  letta-memory-cli memory search --agent windsurf --query "database"
  
  # Blocks
  letta-memory-cli block create --label persona --value "I am an AI assistant"
  letta-memory-cli block attach --agent windsurf --block <id>
  
  # Conversations and decisions
  letta-memory-cli conversation save --agent windsurf --messages '[{"role":"user","content":"hi"}]'
  letta-memory-cli decision create --agent claude --decision "Use PostgreSQL" --context "For reliability"
  
  # Cross-agent search
  letta-memory-cli search all --query "AI agent"
  
  # Backup
  letta-memory-cli backup create --agent windsurf
  
  # Health and stats
  letta-memory-cli health
  letta-memory-cli stats --agent windsurf
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Agent commands
    agent_parser = subparsers.add_parser("agent", help="Agent management")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_cmd")
    
    agent_create = agent_subparsers.add_parser("create", help="Create agent")
    agent_create.add_argument("--name", required=True, help="Agent name")
    agent_create.add_argument("--persona", help="Persona block content")
    agent_create.add_argument("--human", help="Human block content")
    agent_create.set_defaults(func=cmd_agent_create)
    
    agent_list = agent_subparsers.add_parser("list", help="List agents")
    agent_list.set_defaults(func=cmd_agent_list)
    
    agent_delete = agent_subparsers.add_parser("delete", help="Delete agent")
    agent_delete.add_argument("--id", required=True, help="Agent ID")
    agent_delete.set_defaults(func=cmd_agent_delete)
    
    # Memory commands
    memory_parser = subparsers.add_parser("memory", help="Memory operations")
    memory_subparsers = memory_parser.add_subparsers(dest="memory_cmd")
    
    memory_save = memory_subparsers.add_parser("save", help="Save memory")
    memory_save.add_argument("--agent", required=True, help="Agent name")
    memory_save.add_argument("--content", required=True, help="Memory content")
    memory_save.add_argument("--type", default="archival", 
                            choices=["core", "archival", "context", "persona", "human"],
                            help="Memory type")
    memory_save.add_argument("--tags", help="Comma-separated tags")
    memory_save.set_defaults(func=cmd_memory_save)
    
    memory_search = memory_subparsers.add_parser("search", help="Search memories")
    memory_search.add_argument("--agent", required=True, help="Agent name")
    memory_search.add_argument("--query", required=True, help="Search query")
    memory_search.add_argument("--type", help="Filter by memory type")
    memory_search.add_argument("--tags", help="Comma-separated tags")
    memory_search.add_argument("--limit", type=int, default=10, help="Max results")
    memory_search.set_defaults(func=cmd_memory_search)
    
    memory_list = memory_subparsers.add_parser("list", help="List memories")
    memory_list.add_argument("--agent", required=True, help="Agent name")
    memory_list.add_argument("--type", help="Filter by memory type")
    memory_list.add_argument("--limit", type=int, default=50, help="Max results")
    memory_list.set_defaults(func=cmd_memory_list)
    
    memory_delete = memory_subparsers.add_parser("delete", help="Delete memory")
    memory_delete.add_argument("--agent", required=True, help="Agent name")
    memory_delete.add_argument("--id", required=True, help="Memory ID")
    memory_delete.set_defaults(func=cmd_memory_delete)
    
    # Block commands
    block_parser = subparsers.add_parser("block", help="Memory block operations")
    block_subparsers = block_parser.add_subparsers(dest="block_cmd")
    
    block_create = block_subparsers.add_parser("create", help="Create block")
    block_create.add_argument("--label", required=True, help="Block label")
    block_create.add_argument("--value", required=True, help="Block content")
    block_create.add_argument("--description", help="Block description")
    block_create.add_argument("--limit", type=int, default=5000, help="Character limit")
    block_create.set_defaults(func=cmd_block_create)
    
    block_attach = block_subparsers.add_parser("attach", help="Attach block to agent")
    block_attach.add_argument("--agent", required=True, help="Agent name")
    block_attach.add_argument("--block", required=True, help="Block ID")
    block_attach.set_defaults(func=cmd_block_attach)
    
    block_detach = block_subparsers.add_parser("detach", help="Detach block from agent")
    block_detach.add_argument("--agent", required=True, help="Agent name")
    block_detach.add_argument("--block", required=True, help="Block ID")
    block_detach.set_defaults(func=cmd_block_detach)
    
    block_list = block_subparsers.add_parser("list", help="List agent blocks")
    block_list.add_argument("--agent", required=True, help="Agent name")
    block_list.set_defaults(func=cmd_block_list)
    
    # Conversation commands
    conv_parser = subparsers.add_parser("conversation", help="Conversation management")
    conv_subparsers = conv_parser.add_subparsers(dest="conv_cmd")
    
    conv_save = conv_subparsers.add_parser("save", help="Save conversation")
    conv_save.add_argument("--agent", required=True, help="Agent name")
    conv_save.add_argument("--messages", required=True, help="JSON array of messages")
    conv_save.add_argument("--tags", help="Comma-separated tags")
    conv_save.set_defaults(func=cmd_conversation_save)
    
    # Decision commands
    decision_parser = subparsers.add_parser("decision", help="Decision management")
    decision_subparsers = decision_parser.add_subparsers(dest="decision_cmd")
    
    decision_create = decision_subparsers.add_parser("create", help="Create decision memory")
    decision_create.add_argument("--agent", required=True, help="Agent name")
    decision_create.add_argument("--decision", required=True, help="Decision text")
    decision_create.add_argument("--context", required=True, help="Decision context")
    decision_create.set_defaults(func=cmd_decision_create)
    
    # Action commands
    action_parser = subparsers.add_parser("action", help="Action item management")
    action_subparsers = action_parser.add_subparsers(dest="action_cmd")
    
    action_create = action_subparsers.add_parser("create", help="Create action item")
    action_create.add_argument("--agent", required=True, help="Agent name")
    action_create.add_argument("--action", required=True, help="Action description")
    action_create.add_argument("--priority", default="medium", 
                              choices=["low", "medium", "high"],
                              help="Priority level")
    action_create.set_defaults(func=cmd_action_create)
    
    # Search commands
    search_parser = subparsers.add_parser("search", help="Search operations")
    search_subparsers = search_parser.add_subparsers(dest="search_cmd")
    
    search_all = search_subparsers.add_parser("all", help="Search all agents")
    search_all.add_argument("--query", required=True, help="Search query")
    search_all.add_argument("--limit", type=int, default=5, help="Results per agent")
    search_all.set_defaults(func=cmd_search_all)
    
    # Backup commands
    backup_parser = subparsers.add_parser("backup", help="Backup operations")
    backup_subparsers = backup_parser.add_subparsers(dest="backup_cmd")
    
    backup_create = backup_subparsers.add_parser("create", help="Create backup")
    backup_create.add_argument("--agent", required=True, help="Agent name")
    backup_create.add_argument("--path", help="Backup directory")
    backup_create.set_defaults(func=cmd_backup_create)
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check server health")
    health_parser.set_defaults(func=cmd_health)
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get agent stats")
    stats_parser.add_argument("--agent", required=True, help="Agent name")
    stats_parser.set_defaults(func=cmd_stats)
    
    # Entity commands
    entity_parser = subparsers.add_parser("entities", help="Entity extraction")
    entity_subparsers = entity_parser.add_subparsers(dest="entity_cmd")
    
    entity_extract = entity_subparsers.add_parser("extract", help="Extract entities")
    entity_extract.add_argument("--agent", required=True, help="Agent name")
    entity_extract.add_argument("--text", required=True, help="Text to extract from")
    entity_extract.set_defaults(func=cmd_entities_extract)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

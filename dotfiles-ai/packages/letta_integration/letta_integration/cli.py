#!/usr/bin/env python3
"""
Letta Memory CLI
Command-line interface for Letta memory management.

Usage:
    letta-memory-cli save --type "conversation" --content "..."
    letta-memory-cli search --query "entity extraction"
    letta-memory-cli stats
    letta-memory-cli health
    letta-memory-cli backup
"""

import argparse
import sys
import json
from letta_integration import LettaIntegration, get_letta_integration


def cmd_save(args):
    """Save memory via CLI"""
    letta = get_letta_integration()
    
    if args.type == "conversation":
        messages = [{
            "role": "user",
            "content": args.content,
            "timestamp": args.timestamp or None
        }]
        result = letta.save_conversation(messages, tags=args.tags)
    elif args.type == "decision":
        result = letta.create_memory_from_decision(args.content, args.context or "")
    elif args.type == "action_item":
        result = letta.create_memory_from_action_item(args.content, args.priority or "medium")
    else:
        # Generic memory
        if not letta.agent_id:
            letta.get_or_create_agent()
        result = letta._make_request(
            "POST",
            f"/v1/agents/{letta.agent_id}/memory",
            {
                "content": args.content,
                "memory_type": args.memory_type or "archival",
                "tags": args.tags or []
            }
        )
    
    print(json.dumps(result, indent=2))
    return 0


def cmd_search(args):
    """Search memories via CLI"""
    letta = get_letta_integration()
    result = letta.search_memories(
        args.query,
        memory_type=args.type,
        limit=args.limit
    )
    print(json.dumps(result, indent=2))
    return 0


def cmd_stats(args):
    """Get memory statistics via CLI"""
    letta = get_letta_integration()
    
    print("=== Letta Server Stats ===")
    health = letta.check_server_health()
    print(f"Server Status: {health.get('status', 'unknown')}")
    print(f"Server Version: {health.get('version', 'unknown')}")
    
    print("\n=== Agent Stats ===")
    stats = letta.get_memory_stats()
    print(json.dumps(stats, indent=2))
    return 0


def cmd_health(args):
    """Check server health via CLI"""
    letta = get_letta_integration()
    health = letta.check_server_health()
    print(json.dumps(health, indent=2))
    return 0 if health.get("status") == "healthy" else 1


def cmd_backup(args):
    """Backup memories via CLI"""
    letta = get_letta_integration()
    result = letta.backup_memories(args.output)
    print(json.dumps(result, indent=2))
    return 0


def cmd_list(args):
    """List agents or memories via CLI"""
    letta = get_letta_integration()
    
    if args.target == "agents":
        result = letta.list_agents()
    elif args.target == "memories":
        result = letta.get_memories(memory_type=args.type, limit=args.limit)
    else:
        result = {"error": f"Unknown target: {args.target}"}
    
    print(json.dumps(result, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Letta Memory CLI - Manage Letta memories from command line"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Save command
    save_parser = subparsers.add_parser("save", help="Save memory")
    save_parser.add_argument("--type", "-t", required=True,
                            choices=["conversation", "decision", "action_item", "generic"],
                            help="Type of memory to save")
    save_parser.add_argument("--content", "-c", required=True, help="Content to save")
    save_parser.add_argument("--context", help="Additional context (for decisions)")
    save_parser.add_argument("--tags", nargs="+", help="Tags for categorization")
    save_parser.add_argument("--timestamp", help="Timestamp (ISO format)")
    save_parser.add_argument("--memory-type", choices=["core", "archival", "context", "persona", "human"],
                            help="Memory type (for generic)")
    save_parser.add_argument("--priority", choices=["low", "medium", "high"],
                            help="Priority (for action items)")
    save_parser.set_defaults(func=cmd_save)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search memories")
    search_parser.add_argument("--query", "-q", required=True, help="Search query")
    search_parser.add_argument("--type", "-t", help="Filter by memory type")
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    search_parser.set_defaults(func=cmd_search)
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get memory statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check server health")
    health_parser.set_defaults(func=cmd_health)
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup memories")
    backup_parser.add_argument("--output", "-o", help="Output directory")
    backup_parser.set_defaults(func=cmd_backup)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List agents or memories")
    list_parser.add_argument("target", choices=["agents", "memories"], help="What to list")
    list_parser.add_argument("--type", "-t", help="Filter by memory type (for memories)")
    list_parser.add_argument("--limit", "-l", type=int, default=100, help="Max results")
    list_parser.set_defaults(func=cmd_list)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

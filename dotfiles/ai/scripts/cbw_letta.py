#!/usr/bin/env python3
"""
Letta Automation Wrapper - Simplified commands for common Letta operations
"""

import argparse
import subprocess
import sys


def run_letta_cli(args):
    """Run letta-memory-cli with arguments."""
    cmd = ["letta-memory-cli"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def agent_list():
    """List all agents."""
    return run_letta_cli(["agent", "list"])


def agent_create(name, persona, human):
    """Create a new agent."""
    return run_letta_cli([
        "agent", "create",
        "--name", name,
        "--persona", persona,
        "--human", human
    ])


def memory_save(agent, content, memory_type="archival", tags=None):
    """Save a memory."""
    args = [
        "memory", "save",
        "--agent", agent,
        "--content", content,
        "--type", memory_type
    ]
    if tags:
        args.extend(["--tags", tags])
    return run_letta_cli(args)


def memory_search(agent, query, memory_type=None, limit=10):
    """Search memories."""
    args = [
        "memory", "search",
        "--agent", agent,
        "--query", query,
        "--limit", str(limit)
    ]
    if memory_type:
        args.extend(["--type", memory_type])
    return run_letta_cli(args)


def health_check():
    """Check server health."""
    return run_letta_cli(["health"])


def backup_agent(agent, path="~/backups/letta"):
    """Backup an agent."""
    import os
    path = os.path.expanduser(path)
    os.makedirs(path, exist_ok=True)
    return run_letta_cli([
        "backup", "create",
        "--agent", agent,
        "--path", path
    ])


def main():
    parser = argparse.ArgumentParser(description='Letta Automation Wrapper')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Agent commands
    agent_parser = subparsers.add_parser('agent', help='Agent operations')
    agent_sub = agent_parser.add_subparsers(dest='agent_cmd')
    
    agent_list_cmd = agent_sub.add_parser('list', help='List agents')
    agent_list_cmd.set_defaults(func=lambda _: agent_list())
    
    agent_create_cmd = agent_sub.add_parser('create', help='Create agent')
    agent_create_cmd.add_argument('--name', required=True)
    agent_create_cmd.add_argument('--persona', required=True)
    agent_create_cmd.add_argument('--human', required=True)
    agent_create_cmd.set_defaults(func=lambda args: agent_create(args.name, args.persona, args.human))
    
    # Memory commands
    memory_parser = subparsers.add_parser('memory', help='Memory operations')
    memory_sub = memory_parser.add_subparsers(dest='memory_cmd')
    
    mem_save = memory_sub.add_parser('save', help='Save memory')
    mem_save.add_argument('--agent', required=True)
    mem_save.add_argument('--content', required=True)
    mem_save.add_argument('--type', default='archival')
    mem_save.add_argument('--tags')
    mem_save.set_defaults(func=lambda args: memory_save(args.agent, args.content, args.type, args.tags))
    
    mem_search = memory_sub.add_parser('search', help='Search memories')
    mem_search.add_argument('--agent', required=True)
    mem_search.add_argument('--query', required=True)
    mem_search.add_argument('--type')
    mem_search.add_argument('--limit', type=int, default=10)
    mem_search.set_defaults(func=lambda args: memory_search(args.agent, args.query, args.type, args.limit))
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check health')
    health_parser.set_defaults(func=lambda _: health_check())
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup agent')
    backup_parser.add_argument('--agent', required=True)
    backup_parser.add_argument('--path', default='~/backups/letta')
    backup_parser.set_defaults(func=lambda args: backup_agent(args.agent, args.path))
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())

"""
CLI Operations Skill Package

Provides command-line interface operations for Letta server and other tools.
This skill wraps CLI commands into reusable functions for AI agents.
"""

from .cli_operations import (
    run_letta_command,
    search_letta_memories,
    store_letta_memory,
    list_letta_agents,
    check_letta_health,
    run_sql_query,
    search_postgres_memories,
    get_memory_stats,
    CLIOperations,
)

__version__ = "1.0.0"
__all__ = [
    "run_letta_command",
    "search_letta_memories",
    "store_letta_memory",
    "list_letta_agents",
    "check_letta_health",
    "run_sql_query",
    "search_postgres_memories",
    "get_memory_stats",
    "CLIOperations",
]

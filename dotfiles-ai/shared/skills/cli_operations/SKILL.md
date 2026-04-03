# CLI Operations Skill
# Command-line interface operations for Letta and other tools
# Location: ~/dotfiles/ai/skills/cli_operations/SKILL.md

name: cli_operations
description: "Command-line interface operations for Letta server and other tools"
version: 1.0.0

## Overview

This skill provides command-line interface operations for interacting with Letta server and other tools. It wraps CLI commands into reusable functions that can be used by any AI agent.

## Operations

### `run_letta_command`
Run a Letta CLI command and return the result.

**Parameters:**
- `command` (list): List of command arguments (e.g., ["archival-search", "agent-id", "query"])
- `timeout` (int, optional): Command timeout in seconds (default: 30)

**Returns:** Dict with success status, data, and raw output

**Example:**
```python
result = cli.run_letta_command(["archival-search", "agent-xxx", "query"])
```

### `search_letta_memories`
Search memories using Letta CLI.

**Parameters:**
- `agent_id` (string): Agent ID to search
- `query` (string): Search query
- `limit` (int, optional): Max results (default: 10)

**Returns:** List of memory results

### `store_letta_memory`
Store a memory using Letta CLI.

**Parameters:**
- `agent_id` (string): Agent ID to store to
- `text` (string): Memory text
- `tags` (list, optional): Tags for categorization

**Returns:** Dict with success status

### `list_letta_agents`
List all agents in Letta server.

**Returns:** List of agent objects

### `check_letta_health`
Check Letta server health status.

**Returns:** Dict with health status

### `backup_letta_agent`
Backup an agent's data to JSON file.

**Parameters:**
- `agent_id` (string): Agent ID to backup
- `output_file` (string): Output file path

**Returns:** Dict with success status

### `run_sql_query`
Run a SQL query against PostgreSQL database.

**Parameters:**
- `query` (string): SQL query to execute
- `params` (tuple, optional): Query parameters
- `fetch` (bool, optional): Whether to fetch results (default: True)

**Returns:** Query results or success status

### `search_postgres_memories`
Search memories in PostgreSQL database.

**Parameters:**
- `search_text` (string): Text to search for
- `memory_type` (string, optional): Filter by memory type
- `tags` (list, optional): Filter by tags
- `limit` (int, optional): Max results (default: 50)

**Returns:** List of memory objects

## Usage Examples

### Memory Search Protocol
```python
# Semantic search via Letta CLI
results = cli.search_letta_memories("agent-xxx", "AI skills")

# Text search via PostgreSQL
memories = cli.search_postgres_memories("configuration", tags=["opencode"])
```

### Memory Storage Protocol
```python
# Store via Letta CLI
cli.store_letta_memory("agent-xxx", "Memory text", ["tag1", "tag2"])

# Store via PostgreSQL
cli.run_sql_query(
    "INSERT INTO letta_memories (memory_type, title, content, tags) VALUES (%s, %s, %s, %s)",
    ("general", "Title", "Content", ["tag1"])
)
```

## Automatic Behavior

When this skill is loaded, agents can:

1. **Run any CLI command** through the `run_letta_command` function
2. **Search memories** via multiple protocols
3. **Store memories** in different backends
4. **Manage agent data** with backup/restore operations

# Memory Sync Skill
# Synchronize memories between PostgreSQL and Letta server
# Location: ~/dotfiles/ai/skills/memory_sync/SKILL.md

name: memory_sync
description: "Synchronize memories between PostgreSQL database and Letta server"
version: 1.0.0

## Overview

This skill provides synchronization capabilities between the PostgreSQL memory database and the Letta server. It allows:
- Syncing memories from PostgreSQL to Letta archival memory
- Backing up Letta agent data to PostgreSQL
- Migrating memories between different storage backends
- Conflict resolution and deduplication

## Operations

### `sync_postgres_to_letta`
Sync memories from PostgreSQL to Letta server.

**Parameters:**
- `agent_id` (string): Target agent ID in Letta
- `memory_types` (list, optional): Memory types to sync (default: all)
- `limit` (int, optional): Max memories to sync (default: 100)
- `dry_run` (bool, optional): Preview sync without executing (default: False)

**Example:**
```python
result = memory_sync.sync_postgres_to_letta(
    agent_id="agent-xxx",
    memory_types=["conversation", "decision"],
    limit=50
)
```

### `sync_letta_to_postgres`
Sync memories from Letta server to PostgreSQL.

**Parameters:**
- `agent_id` (string): Source agent ID in Letta
- `memory_types` (list, optional): Memory types to sync (default: all)
- `limit` (int, optional): Max memories to sync (default: 100)

**Returns:** Sync results

### `backup_agent_data`
Backup Letta agent data to PostgreSQL.

**Parameters:**
- `agent_id` (string): Agent ID to backup
- `backup_name` (string, optional): Backup name (default: timestamp-based)

**Returns:** Backup results

### `restore_agent_data`
Restore agent data from PostgreSQL backup.

**Parameters:**
- `backup_id` (string): Backup ID to restore
- `agent_id` (string, optional): Target agent ID (default: original)

**Returns:** Restore results

### `deduplicate_memories`
Remove duplicate memories across storage backends.

**Parameters:**
- `agent_id` (string, optional): Filter by agent
- `memory_type` (string, optional): Filter by memory type
- `strategy` (string): Deduplication strategy (hash, content, semantic)

**Returns:** Deduplication results

### `resolve_conflicts`
Resolve conflicts between PostgreSQL and Letta memories.

**Parameters:**
- `conflicts` (list): List of conflicting memories
- `resolution_strategy` (string): Resolution strategy (newest, oldest, postgres, letta)

**Returns:** Resolution results

## Sync Strategies

### Full Sync
Syncs all memories from source to destination.
```python
memory_sync.sync_postgres_to_letta(agent_id="agent-xxx")
```

### Incremental Sync
Syncs only new or updated memories since last sync.
```python
memory_sync.sync_postgres_to_letta(
    agent_id="agent-xxx",
    incremental=True,
    last_sync_timestamp="2026-03-24T12:00:00Z"
)
```

### Filtered Sync
Syncs only specific types or tags.
```python
memory_sync.sync_postgres_to_letta(
    agent_id="agent-xxx",
    memory_types=["conversation", "decision"],
    tags=["important", "project"]
)
```

## Conflict Resolution

### Timestamp-based
Newest memory wins.
```python
memory_sync.resolve_conflicts(
    conflicts=conflict_list,
    resolution_strategy="newest"
)
```

### Source-based
PostgreSQL or Letta memories take precedence.
```python
memory_sync.resolve_conflicts(
    conflicts=conflict_list,
    resolution_strategy="postgres"
)
```

### Manual Review
Flag conflicts for manual review.
```python
memory_sync.resolve_conflicts(
    conflicts=conflict_list,
    resolution_strategy="manual"
)
```

## Automatic Behavior

When this skill is loaded, agents can:

1. **Sync memories** between PostgreSQL and Letta server
2. **Backup agent data** for disaster recovery
3. **Resolve conflicts** when memories differ between backends
4. **Deduplicate memories** to reduce storage usage

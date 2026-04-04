# Letta Server Skill
# Automatic memory management for AI agents
# Location: ~/dotfiles/ai/skills/letta_server/SKILL.md

name: letta_server
description: "Comprehensive Letta server integration for automatic memory management"
version: 1.0.0

## Overview

This skill provides complete Letta server integration for AI agents. It automatically:
- Saves all conversations
- Extracts entities
- Creates memories from decisions and action items
- Enables cross-agent search

## Operations

### `save_conversation`
Save entire conversation to Letta archival memory.

**Parameters:**
- `messages` (list): Conversation messages
- `tags` (list, optional): Tags for categorization

**Example:**
```python
letta.save_conversation([
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
], tags=["greeting"])
```

### `search_memories`
Search for relevant memories.

**Parameters:**
- `query` (string): Search query
- `memory_type` (string, optional): Filter by type
- `limit` (int, optional): Max results (default: 10)

**Example:**
```python
results = letta.search_memories("entity extraction", limit=5)
```

### `get_memory_stats`
Get memory statistics for current agent.

**Returns:** Dict with memory counts, storage usage, etc.

### `check_server_health`
Check Letta server health status.

**Returns:** Dict with status and version

### `setup_agent_memory`
Initialize agent memory in Letta.

**Parameters:**
- `agent_name` (string): Name of agent

### `sync_agent_context`
Synchronize agent context with Letta.

### `extract_and_store_entities`
Automatically extract entities from text.

**Parameters:**
- `text` (string): Text to extract from
- `entity_types` (list, optional): Types to extract

**Extracts:**
- Code blocks
- File paths
- URLs
- Commands
- Key entities

### `create_memory_from_decision`
Create memory from important decision.

**Parameters:**
- `decision` (string): The decision made
- `context` (string): Additional context

### `create_memory_from_action_item`
Create memory from action item.

**Parameters:**
- `action_item` (string): Task description
- `priority` (string): low/medium/high

## Advanced Search Operations

### `advanced_memory_search`
Advanced memory search with multiple protocols.

**Parameters:**
- `query` (string, optional): Search query
- `search_type` (string): Type of search (semantic, tags, text, recent, stats)
- `agent_id` (string, optional): Agent ID to search
- `tags` (list, optional): Tags to filter by
- `memory_type` (string, optional): Memory type to filter by
- `limit` (int, optional): Max results (default: 10)

**Example:**
```python
# Semantic search
results = letta.advanced_memory_search("AI skills", search_type="semantic")

# Tag-based search
results = letta.advanced_memory_search(search_type="tags", tags=["opencode", "configuration"])

# Text search
results = letta.advanced_memory_search("configuration", search_type="text")

# Get statistics
stats = letta.advanced_memory_search(search_type="stats")
```

### `cross_agent_search`
Search across multiple agents.

**Parameters:**
- `query` (string): Search query
- `agent_ids` (list, optional): List of agent IDs to search

**Example:**
```python
results = letta.cross_agent_search("entity extraction", agent_ids=["agent-xxx", "agent-yyy"])
```

## Automatic Behavior

When this skill is loaded, the agent automatically:

1. **Saves every conversation** to Letta archival memory
2. **Extracts entities** from all messages
3. **Searches prior memories** before starting tasks
4. **Provides advanced search protocols** for memory retrieval
4. **Creates decision memories** when important choices are made
5. **Creates action item memories** when tasks are identified

## Usage in Agent Config

```yaml
# agents/<agent>/config.yaml
skills:
  - letta_server

tools:
  - letta_server.save_conversation
  - letta_server.search_memories
  - letta_server.get_memory_stats
  - letta_server.check_server_health
  - letta_server.extract_and_store_entities
```

## Environment Variables

```bash
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_API_KEY="your-api-key"
```

## Implementation

See: `~/dotfiles/ai/packages/letta_integration/`

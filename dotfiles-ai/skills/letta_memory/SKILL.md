---
name: letta_memory
description: "Unified Letta memory operations for all AI agents. Core memory, archival storage, cross-agent search, and memory lifecycle management. Use this as the primary memory interface for all agent operations."
version: "2.0.0"
category: memory
---

# Letta Unified Memory Skill

Primary memory interface for all AI agents on the CBW server. Leverages the self-hosted Letta server (v0.16.6) for persistent, searchable, cross-agent memory.

## When to Use

- Before starting ANY task: search memory for prior context
- After completing ANY task: store results and decisions
- When asked about past work, configurations, or decisions
- When coordinating between multiple agents
- When the user asks to "remember" or "recall" something

## Prerequisites

- Letta server running at `localhost:8283` (Docker container `letta-server`)
- Letta CLI: `~/bin/letta` (Node.js wrapper)
- Secrets sourced: `source ~/.bash_secrets`

## Operations

### 1. Search Memories (Before Every Task)

```bash
# Semantic search
~/bin/letta archival-search <agent-id> "search query"

# Example: search for prior Docker configurations
~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "docker compose setup"
```

### 2. Store Memory (After Every Task)

```bash
# Store with tags
~/bin/letta archival-insert <agent-id> "Description of what was done" "tag1,tag2,tag3"

# Example
~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
  "2026-04-02: Configured nginx reverse proxy for port 8083" \
  "nginx,proxy,config"
```

### 3. List All Memories

```bash
~/bin/letta archival <agent-id>
```

### 4. View Core Memory Blocks

```bash
~/bin/letta memory <agent-id>
```

### 5. Update Core Memory Block

```bash
~/bin/letta memory-update <agent-id> <label> "new value"
```

### 6. Create Reusable Memory Block

```bash
~/bin/letta block create "label-name" "block content"
~/bin/letta block attach "block-<uuid>" "<agent-id>"
```

### 7. Cross-Agent Search

Search across all known agents:
```bash
# Search each agent sequentially
for agent in agent-e5e8aab5-9e87-45c1-8025-700503b524c6; do
  echo "=== Agent: $agent ==="
  ~/bin/letta archival-search "$agent" "query"
done
```

### 8. Batch Store (from JSON file)

```bash
~/bin/letta batch-store <agent-id> /path/to/memories.json
```

JSON format:
```json
[
  {"text": "Fact to remember", "tags": ["tag1", "tag2"]},
  {"text": "Another fact", "tags": ["tag3"]}
]
```

### 9. Health Check

```bash
~/bin/letta health
```

## Agent IDs

| Agent | ID |
|-------|----|
| kilocode | `agent-e5e8aab5-9e87-45c1-8025-700503b524c6` |

## Memory Types in Letta

- **Core Memory**: Permanent agent knowledge (persona, human info, system state)
- **Archival Memory**: Long-term searchable storage (conversations, decisions, facts)
- **Message History**: Full conversation logs

## Auto-Save Pattern

Every agent should follow this pattern:

1. **Before task**: `archival-search` for relevant prior work
2. **During task**: Reference found memories to avoid duplication
3. **After task**: `archival-insert` with description + tags

## Tagging Convention

Always use descriptive tags for searchability:
- Category: `config`, `docker`, `nginx`, `database`, `skills`, `security`
- Agent: `kilocode`, `opencode`, `claude`
- Type: `decision`, `setup`, `fix`, `feature`, `investigation`
- Date: Include date in memory text: `YYYY-MM-DD:`

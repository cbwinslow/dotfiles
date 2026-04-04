# Letta Memory Skill
# Unified memory interface for ALL AI agents on the CBW server.

## What This Skill Does

Provides a single interface to all Letta memory operations:
- **Before every task**: Search archival memory for prior context
- **After every task**: Store results with tags for future retrieval
- **Core memory blocks**: View and update persistent agent knowledge
- **Cross-agent search**: Find memories from other agents
- **Health check**: Verify Letta server is operational

## When to Use This Skill

- Starting any non-trivial task → run `before_task` (search memory)
- Completing any task → run `after_task` (store result)
- User asks "what do we know about X?" → search memory
- User asks to "remember" something → store memory
- Coordinating with another agent → cross-agent search

## Prerequisites

- Letta server running: `~/bin/letta health` should return `{"status":"ok"}`
- Secrets sourced: `source ~/.bash_secrets`
- Agent exists: `agent-e5e8aab5-9e87-45c1-8025-700503b524c6` (kilocode)

## Files

- `SKILL.md` — Full skill documentation with all operations and examples
- `agents.md` — THIS FILE

## Quick Command Reference

```bash
source ~/.bash_secrets
AGENT="agent-e5e8aab5-9e87-45c1-8025-700503b524c6"

# Search
~/bin/letta archival-search "$AGENT" "query"

# Store
~/bin/letta archival-insert "$AGENT" "text" "tag1,tag2"

# View blocks
~/bin/letta memory "$AGENT"

# Update block
~/bin/letta memory-update "$AGENT" skills-config "new value"

# Health
~/bin/letta health
```

## Why This Exists

User requirement: "I need every AI agent to search memory before starting work and store results after. This must be the universal pattern across all agents on the server."

This skill is the primary interface to that pattern. Without it, agents lose context between sessions and duplicate work.

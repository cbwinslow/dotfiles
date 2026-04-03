---
name: cross-agent-memory
version: "1.0.0"
description: "Enable seamless memory sharing across all AI agents - Claude, Windsurf, Cline, Codex, and more share the same Letta memory pool"
category: collaboration
agents: [claude, cline, codex, windsurf, kilocode, opencode, openclaw, gemini, qwen, vscode]
tags: [letta, cross-agent, shared-memory, collaboration, knowledge-transfer]
triggers:
  - AGENT_SWITCH
  - CONTEXT_REQUEST
  - MEMORY_SYNC
---

# Cross-Agent Memory Sharing Workflow

## Overview

This workflow enables **true collaboration** between different AI agents by giving them access to a **shared memory pool** powered by Letta. When you switch from Claude to Windsurf, Windsurf can see what you and Claude were working on. When Cline solves a problem, Codex can recall that solution later.

## The Problem It Solves

**Without Cross-Agent Memory:**
```
You: "Claude, help me fix this Docker issue"
Claude: "Fixed! Here's the solution..."
[Later, you open Windsurf]
You: "Help me with Docker"
Windsurf: "Sure, what Docker issue are you having?"
You: 😤 "We JUST solved this with Claude!"
```

**With Cross-Agent Memory:**
```
You: "Claude, help me fix this Docker issue"
Claude: "Fixed! I'll save this solution..."
[Later, you open Windsurf]
You: "Help me with Docker"
Windsurf: "I see you and Claude solved a Docker networking 
          issue earlier. The fix was to add --network=host. 
          Is this the same issue or something new?"
You: 😊 "Wow, you're already caught up!"
```

## How It Works

### Shared Memory Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Claude    │────→│             │←────│  Windsurf   │
│   (Agent)   │     │   Letta     │     │   (Agent)   │
└─────────────┘     │   Memory    │     └─────────────┘
                     │   Server    │
┌─────────────┐     │             │     ┌─────────────┐
│    Cline    │────→│             │←────│    Codex    │
│   (Agent)   │     │             │     │   (Agent)   │
└─────────────┘     └─────────────┘     └─────────────┘
        │                    ↑                    │
        └────────────────────┘────────────────────┘
                      Shared Pool
```

All agents read from and write to the **same** Letta memory instance:
- **Archival Memory**: Long-term storage of solutions, conversations, patterns
- **Core Memory**: Active context shared across all sessions
- **Recall**: Vector search finds relevant memories regardless of which agent created them

## Workflow Triggers

### 1. AGENT_SWITCH
```
TRIGGER: User switches from one agent to another
ACTION:
  - New agent searches Letta for recent sessions
  - Recalls context from previous agent conversations
  - Acknowledges continuity: "I see you were working with Claude on..."
  - Offers to continue or pivot
```

**Example:**
```markdown
User switches from Claude Code to Windsurf

Windsurf Action:
1. Search Letta: "Recent sessions with context"
2. Find: "Session #5678 - Claude Code - React performance optimization"
3. Recall: Component profiling, useMemo usage, re-render issues
4. Response: "Hi! I see you and Claude were optimizing React performance 
            for the dashboard component. You identified unnecessary re-renders 
            in the Table component. Want to continue with those optimizations, 
            or work on something else?"
```

### 2. CONTEXT_REQUEST
```
TRIGGER: User asks about previous work or context
ACTION:
  - Search across ALL agent sessions for relevant context
  - Aggregate findings from multiple sources
  - Present unified view: "Based on your work with Claude, Cline, and Windsurf..."
```

**Example:**
```markdown
User: "What have I been working on this week?"

Any Agent Action:
1. Search Letta: Sessions from last 7 days
2. Aggregate:
   - Monday (Claude): API design for user auth
   - Tuesday (Windsurf): Frontend implementation
   - Wednesday (Cline): Database schema updates
   - Thursday (You): Manual code review
3. Response: "This week you've worked across multiple agents:
   - With Claude on API authentication design
   - With Windsurf on the React frontend
   - With Cline on PostgreSQL schema changes
   Would you like a summary of any specific area?"
```

### 3. MEMORY_SYNC
```
TRIGGER: Periodic synchronization or explicit sync request
ACTION:
  - Verify all agents using same Letta agent_id
  - Reconcile any divergent memories
  - Update shared context
  - Ensure consistency across agents
```

## Setup & Configuration

### 1. Shared Agent ID
All agents must use the **same** Letta agent ID:

```bash
# Set in your shell profile (applies to all agents)
export LETTA_AGENT_ID="cbwinslow-shared-agent"
export LETTA_SERVER_URL="http://localhost:8283"
```

### 2. Agent-Specific Configuration

#### For Claude Code (`~/.claude/config.json`)
```json
{
  "letta": {
    "agent_id": "cbwinslow-shared-agent",
    "server_url": "http://localhost:8283",
    "auto_recall": true,
    "auto_save": true
  }
}
```

#### For Windsurf (`~/.windsurf/settings.json`)
```json
{
  "letta_integration": {
    "agent_id": "cbwinslow-shared-agent",
    "server_url": "http://localhost:8283",
    "shared_memory": true,
    "recall_on_start": true
  }
}
```

#### For Cline (`~/.cline/config.json`)
```json
{
  "memory": {
    "provider": "letta",
    "agent_id": "cbwinslow-shared-agent",
    "cross_agent_sync": true
  }
}
```

### 3. Verification Script
```bash
#!/bin/bash
# verify-cross-agent-setup.sh

echo "Checking Cross-Agent Memory Setup..."
echo ""

AGENTS=("claude" "cline" "codex" "windsurf" "kilocode" "opencode")
AGENT_ID="${LETTA_AGENT_ID:-cbwinslow-shared-agent}"

echo "Shared Agent ID: ${AGENT_ID}"
echo ""

for agent in "${AGENTS[@]}"; do
  echo "Checking ${agent}..."
  
  # Check if agent config references the shared agent_id
  case "${agent}" in
    claude) config_file="${HOME}/.claude/config.json" ;;
    cline) config_file="${HOME}/.cline/config.json" ;;
    codex) config_file="${HOME}/.codex/config.json" ;;
    windsurf) config_file="${HOME}/.windsurf/settings.json" ;;
    kilocode) config_file="${HOME}/.config/kilo/kilo.jsonc" ;;
    opencode) config_file="${HOME}/.config/opencode/config.json" ;;
  esac
  
  if [ -f "${config_file}" ]; then
    if grep -q "${AGENT_ID}" "${config_file}" 2>/dev/null; then
      echo "  ✓ ${agent} configured with shared agent_id"
    else
      echo "  ⚠ ${agent} config found but may not use shared agent_id"
    fi
  else
    echo "  ✗ ${agent} config not found"
  fi
done

echo ""
echo "Testing Letta server connection..."
if curl -s "http://localhost:8283/health" > /dev/null; then
  echo "  ✓ Letta server is running"
else
  echo "  ✗ Letta server not reachable"
fi
```

## Usage Patterns

### Pattern 1: Continue Work Across Agents
```markdown
Scenario: You're working on a complex feature

With Claude Code (Deep Thinking):
- Design the architecture
- Plan the implementation
- Save to memory: "Feature X architecture designed"

With Windsurf (Fast Implementation):
- Windsurf sees the architecture from memory
- "I see you designed this with Claude. Let's implement it."
- Codes the solution based on Claude's design

With Cline (Debugging):
- Cline sees both design and implementation
- "I see the architecture and implementation. Let me debug the issue."
- Fixes bugs with full context
```

### Pattern 2: Specialized Agent Roles
```markdown
Define specific roles for each agent:

- **Claude**: Architecture & Design (saves high-level plans)
- **Windsurf**: Implementation (saves code solutions)
- **Cline**: Debugging & Optimization (saves fixes)
- **Codex**: Code Review (saves review notes)

All share memories, so each agent builds on the others' work.
```

### Pattern 3: Knowledge Accumulation
```markdown
Week 1:
- Claude: "Learned that React useEffect cleanup is important"
- Saved to memory

Week 2:
- Windsurf encounters similar issue
- Recalls: "I see Claude learned about useEffect cleanup patterns"
- Applies the knowledge

Week 3:
- Cline teaches a new pattern
- Adds to shared knowledge base

Result: All agents get smarter over time, regardless of which one you use
```

## Advanced Features

### Cross-Agent Session Handoff
```python
from letta_integration import CrossAgentHandoff

# When switching from Claude to Windsurf
handoff = CrossAgentHandoff(
    from_agent="claude",
    to_agent="windsurf",
    session_id="current-session-123"
)

# Transfer context
context = handoff.get_transfer_context()
# Includes:
# - Recent conversation summary
# - Open files and cursor positions
# - Current task status
# - Relevant memories
```

### Memory Attribution
```python
# See which agent created which memory
from letta_integration import MemoryAttribution

attribution = MemoryAttribution()
memory = attribution.get_memory_with_source(
    memory_id="abc-123"
)

print(f"Created by: {memory.agent_name}")  # "claude"
print(f"At: {memory.timestamp}")
print(f"Content: {memory.content}")
```

### Conflict Resolution
When agents have conflicting information:
```python
from letta_integration import MemoryReconciliation

reconciler = MemoryReconciliation()
resolution = reconciler.resolve_conflict(
    memory_1=claude_memory,
    memory_2=windsurf_memory,
    strategy="merge"  # or "latest", "agent_priority"
)
```

## Best Practices

### 1. Consistent Tagging
All agents should use the same tag conventions:
```python
# Good - consistent across agents
tags = ["react", "performance", "useeffect", "cleanup"]

# Bad - inconsistent
# Claude: ["React.js", "perf optimization"]
# Windsurf: ["react", "speed"]
# Cline: ["REACT", "useEffect"]
```

### 2. Agent Signatures
Include agent name in memory metadata:
```python
memory.save(
    content="Solution to Docker issue",
    metadata={
        "agent": "claude",  # Which agent created this
        "task": "docker-setup",
        "version": "1.0"
    }
)
```

### 3. Session Boundaries
Clearly mark when you're switching contexts:
```markdown
User: "Actually, let's switch to a different task"
→ Agent saves current session state
→ Clears short-term context
→ Starts fresh while keeping archival access
```

### 4. Periodic Sync
Run sync every few sessions:
```bash
# Reconcile memories across agents
letta-sync-memories --agents=all --dry-run
letta-sync-memories --agents=all --apply
```

## Troubleshooting

### Issue: Agents don't see each other's memories
**Solutions:**
1. ✅ Verify all agents use same `agent_id`
2. ✅ Check Letta server is accessible from all agents
3. ✅ Ensure `shared_memory=true` in configs
4. ✅ Test with `letta-list-memories` from each agent

### Issue: Memory conflicts between agents
**Solutions:**
1. Use memory versioning
2. Implement agent priority (e.g., human > claude > windsurf)
3. Manual reconciliation with `letta-reconcile`

### Issue: Too much noise in shared memory
**Solutions:**
1. Filter by agent: `search --agent=claude`
2. Use time windows: `search --since="2 days ago"`
3. Tag filtering: `search --tags=important`
4. Archive old memories: `letta-archive --older-than="30 days"`

## Privacy & Security

### Shared vs Private Memories
```python
# Shared memory (all agents see this)
memory.save(content="Docker fix", scope="shared")

# Private memory (only creating agent sees this)
memory.save(content="Personal preference", scope="private")
```

### Access Control
```json
{
  "memory_policies": {
    "claude": ["read:all", "write:all"],
    "windsurf": ["read:all", "write:code_only"],
    "guest_agent": ["read:limited"]
  }
}
```

## Success Metrics

Track cross-agent memory effectiveness:
- **Recall Rate**: % of times relevant memory is found
- **Context Continuity**: % of agent switches with smooth handoff
- **Knowledge Transfer**: # of solutions used across multiple agents
- **Time Saved**: Estimated time not spent re-explaining context

---

**Workflow Version**: 1.0.0  
**Requires**: Letta server, letta-integration skill v2.0+  
**Compatible Agents**: All agents with shared agent_id configured  
**Network**: Requires localhost:8283 access for all agents

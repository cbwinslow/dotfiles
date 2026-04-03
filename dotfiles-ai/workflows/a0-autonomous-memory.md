---
name: a0-autonomous-workflow
description: Complete Agent-Zero style autonomous memory workflow with automatic store/recall/RAG
version: "1.0.0"
category: memory
tags: [a0, agent-zero, autonomous, memory, rag, automatic]
---

# A0 Autonomous Memory Workflow

## Overview

This workflow enables **true Agent-Zero style** autonomous memory where the AI:
1. **Automatically stores** every interaction, fact, and learning
2. **Automatically recalls** relevant context before each task  
3. **Maintains a RAG database** using Letta's pgvector
4. **Tracks instance IDs** for every conversation session

## The A0 Philosophy

> "The agent should never start from zero. It should always remember."

### Automatic Behaviors

| Trigger | Action | Storage |
|---------|--------|---------|
| Agent starts | Create instance ID, load persona | Core memory blocks |
| User message | Store + auto-extract facts | Archival memory (pgvector) |
| Assistant reply | Store response + learned facts | Archival memory |
| Pre-task | RAG search for context | Retrieved from pgvector |
| Post-task | Store result + learnings | Archival + blocks |
| Session end | Store summary | Archival |

## Quick Start

### 1. Automatic Mode (Recommended)

The skill auto-initializes. Just use it:

```python
from skills.a0_memory import A0Skill

a0 = A0Skill()  # Auto-detects agent, creates instance ID

# That's it! Memory is now automatic.
# But you can also be explicit:
```

### 2. Manual Control

```python
from skills.a0_memory import A0Skill

a0 = A0Skill(agent_name="my_agent")

# Before task - auto-recalls context
context = a0.before_task("Fix the Docker networking issue")
print(context)  # Shows relevant past memories

# Do work...
result = fix_docker_networking()

# After task - auto-stores learnings  
a0.after_task(
    "Fix Docker networking",
    result,
    learned=["Docker host mode fixes DNS issues", "Bridge mode has limitations"]
)
```

## Core Operations

### Store Memory

```python
# Store a fact
a0.store("PostgreSQL 16 uses port 5432 by default", memory_type="fact")

# Store with tags
a0.store(
    "Letta server runs on port 8283",
    memory_type="config",
    tags=["letta", "ports", "important"]
)

# Store task result
a0.store(
    "Successfully deployed to production",
    memory_type="task",
    metadata={"deployment_id": "dep-123", "duration": "5m"}
)
```

### Recall / RAG Search

```python
# Semantic search via pgvector
results = a0.recall("What port does Letta use?", limit=3)
# Returns: [{"content": "Letta server runs on port 8283", "similarity": 0.95, ...}]

# Pure RAG - just the strings
context = a0.rag("Docker networking troubleshooting", limit=5)
# Returns: ["Docker host mode fixes DNS...", "Bridge mode has...", ...]

# Use in prompt
prompt = f"""
Context from memory:
{chr(10).join(a0.rag("my query"))}

Now help with: my query
"""
```

### Memory Blocks (Core Memory)

```python
# Update persona
a0.set_block("persona", "I am a coding assistant specializing in Python")

# Track active projects
a0.update_projects("Currently working on: Letta integration (March 2026)")

# Store key knowledge
a0.update_knowledge("Key fact: All agents share the same PostgreSQL database")

# Retrieve
projects = a0.get_block("projects")
```

### Conversation Logging

```python
# Every turn is automatically logged with instance ID
a0.log_interaction(
    user_msg="How do I fix this Docker issue?",
    assistant_msg="You need to use host networking mode...",
    learned_facts=["Docker host mode for DNS issues"]
)

# Get current instance info
print(a0.get_instance_id())  # windsurf_20260329183045_a1b2c3d4
print(a0.get_info())
# {
#   "instance_id": "windsurf_20260329183045_a1b2c3d4",
#   "agent_name": "windsurf",
#   "conversation_id": "conv-xxx",
#   "message_count": 42
# }
```

## Instance Tracking

Each agent session gets a unique instance ID:

```
Format: {agent_name}_{timestamp}_{random}
Example: windsurf_20260329183045_a1b2c3d4
```

All memories are tagged with this ID for tracking.

### Cross-Session Recall

```python
# Search across ALL your instances
all_memories = a0.search_all_agents("Docker fix", limit=10)

# Filter by instance
instance_memories = [
    m for m in all_memories 
    if m.get("instance_id") == a0.get_instance_id()
]
```

## Complete Workflow Example

```python
from skills.a0_memory import A0Skill, store, recall, before_task, after_task

# 1. Initialize (auto-detects agent)
a0 = A0Skill()
print(f"Instance: {a0.get_instance_id()}")

# 2. Pre-task: recall context
task = "Debug why the API is returning 500 errors"
context = before_task(task)
print(f"Relevant memories found: {len(context)}")

# 3. Do the work (with context-aware prompt)
prompt = f"""
Previous context:
{context}

Task: {task}
"""
result = run_llm(prompt)

# 4. Post-task: store learnings
after_task(
    task,
    result,
    learned=[
        "500 errors caused by missing DB connection pool",
        "Fixed by increasing max_connections to 100",
        "Environment variable DB_POOL_SIZE controls this"
    ]
)

# 5. Also store key facts
store(
    "DB_POOL_SIZE env var controls PostgreSQL connection pool",
    tags=["postgresql", "config", "important"]
)

# 6. Update projects block
a0.update_projects("API debugging: COMPLETED - connection pool issue fixed")
```

## Decorator Mode

Wrap any function with automatic memory:

```python
from skills.a0_memory import A0Skill

@A0Skill.wrap
def analyze_code(code: str, memory_context=None):
    """This function automatically gets memory context."""
    # memory_context contains relevant past analysis
    
    result = do_analysis(code)
    
    # Return with facts to auto-store
    return {
        "result": result,
        "learned": ["Pattern X causes performance issues"]
    }
```

## Environment Variables

```bash
# Required
export LETTA_SERVER_URL="http://localhost:8283"

# Optional
export LETTA_AUTO_MEMORY="true"
export A0_AUTO_INIT="true"
export AI_AGENT_NAME="my_agent"  # Override auto-detection
```

## Database Schema

Memories stored in PostgreSQL with pgvector:

```sql
-- Archival memories with vector embeddings
SELECT * FROM archival_memory 
WHERE agent_id = 'agent-xxx'
ORDER BY embedding <-> query_embedding
LIMIT 5;

-- Memory blocks (core memory)
SELECT * FROM memory_blocks 
WHERE agent_id = 'agent-xxx' AND label = 'projects';

-- Conversations by instance
SELECT * FROM conversations 
WHERE metadata->>'instance_id' = 'windsurf_20260329183045_a1b2c3d4';
```

## Best Practices

1. **Let it be automatic** - Don't manually store everything; auto-extraction works
2. **Tag important facts** - Use tags for critical info you want to find later
3. **Update blocks regularly** - Keep projects/knowledge blocks current
4. **Use RAG for context** - Always do `a0.rag()` before complex tasks
5. **One instance per session** - Let the skill manage instance IDs

## Troubleshooting

### Memory not storing
```python
info = a0.get_info()
print(info["initialized"])  # Should be True
print(info["agent_id"])     # Should have UUID
```

### Can't recall
```bash
# Check Letta server
curl http://localhost:8283/v1/health

# Check PostgreSQL
psql -c "SELECT count(*) FROM archival_memory;"
```

### Cross-agent search empty
All agents must use the same Letta server URL and PostgreSQL database.

## Integration with Other Skills

```yaml
# In your agent config
skills:
  - a0_memory              # This skill
  - bitwarden_secrets      # Auto-load credentials
  - cross_agent_search     # Search all agents

tools:
  - a0_memory.store        # Explicit store tool
  - a0_memory.recall       # Explicit recall tool
  - a0_memory.rag          # RAG search tool
```

## Related

- `autonomous_memory/` - Base autonomous memory (replaced by this)
- `cross-agent-memory.md` - Cross-agent memory sharing
- `letta_integration/` - Low-level Letta client
- `letta-deployment-guide.md` - Server setup

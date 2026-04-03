# Autonomous Memory Architecture for AI Agents

## Executive Summary

This document describes the self-hosted autonomous memory system for all AI agents, using **Letta** with **bare-metal PostgreSQL 16 + pgvector**. The system provides zero-intervention memory management - agents automatically recall relevant context and store new learnings.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI AGENTS (Cline, KiloCode, OpenClaw, etc.)       │
│                                                                               │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │   Coding Agent       │  │   Ops Agent          │  │  Research Agent  │  │
│  │   - Python/TS        │  │   - Infrastructure   │  │  - Analysis      │  │
│  │   - Refactoring      │  │   - Docker/K8s       │  │  - Investigation │  │
│  └──────────┬───────────┘  └──────────┬───────────┘  └────────┬─────────┘  │
└─────────────┼─────────────────────────┼───────────────────────┼────────────┘
              │                         │                       │
              └─────────────┬───────────┴───────────┬───────────┘
                            │                       │
              ┌─────────────▼───────────────────────▼─────────────┐
              │     AutonomousMemoryManager (Python)            │
              │     ─────────────────────────────────           │
              │     • Pre-task hook: Auto-retrieve context      │
              │     • Post-task hook: Auto-store learnings    │
              │     • Memory blocks: persona, human, projects   │
              │     • Archival memory: vector search (pgvector)│
              │     • Cross-agent sharing                       │
              └─────────────────────┬─────────────────────────┘
                                      │ HTTP API
              ┌─────────────────────▼─────────────────────────┐
              │     Letta Server (Docker)                       │
              │     ─────────────────────────                 │
              │     • Port: 8283 (API), 8083 (ADE)           │
              │     • Handles: embeddings, memory tools       │
              │     • Multi-layer memory: core, archival    │
              └─────────────────────┬─────────────────────────┘
                                      │ PostgreSQL Protocol
              ┌─────────────────────▼─────────────────────────┐
              │     PostgreSQL 16 (Bare Metal)                  │
              │     ─────────────────────────                   │
              │     • Extensions: pgvector, uuid-ossp           │
              │     • Database: letta                         │
              │     • Tables: agents, memory_blocks            │
              │              archival_memory, conversations    │
              │              messages                         │
              └───────────────────────────────────────────────┘
```

## Key Components

### 1. AutonomousMemoryManager (`autonomous_memory.py`)

**Location:** `~/dotfiles/ai/packages/letta_integration/autonomous_memory.py`

**Responsibilities:**
- Automatic agent initialization
- Pre-task memory retrieval (`pre_task_hook()`)
- Post-task memory storage (`post_task_hook()`)
- Memory block management (persona, human, projects, knowledge)
- Archival memory search and storage
- Cross-agent session management

**Usage Pattern:**
```python
from letta_integration.autonomous_memory import get_memory

# Auto-initializes from environment
memory = get_memory()

# Before task - retrieves context automatically
context = memory.pre_task_hook("Implement OAuth2 flow")

# After task - stores learnings automatically
memory.post_task_hook(
    task_description="Implemented OAuth2",
    result="Success",
    learned_facts=["PKCE required for mobile", "Use auth0-python v4"]
)
```

### 2. Letta Server

**Deployment:** Docker container
**Ports:** 8083 (ADE Web UI), 8283 (API)
**Database:** External PostgreSQL 16 via `LETTA_PG_URI`

**Key Features:**
- **Core Memory**: Always-in-context memory blocks
- **Archival Memory**: Vector-searchable long-term storage
- **Conversation Memory**: Per-session context
- **Memory Tools**: Built-in tools for agents to self-modify memory

### 3. PostgreSQL 16 + pgvector

**Installation:** Bare metal (not containerized)
**Extensions:**
- `pgvector` - Vector similarity search for embeddings
- `uuid-ossp` - UUID generation

**Key Tables:**
```sql
agents              - Agent configurations and IDs
memory_blocks       - Core memory (persona, human, projects)
archival_memory     - Vector-indexed long-term memories
conversations       - Session containers
messages           - Individual exchanges
```

### 4. Agent Configurations

All agents include autonomous memory in their YAML configs:

```yaml
skills:
  - autonomous_memory  # Auto-recall/save

memory:
  backend: letta_server
  auto_init: true
  blocks:
    persona: "Agent identity and role"
    human: "User preferences and context"
    projects: "Active work tracking"
  hooks:
    pre_task: true   # Search before acting
    post_task: true  # Store after completing
```

## Data Flow

### Pre-Task Flow (Automatic)

1. Agent receives task
2. `pre_task_hook()` triggers automatically
3. Searches archival memory for relevant context
4. Retrieves memory blocks (persona, human, projects)
5. Compiles context summary
6. Injects into agent's working context

### Post-Task Flow (Automatic)

1. Agent completes task
2. `post_task_hook()` triggers automatically
3. Extracts learned facts
4. Stores in archival memory with tags
5. Updates memory blocks if needed
6. Updates conversation summary

### Cross-Agent Sharing

1. Multiple agents use same Letta server
2. Shared memory blocks can be attached to multiple agents
3. Archival memory searchable across all agents
4. Common "team_context" block for shared knowledge

## Deployment Files

| File | Purpose |
|------|---------|
| `docs/letta-deployment-guide.md` | Complete deployment instructions |
| `packages/letta_integration/autonomous_memory.py` | Core memory manager |
| `skills/autonomous_memory/SKILL.md` | Skill documentation |
| `workflows/memory-assisted-coding.md` | Coding workflow with memory |
| `scripts/cleanup_orphans.sh` | Cleanup duplicate files |

## Environment Variables

```bash
# Required
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_PG_URI="postgresql://letta:password@localhost:5432/letta"

# Optional
export LETTA_BASE_AGENT_ID="agent-abc123"
export LETTA_AUTO_MEMORY="true"
export LETTA_MEMORY_TAGS="autonomous,coding"
```

## Security Considerations

1. **Database Credentials**: Store in `~/.env.ai`, never commit
2. **Network**: Restrict PostgreSQL to localhost/Docker network
3. **API Keys**: Rotate regularly
4. **Encryption**: Use SSL for production DB connections
5. **Backups**: Automated via `backup.sh` script

## Performance

- **PostgreSQL**: Tune `shared_buffers`, `work_mem` for your RAM
- **pgvector**: IVFFlat index on embedding columns
- **Letta**: Use connection pooling for high concurrency

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Memory not initializing | Check `curl http://localhost:8283/v1/health` |
| No memories retrieved | Verify `pgvector` extension installed |
| Search returns empty | Check archival_memory has embeddings |
| Blocks not persisting | Verify PostgreSQL connection string |

## Next Steps

1. Run cleanup script: `./scripts/cleanup_orphans.sh`
2. Deploy Letta server per `docs/letta-deployment-guide.md`
3. Configure `~/.env.ai` with your database credentials
4. Restart terminal sessions to auto-load memory
5. Test with: `python3 -c "from letta_integration.autonomous_memory import get_memory; print(get_memory())"`

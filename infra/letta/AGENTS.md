# Letta Infrastructure - CBW Server
# Location: ~/infra/letta/
# All Letta server setup, configuration, scripts, and documentation.

## Quick Reference

```bash
# Server health
~/bin/letta health

# List agents
~/bin/letta agents

# Search memory
~/bin/letta archival-search <agent-id> "query"

# Store memory
~/bin/letta archival-insert <agent-id> "text" "tag1,tag2"

# Create agent
~/bin/letta create "name" "persona" "human" "model"
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   CBW Server                     │
│                Dell R720, 128GB RAM              │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │   Ollama     │  │  PostgreSQL  │             │
│  │  :11434      │  │  :5432       │             │
│  │  embeddings  │  │  letta,      │             │
│  │  nomic-embed │  │  cbw_rag     │             │
│  └──────────────┘  └──────────────┘             │
│         ▲                 ▲                      │
│         │                 │                      │
│  ┌──────┴─────────────────┴──────────┐          │
│  │       Letta Server (Docker)       │          │
│  │       Port 8283, v0.16.6          │          │
│  │       Container: letta-server     │          │
│  │                                   │          │
│  │  Core Memory    Archival Memory   │          │
│  │  (persona,      (searchable      │          │
│  │   human)        long-term)       │          │
│  └───────────────────────────────────┘          │
│                     ▲                            │
│                     │                            │
│  ┌──────────────────┴────────────────┐          │
│  │         AI Agents                  │          │
│  │  kilocode, opencode, claude,      │          │
│  │  cline, gemini, vscode,          │          │
│  │  windsurf, openclaw              │          │
│  └───────────────────────────────────┘          │
└─────────────────────────────────────────────────┘
```

## Directory Structure

```
~/infra/letta/
├── AGENTS.md              # This file - AI agent instructions
├── SETUP.md               # Complete setup/rebuild guide
├── TROUBLESHOOTING.md     # Common issues and fixes
├── docker-compose.letta.yml
├── .env.letta
├── deploy_letta.sh
├── data/                  # Letta data mount (Docker)
└── scripts/               # Essential scripts
    ├── letta-backup.sh
    ├── letta-restore.sh
    └── letta-memory-export.sh
```

## Configuration Paths

| File | Purpose |
|------|---------|
| `~/infra/letta/docker-compose.letta.yml` | Docker Compose config |
| `~/infra/letta/.env.letta` | Environment variables |
| `~/infra/letta/deploy_letta.sh` | Deployment script |
| `~/bin/letta` | CLI wrapper (→ ~/letta-cli/index.mjs) |
| `~/letta-cli/index.mjs` | Letta CLI implementation (Node.js SDK) |
| `~/.bash_secrets` | API keys and secrets (source before use) |

## Skill Integration

Skills that leverage Letta (in `~/dotfiles/ai/shared/skills/`):

| Skill | Path | Purpose |
|-------|------|---------|
| `letta_server` | `letta_server/SKILL.md` | Server management, health, agent setup |
| `letta_memory` | `letta_memory/SKILL.md` | Unified memory operations |
| `letta_workflows` | `letta_workflows/SKILL.md` | Stateful workflow automation |
| `cross_agent_coordinator` | `cross_agent_coordinator/SKILL.md` | Multi-agent coordination |
| `knowledge_base` | `knowledge_base/SKILL.md` | Structured knowledge capture |
| `memory_sync` | `memory_sync/SKILL.md` | PostgreSQL <-> Letta sync |
| `conversation_logging` | `conversation_logging/SKILL.md` | Auto conversation logging |
| `cli_operations` | `cli_operations/SKILL.md` | CLI wrappers |

## Workflows (in `~/dotfiles/ai/shared/workflows/`)

| Workflow | Purpose |
|----------|---------|
| `memory-first-task.md` | Universal: search before task, store after |
| `cross-agent-decision.md` | Record decisions for all agents |
| `knowledge-capture.md` | Convert work into searchable knowledge |
| `skill-sync.md` | Sync skill registries |
| `server-health-check.md` | Comprehensive health check |

## Database

- **PostgreSQL**: localhost:5432, user: cbwinslow
- **Letta DB**: `letta` (pgvector + pg_trgm enabled)
- **RAG DB**: `cbw_rag` (separate from Letta)

## Session History

### 2026-04-02: Full AI Agent Infrastructure Setup

**What the user asked for:**
1. Find skills in ~/dotfiles and make them available to KiloCode
2. Set up Letta memory so all AI agents can use it
3. Create skills, workflows, and commands for Letta integration
4. Respect the existing filesystem structure — no duplication
5. Document everything so the server can be rebuilt from scratch
6. Every AI agent must search memory before tasks and store results after

**What was done:**
- Fixed Letta database: created `letta` database with pgvector + pg_trgm extensions
- Created kilocode Letta agent (`agent-e5e8aab5-9e87-45c1-8025-700503b524c6`)
- Set up 3 core memory blocks: skills-config, server-info, environment
- Stored 10+ archival memories covering all configuration
- Created `~/dotfiles/ai/shared/workflows/` (NEW directory, 5 workflows)
- Created `~/dotfiles/ai/shared/commands/` (NEW directory, 2 commands)
- Created 4 new skills: letta_memory, letta_workflows, cross_agent_coordinator, knowledge_base
- Added 16 slash commands to `~/.config/kilo/command/`
- Updated registries: `registry.json` (17 skills), `registry.yaml`
- Updated `skills.paths` in `kilo.jsonc` to discover all skill locations
- Created symlinks in `~/.config/kilo/skills/` for all skills
- Created this documentation in `~/infra/letta/`

**Key files modified:**
- `~/.config/kilo/kilo.jsonc` — added skills.paths
- `~/.config/kilo/command/` — 16 slash command .md files
- `~/.config/kilo/skills/` — 16 skill symlinks
- `~/dotfiles/ai/shared/skills/` — 4 new skill directories
- `~/dotfiles/ai/shared/workflows/` — 5 workflow files
- `~/dotfiles/ai/shared/commands/` — 2 command files
- `~/dotfiles/ai/skills/registry.json` — updated with 4 new entries
- `~/dotfiles/ai/shared/skills/registry.yaml` — added letta category
- `~/AGENTS.md` — full inventory

## Disaster Recovery

If the server crashes, follow `SETUP.md` step by step. Key things to restore:
1. PostgreSQL databases: `letta` and `cbw_rag`
2. Docker container: `letta-server`
3. Skills in `~/dotfiles/` (restore from git)
4. CLI at `~/letta-cli/` and wrapper at `~/bin/letta`
5. Letta agent and memories (re-create or restore from backup)
6. KiloCode config in `~/.config/kilo/`

Run `~/infra/letta/scripts/letta-backup.sh` regularly to create backups.

## Backup

```bash
# Full backup
~/infra/letta/scripts/letta-backup.sh

# Export memories
~/infra/letta/scripts/letta-memory-export.sh

# PostgreSQL dump
pg_dump -h localhost -U cbwinslow letta > ~/infra/letta/data/letta_db_$(date +%Y%m%d).sql
```

See `SETUP.md` for full restore procedures.

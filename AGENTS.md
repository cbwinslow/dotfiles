# CBW Server Agent Configuration

## Available Skills

### cbw-rag
Search and retrieve files from the CBW RAG vector database. All server files are indexed with embeddings for semantic search.

- Search: `rag-search "query"` (vector), `rag-search "query" --text-only` (keyword), `rag-search "query" --hybrid` (combined)
- Index: `rag-index /path/to/dir --resume --verbose`
- Stats: `rag-search --stats`

### Database
- PostgreSQL 16 + pgvector 0.8 on localhost:5432
- Database: `cbw_rag` (user: cbwinslow)
- Embedding model: nomic-embed-text (768d) via Ollama at localhost:11434

### dotfiles-manager
Manage and organize `~/dotfiles`. Knows the full directory structure and where every file type belongs. Use this to create, move, edit, or audit dotfiles, configs, scripts, skills, MCP servers, and agent definitions.

- Agent definition: `~/.kilo/agent/dotfiles-manager.md`
- Filing rules table for: agents, skills, tools, MCP servers, scripts, shell aliases, configs
- CRITICAL: Never creates duplicate directories. Always reuses existing structure.
- Manages the 8-agent ecosystem (opencode, gemini, claude, cline, kilocode, vscode, windsurf, openclaw)

## Letta Memory System

Self-hosted Letta server (v0.16.6) for persistent, searchable memory across all AI agents.

- **Server**: Docker container `letta-server` at localhost:8283
- **CLI**: `~/bin/letta` (aliases: `lh`, `la`, `lcreate`, `lsend`, `lmem`, `larchi`, `larchs`)
- **Agent ID**: `agent-e5e8aab5-9e87-45c1-8025-700503b524c6` (kilocode)
- **Database**: PostgreSQL `letta` with pgvector + pg_trgm
- **Docs**: `~/infra/letta/` (AGENTS.md, SETUP.md, TROUBLESHOOTING.md)

**Key commands** (always `source ~/.bash_secrets` first):
```bash
~/bin/letta health                          # Check server
~/bin/letta agents                          # List agents
~/bin/letta archival-search <id> "query"    # Search memories
~/bin/letta archival-insert <id> "text" "tags"  # Store memory
~/bin/letta memory <id>                     # View core blocks
~/bin/letta block list                      # List all blocks
```

**Universal pattern**: Before ANY task, search memory. After ANY task, store results.

## Slash Commands

All available via `~/.config/kilo/command/` (global):

| Command | Description |
|---------|-------------|
| `/docker-ops` | Docker compose, containers, images, networks |
| `/github` | GitHub issues, PRs, CI via gh CLI |
| `/imagegen` | AI image generation and editing |
| `/skill-creator` | Create or update AI agent skills |
| `/skill-installer` | Install skills from GitHub repos |
| `/plugin-creator` | Create and scaffold plugins |
| `/bitwarden` | Retrieve secrets from Bitwarden vault |
| `/memory-sync` | Sync PostgreSQL <-> Letta memories |
| `/letta-server` | Letta server and agent management |
| `/letta-memory` | Search and manage Letta memory |
| `/letta-workflow` | Start, resume, or manage workflows |
| `/knowledge-base` | Store or search structured knowledge |
| `/agent-coordinator` | Coordinate tasks across agents |
| `/server-health` | Run comprehensive health check |
| `/conversation-log` | Log conversations to Letta memory |
| `/cli-operations` | CLI wrappers for Letta operations |
| `/rag-search` | Search CBW RAG vector database |
| `/rag-index` | Index files into CBW RAG database |

## Skill Discovery

Skills are loaded from these paths (configured in `kilo.jsonc` via `skills.paths`):

1. `~/dotfiles/ai/skills/` — Primary skills (docker-ops, .system skills)
2. `~/dotfiles/ai/shared/skills/` — Shared skills (letta_memory, letta_workflows, cross_agent_coordinator, knowledge_base, cbw_rag, bitwarden, letta_server, memory_sync, conversation_logging, cli_operations)
3. `~/dotfiles/skills/` — Additional skills (github)

Skill registry: `~/dotfiles/ai/skills/registry.json`

## Workflows

All AI agents should follow these shared workflows (in `~/dotfiles/ai/shared/workflows/`):

| Workflow | Rule |
|----------|------|
| `memory-first-task` | ALWAYS search Letta before tasks, store after |
| `cross-agent-decision` | Record important decisions for all agents |
| `knowledge-capture` | Convert work into searchable knowledge |
| `skill-sync` | Keep skill registries in sync |
| `server-health-check` | Comprehensive server health monitoring |

## Environment
- Server: Dell R720, 128GB RAM
- OS: Ubuntu 24.04
- Secrets: `~/.bash_secrets` (source before running tools)
- Dotfiles: `~/dotfiles/` (AI agent system, shell, git, ssh, editor, docs, letta)
- Infrastructure: `~/infra/` (docker, letta, monitoring, ansible, k8s, terraform)

# Shared AI Resources
# This is the central hub for ALL AI agents on the CBW server.
# Every agent reads from here. Changes here affect everyone.

## Purpose

This directory (`~/dotfiles/ai/shared/`) contains resources shared across the entire AI agent ecosystem: kilocode, opencode, claude, cline, gemini, vscode, windsurf, openclaw.

**Single source of truth.** No duplicating files into agent-specific directories.

## Directory Layout

```
~/dotfiles/ai/shared/
├── skills/          # Shared SKILL.md definitions (11 skills)
├── workflows/       # Shared workflow patterns (5 workflows)
├── commands/        # Shared command definitions (2 commands)
├── scripts/         # Utility scripts (auto_load_skills.sh, letta CLI, etc.)
├── tools/           # Shared tool definitions
├── mcp/             # MCP server implementations (RAG)
├── agents.md        # THIS FILE
└── CORE_MANDATES.md # Core agent rules
```

## What Goes Where

| Type | Location | Example |
|------|----------|---------|
| New skill | `skills/<name>/SKILL.md` | `skills/my_new_skill/SKILL.md` |
| New workflow | `workflows/<name>.md` | `workflows/deploy-app.md` |
| New command | `commands/<name>.md` | `commands/backup-db.md` |
| Utility script | `scripts/<name>.sh` | `scripts/monitor.sh` |
| MCP server | `mcp/<name>.py` | `mcp/my_server.py` |
| Tool definition | `tools/<category>/` | `tools/cli_tools/` |

## Important Rules

1. **Every directory must have an `agents.md`** — this is how AI agents understand what's in a folder
2. **Skills must have `SKILL.md` with YAML frontmatter** — `name` and `description` fields required
3. **Workflows must have YAML frontmatter** — `name`, `description`, `triggers`, `agents` fields
4. **Commands must have YAML frontmatter** — `name`, `description` fields
5. **Update registries** when adding skills — `~/dotfiles/ai/skills/registry.json` and `skills/registry.yaml`
6. **Create symlinks** in `~/.config/kilo/skills/` for KiloCode to discover new skills

## How KiloCode Discovers This

KiloCode's `kilo.jsonc` has `skills.paths` pointing here:
```json
"skills": {
  "paths": [
    "~/dotfiles/ai/skills",
    "~/dotfiles/ai/shared/skills",
    "~/dotfiles/skills"
  ]
}
```

Slash commands go in `~/.config/kilo/command/*.md` (global) or `.kilo/command/*.md` (project).

## Dependencies

- **Letta Server**: Docker `letta-server` at localhost:8283 — memory for all agents
- **PostgreSQL**: localhost:5432 — databases: `letta`, `cbw_rag`
- **Ollama**: localhost:11434 — embeddings (nomic-embed-text)
- **Secrets**: `source ~/.bash_secrets` before running anything

## Session History

### 2026-04-02: Full AI Infrastructure Setup
- Created `workflows/` directory with 5 Letta-integrated workflows
- Created `commands/` directory with 2 shared commands
- Added 4 new skills: `letta_memory`, `letta_workflows`, `cross_agent_coordinator`, `knowledge_base`
- Fixed Letta database (created `letta` DB with pgvector + pg_trgm)
- Created kilocode Letta agent (`agent-e5e8aab5-9e87-45c1-8025-700503b524c6`)
- Set up 3 core memory blocks and 10+ archival memories
- Full documentation in `~/infra/letta/`

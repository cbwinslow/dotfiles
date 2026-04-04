# Shared Skills Directory
# 11 skills available to ALL AI agents on the CBW server.
# Each skill is a directory with a SKILL.md file.

## Available Skills

| Skill | Category | Description |
|-------|----------|-------------|
| `letta_memory` | memory | Unified Letta memory — search, store, blocks, cross-agent |
| `letta_workflows` | automation | Stateful workflow automation backed by Letta |
| `letta_server` | memory | Letta server health, agent setup, server management |
| `cross_agent_coordinator` | coordination | Multi-agent coordination via shared Letta memory |
| `knowledge_base` | knowledge | Structured knowledge capture — decisions, runbooks, ADRs |
| `cbw_rag` | search | RAG semantic search, file dedup, code similarity |
| `bitwarden` | security | Bitwarden vault secret management |
| `memory_sync` | memory | PostgreSQL <-> Letta synchronization |
| `conversation_logging` | memory | Auto conversation logging with entity extraction |
| `cli_operations` | tools | CLI wrappers for Letta and PostgreSQL |
| `gdrive-download` | tools | Download files from Google Drive |

## How Skills Work

Each skill directory contains:
- `SKILL.md` — Skill definition with YAML frontmatter (`name`, `description`, `version`, `category`)
- Optional: implementation files (.py, .sh), config, data

KiloCode loads skills via the `skill` tool:
```
Use the `skill` tool with `name: "letta_memory"` to load full instructions
```

## Adding a New Skill

1. Create directory: `mkdir skills/my_skill/`
2. Create SKILL.md with frontmatter:
   ```markdown
   ---
   name: my_skill
   description: "What this skill does"
   version: 1.0.0
   category: general
   ---
   # My Skill
   ...
   ```
3. Add `agents.md` to the directory
4. Update `~/dotfiles/ai/skills/registry.json` — add entry to `skills` array
5. Update `registry.yaml` in this directory
6. Create symlink: `ln -s ~/dotfiles/ai/shared/skills/my_skill ~/.config/kilo/skills/my_skill`
7. Create slash command (optional): `~/.config/kilo/command/my-skill.md`

## Registry Files

- `registry.yaml` — Categorized skill definitions (core, code, data, research, writing, system, letta)
- `unified_loader.py` — Python skill discovery and loading

## Critical Requirement

**Every AI agent must search Letta memory BEFORE starting any task and store results AFTER completing it.** This is the universal pattern defined in `../workflows/memory-first-task.md`.

## Session History

### 2026-04-02: Added Letta Integration Skills
- `letta_memory` — unified memory operations (before/after task, search, store, blocks)
- `letta_workflows` — stateful workflow automation (start, resume, track, handoff)
- `cross_agent_coordinator` — multi-agent coordination (post findings, request help, share config)
- `knowledge_base` — structured knowledge (decisions, runbooks, ADRs, debugging)
- Updated `registry.yaml` with `letta` category section
- Updated `~/dotfiles/ai/skills/registry.json` with 4 new entries

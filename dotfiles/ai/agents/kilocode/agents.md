# KiloCode Agent Configuration
# This is the agent definition for KiloCode within the CBW AI agent ecosystem.

## What This Directory Contains

- `config.yaml` — Agent configuration (skills, tools, framework, security)
- `agents.md` — THIS FILE
- `prompts/` — Agent-specific prompts (placeholder)
- `skills/` — Agent-specific skills (placeholder — uses shared skills)
- `tools/` — Agent-specific tools (placeholder — uses shared tools)

## Agent Identity

- **Name**: kilocode_agent
- **Framework**: crewai
- **Shared resources**: `~/dotfiles/ai/shared/` (skills, tools, scripts, MCP, docs)

## How KiloCode Actually Works

KiloCode's real configuration is in:
- `~/.config/kilo/kilo.jsonc` — Global config (permissions, model, skills.paths)
- `~/.kilo/` — Project-level config (agents, commands, plans)
- `~/.kilocode/config.json` — Provider config (openrouter, gemini models)

The `config.yaml` in this directory defines the dotfiles-level agent spec, but KiloCode reads from `~/.config/kilo/` and `.kilo/`.

## Skills Available to KiloCode

KiloCode discovers skills from 3 locations via `skills.paths` in `kilo.jsonc`:
1. `~/dotfiles/ai/skills/` — docker-ops, .system skills
2. `~/dotfiles/ai/shared/skills/` — 11 shared skills (letta_memory, cbw_rag, etc.)
3. `~/dotfiles/skills/` — github

Symlinks in `~/.config/kilo/skills/` point to all available skills.

## Slash Commands (16 total)

Global commands in `~/.config/kilo/command/`:
`/docker-ops`, `/github`, `/imagegen`, `/skill-creator`, `/skill-installer`, `/plugin-creator`, `/bitwarden`, `/memory-sync`, `/letta-server`, `/letta-memory`, `/letta-workflow`, `/knowledge-base`, `/agent-coordinator`, `/server-health`, `/conversation-log`, `/cli-operations`

Project commands in `.kilo/command/`:
`/rag-search`, `/rag-index`

## Letta Integration

KiloCode agent uses Letta for persistent memory:
- **Server**: localhost:8283 (Docker `letta-server`)
- **Agent ID**: `agent-e5e8aab5-9e87-45c1-8025-700503b524c6`
- **CLI**: `~/bin/letta`
- **Pattern**: Before every task → search memory. After every task → store results.

## Critical Requirements from User

1. **Memory-first pattern**: ALL agents must search Letta before tasks, store after
2. **No filesystem duplication**: Use symlinks, don't copy files
3. **Respect existing structure**: Work within the established directory layout
4. **Documentation**: Every directory needs an agents.md
5. **Registries**: Keep registry.json and registry.yaml updated
6. **Disaster recovery**: Everything must be rebuildable from docs in `~/infra/letta/`

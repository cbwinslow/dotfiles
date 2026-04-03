# Centralized AI Agent Architecture
# ~/dotfiles/ai/ARCHITECTURE.md

## Overview

This architecture provides a **single source of truth** for all 10 AI agents:
- claude, cline, codex, gemini, kilocode, openclaw, opencode, qwen, vscode, windsurf

## Core Principle: Share Everything Possible

Instead of each agent having its own copy of skills, tools, and scripts, all agents reference the centralized shared resources.

## Directory Structure

```
~/dotfiles/ai/
├── ARCHITECTURE.md           # This file
├── AGENT_STATUS.md           # Status of all agents
├── registry.yaml             # Master registry of all resources
├── QUICKSTART.md            # Quick start guide
│
├── shared/                   # ★ CENTRALIZED RESOURCES ★
│   ├── CORE_MANDATES.md     # Core operating principles
│   ├── skills/              # All skills (moved from ai/skills/)
│   │   ├── cbw_rag/        # RAG semantic search
│   │   ├── memory/         # Memory management
│   │   ├── bitwarden/      # Secret management
│   │   └── ...
│   ├── tools/               # All tools (moved from ai/tools/)
│   │   ├── api_tools/
│   │   ├── cli_tools/
│   │   └── ...
│   ├── scripts/             # All shared scripts
│   │   ├── rag_cli.sh      # NEW: RAG search/index commands
│   │   ├── github_backup.py
│   │   └── ...
│   ├── configs/             # Shared configuration
│   │   ├── memory_types.yaml
│   │   └── agent_defaults.yaml
│   ├── mcp/                 # MCP servers
│   │   ├── rag_server.py
│   │   └── rag_system.py
│   └── docs/                # Shared documentation
│
├── agents/                  # Agent-specific files ONLY
│   ├── claude/             # Just config.yaml + overrides
│   │   └── config.yaml     # References shared resources
│   ├── cline/
│   ├── codex/
│   ├── gemini/
│   ├── kilocode/
│   ├── openclaw/
│   ├── opencode/
│   ├── qwen/
│   ├── vscode/
│   └── windsurf/
│
├── frameworks/              # AI frameworks (crewai, autogen, etc.)
├── packages/                # External packages/integrations
├── base/                    # Base configurations
├── global_rules/            # Global agent rules
├── docs/                    # General documentation
├── logs/                    # Centralized logging
└── services/                # Service definitions
```

## Migration Strategy

### Phase 1: Create Central Shared Structure (COMPLETED)
- ✅ Created `~/dotfiles/ai/shared/scripts/rag_cli.sh` - RAG CLI commands
- ✅ CBW RAG MCP server at `~/dotfiles/ai/shared/mcp/`
- ✅ Registry at `~/dotfiles/ai/skills/registry.yaml`

### Phase 2: Move Skills to Central Location (PENDING)
```bash
# Move skills from ai/skills/ to ai/shared/skills/
mv ~/dotfiles/ai/skills/* ~/dotfiles/ai/shared/skills/
```

### Phase 3: Move Tools to Central Location (PENDING)
```bash
# Move tools from ai/tools/ to ai/shared/tools/
mv ~/dotfiles/ai/tools/* ~/dotfiles/ai/shared/tools/
```

### Phase 4: Move Scripts to Central Location (PENDING)
```bash
# Move scripts from ai/scripts/ to ai/shared/scripts/
mv ~/dotfiles/ai/scripts/*.py ~/dotfiles/ai/shared/scripts/
mv ~/dotfiles/ai/scripts/*.sh ~/dotfiles/ai/shared/scripts/
```

### Phase 5: Update Agent Configs (PENDING)
Update each agent's config.yaml to reference shared resources:
```yaml
# Example agent config referencing shared resources
shared_resources:
  skills_path: ~/dotfiles/ai/shared/skills
  tools_path: ~/dotfiles/ai/shared/tools
  scripts_path: ~/dotfiles/ai/shared/scripts
  mcp_servers: ~/dotfiles/ai/shared/mcp
```

## CBW RAG System

### Status: ✅ OPERATIONAL
- **Database**: PostgreSQL 16 + pgvector 0.8 on localhost:5432
- **Database**: cbw_rag
- **Embedding Model**: nomic-embed-text (768 dimensions)
- **Note**: qwen3-embedding (4096 dimensions) incompatible with pgvector index limits

### Commands Available
```bash
# Index files for semantic search
rag-index ~/dotfiles

# Search across indexed content
rag-search "authentication middleware"

# Show RAG statistics
rag-stats

# Find duplicate files
rag-duplicates
```

### MCP Server
Location: `~/dotfiles/ai/shared/mcp/rag_server.py`
Connects to: `/home/cbwinslow/projects/ai/rag_system/mcp_server.py`

## Agent Configuration Template

Each agent should use this minimal config structure:

```yaml
# ~/dotfiles/ai/agents/{agent_name}/config.yaml
agent:
  name: {agent_name}
  version: "1.0.0"
  
shared:
  # All agents reference same shared resources
  skills: ~/dotfiles/ai/shared/skills
  tools: ~/dotfiles/ai/shared/tools
  scripts: ~/dotfiles/ai/shared/scripts
  mcp_servers: ~/dotfiles/ai/shared/mcp
  
agent_specific:
  # Only put agent-specific overrides here
  custom_prompts: ./prompts/
  custom_tools: ./tools/  # Empty if using shared
  
mcp_servers:
  cbw-rag:
    command: python3 ~/dotfiles/ai/shared/mcp/rag_server.py
    env:
      CBW_RAG_DATABASE: postgresql://localhost:5432/cbw_rag
```

## Benefits of This Architecture

1. **Single Source of Truth**: One working copy of skills, tools, scripts
2. **Consistency**: All agents use the same version of resources
3. **Maintainability**: Update once, all agents benefit
4. **Storage Efficiency**: No duplicate files
5. **Easy Onboarding**: New agents reference existing shared resources
6. **Version Control**: Track changes in one place

## Implementation Checklist

- [x] CBW RAG system operational with pgvector
- [x] rag-search and rag-index CLI commands created
- [x] MCP server in shared location
- [ ] Move skills to shared/skills/
- [ ] Move tools to shared/tools/
- [ ] Move scripts to shared/scripts/
- [ ] Update all 10 agent configs to reference shared resources
- [ ] Create symlinks from old locations to new (for backwards compatibility)
- [ ] Document the architecture in agent onboarding

# AI Agent Skills System - Project Overview

## Overview

Centralized AI agent management with:
- **OpenRouter Free Models** - All agents use `openrouter/free` by default
- **Letta Server Integration** - Automatic conversation saving and memory management
- **Layered Configuration** - Base config inherited by all agents
- **Shared Skills & Tools** - Centralized registry used by all agents

## Directory Structure

```
~/dotfiles/ai/
├── base/                    # Base configurations (single source of truth)
│   ├── base_agent.yaml      # Inherited by all agents
│   ├── providers.yaml       # Provider configs (OpenRouter free models)
│   └── memory.yaml          # Letta memory configuration
├── agents/                  # Agent-specific configs (overrides only)
│   ├── opencode/
│   ├── cline/
│   ├── gemini/
│   ├── claude/
│   └── ...
├── skills/                  # Shared skills
│   ├── registry.yaml        # Skill catalog
│   └── letta_server/
├── tools/                   # Shared tools
│   ├── registry.yaml        # Tool catalog
│   └── ...
├── global_rules/            # Mandatory rules for all agents
│   ├── agent_init_rules.md
│   └── letta_integration_rules.md
├── packages/                # Installable packages
│   └── letta_integration/   # Letta Python package
└── scripts/                 # Utility scripts
    ├── setup_complete_system.sh
    ├── create_symlinks.sh
    ├── validate_configs.py
    └── shell_integration.sh
```

## Quick Setup

```bash
# 1. Run alias ai-init='bash ~/dotfiles/ai/scripts/setup_complete_system.sh'

# 2. Update environment variables
# Edit ~/dotfiles/ai/.env with your API keys

# 3. Restart shell
source ~/.zshrc

# 4. Verify setup
ai-health
```

## Environment Variables

Create/edit `~/dotfiles/ai/.env`:

```bash
# Letta Server
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_API_KEY="your-letta-api-key"

# OpenRouter (free models)
export OPENROUTER_API_KEY="your-openrouter-api-key"

# PostgreSQL (backup)
export PG_HOST="localhost"
export PG_PORT="5432"
export PG_DATABASE="letta"
export PG_USER="cbwinslow"
export PG_PASSWORD="your-password"
```

## Usage

### Agent Commands

```bash
# Start agents (they auto-load centralized configs)
opencode
cline
kilocode

# All agents automatically:
# - Use OpenRouter free models
# - Save conversations to Letta
# - Extract entities
# - Create memories
```

### Letta Memory Commands

```bash
# Check health
letta-health

# Get statistics
letta-stats

# Search memories
letta-search --query "entity extraction"

# Save conversation
letta-save --type conversation --content "..."

# Backup memories
letta-backup

# List agents
letta-list agents

# List memories
letta-list memories --limit 50
```

### Management Commands

```bash
# Validate all configs
ai-validate

# Create symlinks
ai-symlinks

# Full health check
ai-health

# Show all commands
ai-help
```

### Navigation

```bash
ai-cd        # Go to AI root
ai-agents    # Go to agents directory
ai-skills    # Go to skills directory
ai-tools     # Go to tools directory
```

## Configuration

### Base Config (`base/base_agent.yaml`)

All agents inherit from this. Key settings:

```yaml
provider: openrouter
model: openrouter/free
memory_backend: letta_server

letta:
  auto_save_conversations: true
  auto_create_memories: true
  memory_types:
    - core
    - archival
    - context
    - persona
    - human
```

### Agent Config (`agents/<agent>/config.yaml`)

Only agent-specific overrides:

```yaml
extends: ../../base/base_agent.yaml

name: opencode_agent
framework: langchain

# Only unique settings
tools:
  - file_system
  - git
  - terminal
```

## Letta Integration

### Automatic Memory Operations

Every agent automatically:

1. **Saves conversations** - Full logs to archival memory
2. **Extracts entities** - Code, files, URLs, commands
3. **Creates decision memories** - Important choices
4. **Creates action items** - Tasks identified
5. **Searches before acting** - Prior context first

### Memory Types

| Type | Purpose | TTL |
|------|---------|-----|
| `core` | Permanent knowledge | Never |
| `archival` | Conversations, context | 365 days |
| `context` | Session working memory | 30 days |
| `persona` | Agent personality | Never |
| `human` | User preferences | Never |

### Python API

```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="my_agent")

# Save conversation
letta.save_conversation(messages, tags=["task"])

# Search memories
results = letta.search_memories("prior work")

# Extract entities
letta.extract_and_store_entities(code_text)

# Check health
health = letta.check_server_health()
```

## Validation

```bash
# Validate all configurations
python3 scripts/validate_configs.py --verbose

# Checks:
# - Base config exists and is valid
# - All agent configs extend base
# - Provider is openrouter
# - Model is openrouter/free
# - Letta tools are configured
# - Skills registry is valid
# - Tools registry is valid
# - Environment variables are set
```

## Troubleshooting

### Letta Server Not Accessible

```bash
# Start Letta server
letta server

# Or check Docker
docker ps | grep letta
```

### Config Validation Fails

```bash
# Run validation with details
ai-validate --verbose

# Fix reported issues
```

### Symlinks Broken

```bash
# Recreate symlinks
ai-symlinks
```

## Files Reference

| File | Purpose |
|------|---------|
| `base/base_agent.yaml` | Base config for all agents |
| `base/providers.yaml` | Provider configurations |
| `base/memory.yaml` | Letta memory settings |
| `skills/registry.yaml` | Skill catalog |
| `tools/registry.yaml` | Tool catalog |
| `global_rules/agent_init_rules.md` | Universal agent rules |
| `global_rules/letta_integration_rules.md` | Letta integration rules |
| `packages/letta_integration/` | Letta Python package |
| `scripts/setup_complete_system.sh` | Complete setup |
| `scripts/create_symlinks.sh` | Create symlinks |
| `scripts/validate_configs.py` | Validate configs |
| `scripts/shell_integration.sh` | Shell aliases |

## Next Steps

1. **Start Letta Server**: `letta server` or Docker
2. **Set API Keys**: Edit `~/dotfiles/ai/.env`
3. **Test Setup**: Run `ai-health`
4. **Start Using**: Run any agent (`opencode`, `cline`, etc.)

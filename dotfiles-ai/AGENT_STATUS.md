# AI Agents Installation Status

**Last Updated**: 2026-03-24
**Status**: ✅ All Agents Working

## Installed Agents

| Agent | Version | Status | Config Location |
|-------|---------|--------|-----------------|
| **Cline** | 2.9.0 | ✅ Working | `~/.cline` → `~/dotfiles/ai/.cline/data` |
| **OpenCode** | 1.3.0 | ✅ Working | `~/.opencode/` |
| **KiloCode** | 7.1.0 | ✅ Working | `~/.kilocode` → `~/dotfiles/ai/.kilocode/data` |
| **Gemini CLI** | 0.34.0 | ✅ Working | `~/.gemini` → `~/dotfiles/ai/.gemini/data` |
| **OpenClaw** | 2026.3.13 | ✅ Working | `~/.openclaw` → `~/dotfiles/ai/.openclaw/data` |

## Configuration

All agents now use:
- **Provider**: `openrouter`
- **Model**: `openrouter/free` (free model router)
- **Memory**: `letta_server` (self-hosted)
- **Config Source**: `~/dotfiles/ai/agents/<agent>/config.yaml`

## Data Directories

```
~/dotfiles/ai/
├── .cline/data/          # Cline data
├── .gemini/data/         # Gemini data
├── .openclaw/data/       # OpenClaw data
├── .kilocode/data/       # KiloCode data
└── .opencode/data/       # OpenCode data
```

## Symlinks

```bash
~/.cline     -> ~/dotfiles/ai/.cline/data
~/.gemini    -> ~/dotfiles/ai/.gemini/data
~/.openclaw  -> ~/dotfiles/ai/.openclaw/data
~/.kilocode  -> ~/dotfiles/ai/.kilocode/data
```

## Quick Test

```bash
# Test all agents
cline --version
opencode --version
kilocode --version
gemini --version
openclaw --version

# Or run test script
bash ~/dotfiles/ai/scripts/test_agents.sh
```

## Fix Script

If any agent has issues:

```bash
bash ~/dotfiles/ai/scripts/fix_agent_installs.sh
```

## Environment Setup

Required environment variables (set in `~/dotfiles/ai/.env`):

```bash
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_API_KEY="your-letta-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

Add to shell (`~/.zshrc` or `~/.bashrc`):

```bash
source ~/dotfiles/ai/scripts/shell_integration.sh
```

## Usage

```bash
# Start any agent
cline
opencode
kilocode
gemini
openclaw

# All agents will:
# - Use OpenRouter free models
# - Save conversations to Letta
# - Extract entities automatically
# - Create memories from decisions
```

## Troubleshooting

### Agent won't start

1. Check installation: `which <agent>`
2. Check version: `<agent> --version`
3. Re-run fix script: `bash ~/dotfiles/ai/scripts/fix_agent_installs.sh`

### Config not loading

1. Check symlink: `ls -la ~/.<agent>`
2. Verify config exists: `ls ~/dotfiles/ai/agents/<agent>/config.yaml`
3. Re-create symlinks: `bash ~/dotfiles/ai/scripts/create_symlinks.sh`

### Letta not saving

1. Check server: `letta-health`
2. Check API key: `echo $LETTA_API_KEY`
3. Start server: `letta server`

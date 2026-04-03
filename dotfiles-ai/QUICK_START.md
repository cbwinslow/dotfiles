# Agent AI Skills System - Quick Start Guide

## 🚀 Quick Start

### 1. Install Agent Memory Package
```bash
cd /home/cbwinslow/dotfiles/ai/packages/agent_memory
pip install -e .
```

### 2. Set Environment Variables
```bash
export PG_HOST=localhost
export PG_PORT=5432
export PG_DBNAME=letta
export PG_USER=cbwinslow
export PG_PASSWORD=123qweasd
export LETTA_SERVER_URL=http://localhost:8283
export LETTA_API_KEY=your-api-key
```

### 3. Initialize System
```bash
cd /home/cbwinslow/dotfiles/ai
python3 scripts/setup_complete_system.py
```

### 4. Initialize Individual Agents
```bash
# Initialize specific agent
python3 scripts/auto_init_agents.py --agent opencode

# Or initialize all agents
python3 scripts/auto_init_agents.py --all
```

### 5. Test the System
```bash
python3 scripts/validate_system.py --verbose
```

## 📋 Daily Usage

### Start Shell with AI Integration
```bash
# Restart shell to load aliases
source ~/.zshrc  # or ~/.bashrc

# Use agents with automatic rule loading
opencode "Write a Python script to analyze data"
gemini "Help me debug this code"
claude "Explain this algorithm"
```

### Memory Management
```bash
# Save conversation
agent-memory-cli store --type conversation --title "Meeting Notes" --content "Discussion about..."

# Search memories
agent-memory-cli search --query "entity extraction" --type "processing_status"

# View statistics
agent-memory-cli stats
```

### Agent Management
```bash
# Check agent status
python3 scripts/validate_system.py

# Initialize all agents
python3 scripts/auto_init_agents.py --all

# Create backup
python3 scripts/github_backup.py --create-backup
```

## 🔧 Configuration

### Agent-Specific Configuration
Edit agent configs in:
- `/home/cbwinslow/dotfiles/ai/agents/opencode/config.yaml`
- `/home/cbwinslow/dotfiles/ai/agents/gemini/config.yaml`
- `/home/cbwinslow/dotfiles/ai/agents/claude/config.yaml`

### Framework Configuration
Edit framework configs in:
- `/home/cbwinslow/dotfiles/ai/frameworks/langchain/config.yaml`
- `/home/cbwinslow/dotfiles/ai/frameworks/crewai/config.yaml`
- `/home/cbwinslow/dotfiles/ai/frameworks/autogen/config.yaml`

### Global Rules
Edit global rules in:
- `/home/cbwinslow/dotfiles/ai/global_rules/agent_init_rules.md`

## 🆘 Troubleshooting

### Common Issues

1. **Agent not loading rules**
   - Check shell aliases are loaded: `source ~/.zshrc`
   - Verify global rules path: `ls /home/cbwinslow/dotfiles/ai/global_rules/`

2. **Memory system not working**
   - Check PostgreSQL connection: `psql -h localhost -U cbwinslow letta`
   - Verify environment variables are set
   - Run: `agent-memory-cli init`

3. **Letta integration issues**
   - Check Letta server is running: `docker ps`
   - Verify API key is correct
   - Test connection: `curl http://localhost:8283/health`

### Getting Help
- Check logs in: `/home/cbwinslow/dotfiles/ai/logs/`
- Run validation: `python3 scripts/validate_system.py --verbose`
- View system config: `cat /home/cbwinslow/dotfiles/ai/system_config.json`

## 🔄 Updates and Maintenance

### Update System
```bash
# Pull latest changes
python3 scripts/github_backup.py --pull

# Re-run setup if needed
python3 scripts/setup_complete_system.py
```

### Create Backup
```bash
# Manual backup
python3 scripts/github_backup.py --create-backup

# Automated backup (via GitHub Actions)
# Runs daily at 2 AM UTC
```

### Add New Agent
1. Create agent directory: `/home/cbwinslow/dotfiles/ai/agents/newagent/`
2. Add config file: `config.yaml`
3. Run: `python3 scripts/auto_init_agents.py --agent newagent`

---

**Note**: This system is designed to be self-documenting. Check the README.md files in each directory for detailed information.

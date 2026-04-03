# AI Agent Management System

A sophisticated, centralized system for managing AI agents, skills, tools, and frameworks.

## Architecture Overview

```
dotfiles/ai/
├── agents/          # Individual agent configurations
├── skills/          # Skill categories and implementations
├── tools/           # Tool categories and implementations
├── frameworks/      # Framework integrations (LangChain, CrewAI, AutoGen)
├── configs/         # Shared configurations
├── scripts/         # Automation scripts
├── prompts/         # Agent prompt templates
├── base/           # Base configurations
└── letta/          # Letta memory system
```

## Key Features

### Centralized Configuration
- **Base Agent Config**: All agents inherit from `base/base_agent.yaml`
- **Skill Registry**: Centralized skill management in `skills/registry.yaml`
- **Tool Registry**: Centralized tool management in `tools/registry.yaml`

### Letta Memory Integration
- **Self-Hosted**: Local Letta server for persistent memory
- **Automatic Saving**: Conversations saved automatically
- **Cross-Agent Sharing**: Memories shared across all agents
- **Memory Types**: Core, archival, context, persona, human

### Bitwarden Integration
- **Secure Credentials**: Access to Bitwarden vault for API keys
- **Environment Management**: Automatic population of .env files
- **Vault Operations**: List, search, and validate credentials

### Agent Management
- **10+ Agents**: Cline, OpenCode, KiloCode, Gemini CLI, OpenClaw, VS Code, Windsurf, etc.
- **Skill-Based**: Each agent has core + specialized skills
- **Auto-Initialization**: Scripts for automatic setup

## Quick Start

### Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure Letta: Set `LETTA_SERVER_URL` and `LETTA_API_KEY`
3. Configure Bitwarden: Set `BITWARDEN_VAULT_PASSWORD`

### Usage
```bash
# Auto-load skills for all agents
./scripts/auto_load_skills.sh

# Create agent prompts
./scripts/agent_prompts.sh

# Start an agent
python -m agents.cline --config agents/cline/config.yaml
```

## Skills System

### Core Skills (Required for all agents)
- **Memory Management**: Letta operations (save, search, manage)
- **Entity Extraction**: Extract and store entities from conversations
- **Conversation Logging**: Automatic conversation logging
- **Cross-Agent Search**: Search memories across all agents
- **Server Health**: Monitor Letta server health
- **Bitwarden Integration**: Secure credential access

### Specialized Skills
- **Code Generation**: Multi-language code generation
- **Data Processing**: JSON, CSV, XML, YAML processing
- **Research**: Web search and content fetching
- **Writing**: Documentation, summarization, translation

## Tools System

### Available Tools
- **CLI Tools**: File system, terminal, git operations
- **API Tools**: Web requests, API integrations
- **Data Tools**: Data processing, OCR, format conversion
- **Utility Tools**: Process management, system operations

## Frameworks Integration

### Supported Frameworks
- **LangChain**: For building language model applications
- **CrewAI**: For multi-agent collaboration
- **AutoGen**: For conversation-based agent systems
- **Custom Frameworks**: Extensible framework support

## Security Features

### Access Control
- **Path Restrictions**: Limited file system access
- **Command Blocking**: Restricted dangerous commands
- **Credential Management**: Secure Bitwarden integration

### Privacy
- **Local Processing**: All data processed locally
- **Encrypted Storage**: Sensitive data encrypted at rest
- **Audit Logging**: All operations logged for review

## Monitoring & Maintenance

### Health Checks
- **Server Status**: Letta server health monitoring
- **Agent Status**: Individual agent health checks
- **Memory Usage**: Memory consumption tracking

### Backup & Recovery
- **Automated Backups**: Regular memory backups
- **Restore Procedures**: Documented recovery processes
- **Version Control**: Git-based configuration management

## Contributing

### Adding New Agents
1. Create agent directory in `agents/`
2. Create `config.yaml` extending base config
3. Add skills to `skills/registry.yaml`
4. Add tools to `tools/registry.yaml`

### Adding New Skills
1. Create skill directory in `skills/`
2. Update `skills/registry.yaml`
3. Add implementation files
4. Test with existing agents

## Support

### Documentation
- **API Reference**: Detailed API documentation
- **Troubleshooting Guide**: Common issues and solutions
- **Best Practices**: Recommended usage patterns

### Community
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share experiences and ask questions
- **Contributions**: Guidelines for contributing

---

**This system is designed for commercial-grade AI agent operations with enterprise-level security, scalability, and maintainability.**
# Universal Skills Registry

## All Available Skills for All AI Agents

This document defines all skills available to all AI agents (qwen, gemini, codex, openclaw, opencode, cline, kilocode, vscode, windsurf, etc.).

## Core Skills (Available to All Agents)

### 1. Debug & Analysis
- **debug** - Script debugging and issue detection
- **analyze** - Code structure and architecture analysis
- **visualize** - Architecture visualization and diagrams
- **python-refactor** - Python code refactoring
- **reuse** - Code reuse finder
- **tasks** - Task tracking and TODO management

### 2. Letta Memory System
- **letta_agents** - Agent lifecycle management
- **letta_memory** - Memory storage and retrieval
- **letta_blocks** - Reusable memory blocks
- **letta_backup** - Backup and maintenance
- **a0_memory** - Agent memory system
- **autonomous_memory** - Automated memory
- **unified_memory** - Unified memory interface

### 3. Operations & Infrastructure
- **docker-ops** - Docker operations
- **github** - GitHub integration
- **infrastructure** - Infrastructure management
- **system-maintenance** - System maintenance
- **shell** - Shell scripting
- **bitwarden** - Secure vault access with API key authentication (2FA bypass)
  - Location: `~/dotfiles/ai/skills/bitwarden/SKILL.md`
  - Features: API key auth, secure session management, 2FA bypass for automation
  - Security: Credentials in `.bw_credentials` (600 perms, gitignored)
  - Usage: `source ~/dotfiles/ai/skills/bitwarden_secrets/secure_session_loader.sh`
- **bitwarden_secrets** - Advanced API key management with secure Python interface

### 4. Development & Coding
- **coding** - Coding assistance
- **research** - Research assistance
- **knowledge** - Knowledge base
- **skills** - Skill management
- **conversation_logger** - Conversation tracking

### 5. Model & Framework
- **letta_model_picker** - Letta model selection
- **letta_integration** - Letta integration

## Skills by Agent Type

### Coding Agents (qwen, codex, vscode, windsurf, cline, kilocode)
Required skills:
- debug, analyze, visualize, python-refactor, coding
- letta_agents, letta_memory, letta_blocks
- docker-ops, github, shell
- reuse, tasks

### Operations Agents (gemini, ops-monitor)
Required skills:
- docker-ops, infrastructure, system-maintenance
- shell, bitwarden, bitwarden_secrets
- letta_agents, letta_backup
- github

### Research Agents (researcher)
Required skills:
- research, knowledge
- letta_memory, unified_memory
- github

### Multi-Purpose Agents (openclaw, opencode)
Required skills:
- ALL SKILLS (full access to everything)

## Skill Activation

### For CLI Agents (cline, kilocode, opencode)
```yaml
skills:
  - debug
  - analyze
  - visualize
  - letta_agents
  - letta_memory
  - letta_blocks
  - letta_backup
  - coding
  - docker-ops
  - github
  - shell
  - python-refactor
  - reuse
  - tasks
  - system-maintenance
```

### For IDE Agents (vscode, windsurf)
```yaml
skills:
  - debug
  - analyze
  - visualize
  - coding
  - python-refactor
  - letta_memory
  - letta_agents
  - github
  - reuse
```

### For Web Agents (qwen, gemini, codex, openclaw)
```yaml
skills:
  - ALL
```

## Cross-Agent Coordination

All agents should:
1. Check unified_memory for shared context
2. Use letta_memory for agent-specific knowledge
3. Share discoveries via letta_blocks
4. Coordinate through shared workflows

## Tool Access

All agents have access to:
- cbw-debug - Script debugging
- cbw-analyze - Code analysis
- cbw-visualize - Architecture visualization
- cbw-reuse - Code reuse finder
- cbw-tasks - Task tracking
- cbw-help - Knowledge base query
- letta-memory-cli - Letta memory operations
- cbw-letta - Letta automation wrapper

## Workflows Available

All agents can use:
- script-debugging - Debug scripts
- codebase-analysis - Analyze code
- refactoring-with-analysis - Refactor code
- agent-lifecycle - Manage agents
- memory-operations - Manage memories

## Usage Examples

### Any Agent Can:

```bash
# Debug a script
cbw-debug problematic.sh

# Analyze code
cbw-analyze --path ~/project

# Search knowledge base
cbw-help "how do I use docker compose"

# Save memory to Letta
letta-memory-cli memory save --agent my_agent --content "..."

# Find code reuse opportunities
cbw-reuse --report
```

### Agent Coordination:

```python
# Agent 1 saves discovery
letta.save_memory(content="Found bug in auth module", tags=["bug","auth"])

# Agent 2 searches for related info
results = letta.search_memories("auth module")

# Agent 3 uses shared block
block = letta.get_agent_block_by_label(agent_id, "shared_knowledge")
```

## Priority Skills by Use Case

### Code Review
1. debug - Check scripts
2. analyze - Understand structure
3. python-refactor - Suggest improvements
4. reuse - Find patterns

### System Operations
1. docker-ops - Container management
2. system-maintenance - Health checks
3. shell - Script execution
4. bitwarden - Secret access

### Knowledge Work
1. research - Information gathering
2. knowledge - Knowledge base
3. letta_memory - Store findings
4. unified_memory - Cross-agent sync

### Development
1. coding - Write code
2. github - Version control
3. debug - Fix issues
4. visualize - Document architecture

## Skill Discovery

Agents can discover available skills:
```bash
# List all skills
cbw-skills --list

# Get skill info
cbw-skills --info debug

# Check if skill available
cbw-skills --check letta_memory
```

## Skill Dependencies

Some skills depend on others:
- letta_memory → requires letta_agents
- letta_blocks → requires letta_agents
- letta_backup → requires letta_agents, letta_memory
- reuse → requires analyze
- visualize → requires analyze

## Installation

All skills installed at:
- ~/dotfiles/ai/skills/

All tools installed at:
- ~/dotfiles/ai/scripts/

All workflows at:
- ~/dotfiles/ai/workflows/

## Access Control

All agents have **FULL ACCESS** to:
- All skills
- All tools
- All workflows
- All documentation

No restrictions - collaboration enabled.

## Updates

When new skills are added:
1. Update this registry
2. Notify all agents
3. Update agent configs
4. Test cross-agent compatibility

# AI Agent Skill Training Guide

## Overview
This guide teaches AI agents how to effectively use all available skills.

## All Skills Available to All Agents

### Debug & Analysis
- **debug** - cbw-debug script.sh
- **analyze** - cbw-analyze --path .
- **visualize** - cbw-visualize --tree
- **python-refactor** - Python refactoring patterns
- **reuse** - Find code reuse opportunities
- **tasks** - Track TODOs

### Letta Memory
- **letta_agents** - Agent management
- **letta_memory** - Memory operations
- **letta_blocks** - Memory blocks
- **letta_backup** - Backup/restore
- **a0_memory** - Agent-Zero memory
- **autonomous_memory** - Auto memory
- **unified_memory** - Cross-agent sync

### Operations
- **docker-ops** - Docker operations
- **github** - GitHub integration
- **infrastructure** - IaC management
- **system-maintenance** - System upkeep
- **shell** - Shell scripting

### Security
- **bitwarden** - Bitwarden vault
- **bitwarden_secrets** - Secret management

### Development
- **coding** - General coding
- **research** - Deep research
- **knowledge** - Knowledge base
- **doc_fetcher** - Fetch documentation
- **skills** - Skill management
- **conversation_logger** - Conversation tracking

## Skill Usage Patterns

### Pattern 1: Investigation
```
When encountering unknown code:
1. analyze - Understand structure
2. debug - Check for issues  
3. visualize - Document architecture
4. [Work with code]
5. debug - Verify no new issues
```

### Pattern 2: Refactoring
```
When refactoring:
1. analyze - Baseline metrics
2. debug - Check current state
3. visualize - Before diagram
4. [Apply refactoring]
5. analyze - Verify improvement
6. debug - Check no regressions
7. visualize - After diagram
```

### Pattern 3: Research
```
When learning new tech:
1. doc_fetcher - Get official docs
2. research - Deep investigation
3. knowledge - Store findings
4. letta_memory - Save to agent memory
```

### Pattern 4: Maintenance
```
Daily/weekly maintenance:
1. system-maintenance - Health check
2. docker-ops - Container cleanup
3. analyze - Config review
4. debug - Script validation
5. letta_backup - Memory backup
```

## Quick Reference

### By Task Type

**Coding Tasks:**
- debug, analyze, visualize, python-refactor, coding

**Operations Tasks:**
- docker-ops, system-maintenance, shell, infrastructure

**Research Tasks:**
- doc_fetcher, research, knowledge, letta_memory

**Memory Tasks:**
- letta_agents, letta_memory, letta_blocks, unified_memory

**Security Tasks:**
- bitwarden, bitwarden_secrets

### By Priority

**Always Use:**
- analyze (before major changes)
- debug (for scripts)
- letta_memory (to save context)

**Use When Needed:**
- visualize (for documentation)
- doc_fetcher (for new topics)
- research (for deep dives)

## Agent Instructions

### Before Starting Any Task

1. **Check Memory**
   ```bash
   letta-memory-cli memory search --agent <name> --query "current task"
   ```

2. **Analyze Context**
   ```bash
   cbw-analyze --path . --structure
   ```

3. **Debug Scripts** (if working with shell scripts)
   ```bash
   cbw-debug script.sh
   ```

### During Work

1. **Save Progress**
   ```bash
   letta-memory-cli memory save --agent <name> --content "Progress..." --type archival
   ```

2. **Check for Issues**
   ```bash
   cbw-debug modified_script.sh
   ```

3. **Document Architecture**
   ```bash
   cbw-visualize --path . --mermaid > docs/arch.md
   ```

### After Completing

1. **Final Analysis**
   ```bash
   cbw-analyze --path . --metrics
   ```

2. **Save Summary**
   ```bash
   letta-memory-cli memory save --agent <name> --content "Completed..." --tags "complete"
   ```

3. **Create Backup**
   ```bash
   letta-memory-cli backup create --agent <name>
   ```

## Skill Chaining Examples

### Example 1: New Project Setup
```bash
# Chain skills for new project
cbw-doc-fetch "framework name"        # Get docs
cbw-analyze --path . --structure     # Analyze structure
cbw-visualize --path . --mermaid     # Create diagram
# [Implement project]
cbw-debug scripts/*.sh               # Check scripts
cbw-analyze --path . --metrics       # Final check
```

### Example 2: Bug Fix
```bash
# Chain skills for debugging
cbw-debug problematic.sh             # Find issues
cbw-analyze --path . --structure     # Understand code
cbw-help "error pattern"             # Search knowledge
# [Fix issue]
cbw-debug fixed.sh                   # Verify fix
letta-memory-cli memory save ...     # Document fix
```

### Example 3: Feature Implementation
```bash
# Chain skills for new feature
cbw-analyze --path . --structure     # Understand codebase
cbw-reuse --similar-to feature.py    # Find patterns
cbw-doc-fetch "related tech"         # Get docs
# [Implement feature]
cbw-debug new_feature.sh             # Check implementation
cbw-analyze --path . --metrics       # Verify quality
```

## Best Practices

### Do:
- ✅ Always save context to letta_memory
- ✅ Use analyze before major changes
- ✅ Debug scripts before committing
- ✅ Visualize architecture changes
- ✅ Fetch docs for unfamiliar tech
- ✅ Chain skills for complex tasks

### Don't:
- ❌ Work without analyzing first
- ❌ Commit scripts without debugging
- ❌ Lose context between sessions
- ❌ Skip documentation steps
- ❌ Ignore skill recommendations

## Skill Discovery

```bash
# List all skills
cbw-skills --list

# Get skill info
cbw-skills --info debug

# Check if available
cbw-skills --check letta_memory

# Get recommendations
cbw-skills --recommend coding
```

## Cross-Agent Coordination

### Share Knowledge
```bash
# Save to shared block
letta-memory-cli block create \
  --label shared_knowledge \
  --value "Important finding..."

# Other agents attach block
letta-memory-cli block attach \
  --agent other_agent \
  --block <block_id>
```

### Handoff Workflow
```bash
# Agent A completes work
letta-memory-cli memory save \
  --agent agent_a \
  --content "HANDOFF: Task complete. Next: implementation" \
  --tags ["handoff", "ready"]

# Agent B picks up
letta-memory-cli memory search \
  --agent agent_b \
  --query "handoff ready"
```

## Training Exercises

### Exercise 1: Debug & Fix
1. Create a buggy script
2. Use cbw-debug to find issues
3. Fix the issues
4. Verify with cbw-debug

### Exercise 2: Analyze & Visualize
1. Pick a codebase
2. Run cbw-analyze --report
3. Create visualization with cbw-visualize
4. Document findings

### Exercise 3: Research & Learn
1. Pick unfamiliar tech
2. Fetch docs with cbw-doc-fetch
3. Research best practices
4. Save to memory

### Exercise 4: Memory Management
1. Create agent
2. Save context
3. Search memories
4. Create backup

## Troubleshooting

### Skill Not Found
```bash
# Verify installation
cbw-skills --list | grep skill_name

# Check path
cat ~/dotfiles/ai/skills/skill_name/SKILL.md
```

### Tool Not Working
```bash
# Check help
python3 ~/dotfiles/ai/scripts/cbw_<tool>.py --help

# Verify Python
which python3 && python3 --version
```

### Letta Server Unavailable
```bash
# Check if running
curl http://localhost:8283/health

# Start if needed
docker start letta-server  # or appropriate command
```

## Success Metrics

Agent is skilled when they can:
- ✅ Choose right skill for task
- ✅ Chain skills effectively
- ✅ Save context consistently
- ✅ Cross-reference skills
- ✅ Debug skill issues
- ✅ Extend skills when needed

## Related Resources

- docs/UNIVERSAL_SKILLS_REGISTRY.md - All skills
- workflows/ - Skill workflows
- skills/*/SKILL.md - Individual skill docs
- scripts/ - Skill tools

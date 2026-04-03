---
name: memory-assisted-coding
version: "1.0.0"
description: "Automatically save successful solutions to Letta memory for future recall across all AI agents"
category: development
agents: [claude, cline, codex, windsurf, kilocode, opencode]
tags: [letta, memory, problem-solving, solutions]
triggers:
  - SOLUTION_FOUND
  - ERROR_RESOLVED
  - INSIGHT_GENERATED
---

# Memory-Assisted Coding Workflow

## Overview
This workflow integrates with the Letta memory system to automatically capture and recall coding solutions. When you solve a problem, the solution is saved to Letta's archival memory. When you encounter similar problems, relevant past solutions are recalled automatically.

## Activation Triggers

The agent will automatically save memories when:
- ✅ **Solution Found**: Successfully completing a coding task
- ✅ **Error Resolved**: Fixing a bug with a working solution
- ✅ **Important Insight**: Learning something valuable about the codebase
- ✅ **Pattern Identified**: Recognizing reusable code patterns

## Workflow Steps

### 1. Before Starting Work
```
ACTION: Search archival memory for relevant context
COMMAND: Search Letta for similar problems or related code patterns
TRIGGER: At session start or when new task begins
```

### 2. During Problem Solving
```
ACTION: Monitor for trigger conditions
CONDITIONS:
  - Complex problem solved
  - Error fixed after debugging
  - New pattern or technique discovered
  - Configuration issue resolved
```

### 3. When Trigger Detected
```
ACTION: Save to Letta Memory
FORMAT:
  - Problem description (what was broken/needed)
  - Solution approach (how it was solved)
  - Code snippet (working solution)
  - Context (file paths, technologies, related issues)
  - Tags (for future searchability)
```

### 4. Cross-Agent Sharing
```
FEATURE: Solutions saved by Claude can be recalled by Windsurf, Cline, etc.
BENEFIT: Knowledge persists across different AI agents and sessions
```

## Memory Triggers Reference

### SOLUTION_FOUND Example
```markdown
**Problem**: Database connection failing with SSL error
**Solution**: Updated connection string with sslmode=require
**Code**: `DATABASE_URL="postgresql://...?sslmode=require"`
**Context**: Supabase PostgreSQL on Node.js
**Tags**: [postgres, ssl, supabase, connection]
```

### ERROR_OCCURRED Example
```markdown
**Error**: Module not found 'letta-client'
**Fix**: npm install letta-client
**Context**: Fresh install of letta_integration package
**Tags**: [npm, letta, installation, troubleshooting]
```

## Usage in Agent Conversations

### For Windsurf / Cline / Claude Code
When solving a problem, the agent should:

1. **Search first**: "Let me check if we've solved this before..."
   - Searches Letta archival memory
   - Finds relevant past solutions
   - Applies patterns if applicable

2. **Save on success**: "I'll save this solution for future reference"
   - Extracts the core problem
   - Documents the working solution
   - Tags appropriately
   - Stores in Letta

3. **Recall during work**: "I recall we had a similar issue with..."
   - Automatically suggests relevant past solutions
   - Adapts previous solutions to current context

## Integration Commands

### Manual Memory Operations
```bash
# Save current solution to memory
letta-save "Fixed TypeScript interface error in auth.ts"

# Search memories
letta-search "typescript interface error"

# List recent memories
letta-list --limit 10
```

### Python API (for advanced use)
```python
from letta_integration import IntelligentMemoryManager

# Initialize manager
memory = IntelligentMemoryManager(agent_name="windsurf")

# Trigger-based save
memory.save_trigger(
    trigger_type="SOLUTION_FOUND",
    content="Fixed Docker compose networking issue",
    context={"files": ["docker-compose.yml"], "tags": ["docker", "networking"]}
)

# Search memories
results = memory.search_archival("docker networking")
```

## Best Practices

1. **Tag Strategically**: Use consistent tags (e.g., always tag language/framework)
2. **Save Incrementally**: Don't wait until the end - save partial solutions
3. **Include Context**: File paths, versions, and environment details matter
4. **Review Periodically**: Use `letta-list` to see what's been saved
5. **Clean Up**: Remove outdated memories that no longer apply

## Troubleshooting

**Q: Agent not saving memories?**
A: Ensure `letta-integration` skill is loaded and Letta server is running at http://localhost:8283

**Q: Memories not found in search?**
A: Check that tags match search terms. Try broader keywords or use vector similarity search.

**Q: Cross-agent sharing not working?**
A: Verify all agents use the same Letta agent ID or have shared memory blocks configured.

## Related Skills
- `letta-integration` - Core memory management
- `conversation-logger` - Session logging
- `universal-loader` - Skill discovery

---

**Workflow Version**: 1.0.0  
**Last Updated**: 2026-03-28  
**Compatible With**: All agents with Letta skill installed

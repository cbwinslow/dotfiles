# Cross-Agent Coordination Workflow

## Purpose
Enable seamless collaboration between all AI agents (qwen, gemini, codex, openclaw, opencode, cline, kilocode, vscode, windsurf, etc.)

## Principles
1. **Shared Memory** - All agents access common knowledge base
2. **Skill Reuse** - All agents can use all skills
3. **Discovery** - Agents can find each other's work
4. **Coordination** - Clear handoffs and context passing

## Coordination Patterns

### Pattern 1: Handoff with Context

Agent A completes task, Agent B continues:

```python
# Agent A (e.g., researcher) finishes research
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="researcher")

# Save findings
letta.save_memory(
    content="""RESEARCH FINDINGS: PostgreSQL vs MongoDB
    
Decision: Use PostgreSQL
Reasons: ACID compliance, JSON support, team familiarity
Tradeoffs: Less flexible schema, harder horizontal scaling
Next steps: Design schema, setup replication""",
    memory_type="archival",
    tags=["research", "database", "decision", "ready-for-implementation"]
)

# Mark as handoff ready
letta.save_memory(
    content="HANDOFF: Database research complete. Ready for implementation by coding agent.",
    memory_type="core",
    tags=["handoff", "researcher-to-coder", "ready"]
)
```

Agent B (e.g., vscode) picks up:

```python
# Agent B discovers handoff
results = letta.search_memories(
    query="handoff ready research",
    memory_type="core",
    tags=["handoff"]
)

# Get full context
decision = letta.search_memories(
    query="PostgreSQL vs MongoDB decision",
    memory_type="archival"
)

# Continue work
# ... implement based on research ...
```

### Pattern 2: Shared Knowledge Blocks

All agents use common knowledge:

```bash
# Create shared block once
letta-memory-cli block create \
  --label team_coding_standards \
  --value "Team Coding Standards:
- Python: PEP 8, type hints, docstrings
- JavaScript: ESLint, Prettier, JSDoc
- Commits: Conventional commits
- Reviews: All PRs need 2 approvals
- Testing: 80% coverage minimum" \
  --limit 2000
```

All agents attach and use:

```bash
# Each agent attaches the block
letta-memory-cli block attach \
  --agent qwen \
  --block <team_coding_standards_id>

letta-memory-cli block attach \
  --agent vscode \
  --block <team_coding_standards_id>

letta-memory-cli block attach \
  --agent windsurf \
  --block <team_coding_standards_id>
```

### Pattern 3: Cross-Agent Search

Find work done by other agents:

```bash
# Search all agents for knowledge
letta-memory-cli search all \
  --query "docker best practices" \
  --limit 5

# Results show which agent contributed what
# Can then query that agent's memories directly
```

### Pattern 4: Task Distribution

Multiple agents work on different parts:

```yaml
# Task: Build microservices platform
# Distributed across agents:

# Agent: researcher
# Task: Research service mesh options
# Output: Decision record in shared memory

# Agent: vscode
# Task: Implement API gateway
# Input: Researcher's decision
# Output: Code + documentation

# Agent: windsurf
# Task: Setup Kubernetes deployment
# Input: API gateway code
# Output: K8s manifests

# Agent: ops-monitor
# Task: Setup monitoring
# Input: Deployment manifests
# Output: Monitoring config
```

## Agent Communication Protocol

### Message Format

```python
{
    "from_agent": "researcher",
    "to_agent": "vscode",  # or "all" for broadcast
    "message_type": "handoff",  # handoff, request, response, broadcast
    "context": {
        "task_id": "abc123",
        "previous_actions": ["research", "analysis"],
        "deliverables": ["decision_record", "comparison_table"],
        "next_steps": ["implementation", "testing"]
    },
    "content": "Research complete. See memory ID: mem_456",
    "priority": "high",
    "timestamp": "2024-03-30T12:00:00Z"
}
```

### Communication Types

1. **Handoff** - Task transfer between agents
2. **Request** - Ask another agent for help
3. **Response** - Reply to a request
4. **Broadcast** - Share info with all agents
5. **Query** - Search for existing knowledge

## Coordination Workflows

### Workflow 1: Research → Code → Deploy

```bash
#!/bin/bash
# research_to_deploy.sh

TASK="implement-microservices"

# Phase 1: Research
echo "=== Phase 1: Research (Agent: researcher) ==="
# Researcher agent works
# Saves findings to letta_memory
# Marks: tags=["$TASK", "research-complete"]

# Phase 2: Implementation
echo "=== Phase 2: Implementation (Agent: vscode/codium) ==="
# Coding agent discovers research
# Implements based on findings
# Saves: code blocks, design decisions
# Marks: tags=["$TASK", "implementation-complete"]

# Phase 3: Deployment
echo "=== Phase 3: Deployment (Agent: windsurf) ==="
# Deployment agent picks up
# Creates K8s manifests, CI/CD
# Saves: deployment configs
# Marks: tags=["$TASK", "deployment-complete"]

# Phase 4: Verification
echo "=== Phase 4: Verification (Agent: ops-monitor) ==="
# Ops agent verifies deployment
# Saves: monitoring setup, health checks
# Marks: tags=["$TASK", "verified"]

echo "=== Task Complete: $TASK ==="
```

### Workflow 2: Bug Report → Fix → Verify

```bash
#!/bin/bash
# bug_fix_workflow.sh

BUG_ID="$1"
DESCRIPTION="$2"

echo "=== Bug Report: $BUG_ID ==="
echo "Description: $DESCRIPTION"

# Step 1: Debug (Any agent)
echo "Step 1: Debugging..."
cbw-debug problematic_script.sh > debug_report.txt

# Save debug info
letta-memory-cli memory save \
  --agent "$(whoami)" \
  --content "Debug report for $BUG_ID: $(cat debug_report.txt)" \
  --type archival \
  --tags ["bug", "$BUG_ID", "debug"]

# Step 2: Fix (Coding agent)
echo "Step 2: Fixing..."
# Coding agent reads debug report
# Implements fix
# Saves fix info

# Step 3: Verify (Different agent)
echo "Step 3: Verification..."
# Another agent verifies the fix
# Independent verification

# Step 4: Document
echo "Step 4: Documentation..."
letta-memory-cli memory save \
  --agent "$(whoami)" \
  --content "Bug $BUG_ID fixed. Root cause: X. Solution: Y." \
  --type core \
  --tags ["bug", "$BUG_ID", "resolved", "knowledge"]
```

## Agent Specialization vs. Universal Access

While all agents CAN use all skills, they have SPECIALIZATIONS:

### Specialized Focus
- **qwen** - General coding, analysis
- **gemini** - Research, documentation
- **codex** - Code generation, refactoring
- **openclaw** - System operations
- **opencode** - Full-stack development
- **cline** - Terminal/command-line focus
- **kilocode** - Large-scale code operations
- **vscode** - IDE-integrated development
- **windsurf** - Web development, UI

### Universal Capability
Despite specializations, ALL agents can:
- Use debug skill to check any script
- Use analyze to understand any codebase
- Use letta_memory to store/retrieve knowledge
- Use any tool in the toolkit

## Shared Workflows

All agents follow these common workflows:

### 1. Before Starting Work
```bash
# 1. Check for existing context
cbw-help "current task status"

# 2. Search shared memories
letta-memory-cli search all --query "current project"

# 3. Analyze current state
cbw-analyze --path .

# 4. Check for handoffs waiting
letta-memory-cli memory list --agent shared | grep "handoff"
```

### 2. During Work
```bash
# 1. Save progress regularly
letta-memory-cli memory save --content "Progress update..."

# 2. Debug when stuck
cbw-debug script.sh

# 3. Search for patterns
cbw-reuse --similar-to my_script.sh

# 4. Document decisions
letta-memory-cli decision create --decision "..."
```

### 3. After Completing Work
```bash
# 1. Final analysis
cbw-analyze --metrics

# 2. Create handoff if needed
letta-memory-cli memory save \
  --content "HANDOFF: Task complete. Next: ..." \
  --tags ["handoff", "ready"]

# 3. Update shared blocks if knowledge changed
letta-memory-cli block update --label shared_knowledge --value "..."

# 4. Backup agent memories
letta-memory-cli backup create --agent my_agent
```

## Conflict Resolution

When multiple agents work on same area:

### Strategy 1: Last Write Wins
```python
# Agent A saves
letta.save_memory(content="Config v1", tags=["config"])

# Agent B saves later
letta.save_memory(content="Config v2", tags=["config"])

# Latest version used
```

### Strategy 2: Append-Only Log
```python
# All changes logged, history preserved
letta.save_memory(
    content="Config change: X -> Y by Agent B",
    memory_type="archival",
    tags=["config", "change-log"]
)
```

### Strategy 3: Explicit Coordination
```bash
# Agents check before modifying
# Use "lock" memory to indicate work in progress

letta-memory-cli memory save \
  --content "LOCK: Agent A working on config.py until 14:00" \
  --tags ["lock", "config.py", "in-progress"]
```

## Agent Discovery

Find what other agents are working on:

```bash
# List all active agents
letta-memory-cli agent list

# Check recent activity
for agent in $(letta-memory-cli agent list | awk '{print $2}'); do
  echo "=== $agent ==="
  letta-memory-cli memory list --agent "$agent" --limit 3
done

# Search for handoffs
letta-memory-cli search all --query "handoff ready" --limit 10
```

## Best Practices

1. **Always save context** - Don't lose work between sessions
2. **Tag consistently** - Use common tag format
3. **Use handoffs** - Clear transfer of work
4. **Search first** - Don't duplicate effort
5. **Share knowledge** - Use shared blocks
6. **Document decisions** - Save why, not just what

## Emergency Protocols

### Agent Offline
- Other agents can access its memories via shared search
- Work can continue using stored context

### Memory Corruption
- Restore from backup
- Multiple agents have backups

### Conflicting Changes
- Use conflict resolution strategies
- Escalate to human if needed

## Success Metrics

Good coordination shows:
- ✅ No duplicated work
- ✅ Smooth handoffs
- ✅ Shared knowledge growing
- ✅ Faster problem resolution
- ✅ Consistent quality

## Related Skills
- All letta_* skills for memory
- All debug/analyze/visualize for code
- All ops skills for infrastructure

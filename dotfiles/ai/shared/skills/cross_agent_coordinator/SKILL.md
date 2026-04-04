---
name: cross_agent_coordinator
description: "Coordinate tasks and share knowledge across AI agents using Letta shared memory. Enables agents to request help, share findings, and maintain consistent knowledge."
version: "1.0.0"
category: coordination
---

# Cross-Agent Coordinator Skill

Enables multi-agent collaboration through Letta shared memory. Agents can post tasks, share findings, and maintain a consistent knowledge base across the ecosystem.

## When to Use

- Task requires input from another agent's specialty
- You found something another agent should know
- User asks to coordinate between agents
- Building shared knowledge across the agent ecosystem

## Agent Registry

| Agent | Specialty | Agent ID |
|-------|-----------|----------|
| kilocode | Server admin, skills, config | `agent-e5e8aab5-9e87-45c1-8025-700503b524c6` |

## Operations

### 1. Post Finding for Other Agents

```bash
~/bin/letta archival-insert <agent-id> \
  "SHARED_KNOWLEDGE: <topic> | FROM: <your-agent> | CONTENT: <what you found> | RELEVANT_TO: <agents or 'all'> | TIME: $(date -Iseconds)" \
  "shared,knowledge,<topic>"
```

### 2. Request Help from Another Agent

```bash
~/bin/letta archival-insert <agent-id> \
  "HELP_REQUEST: <topic> | FROM: <your-agent> | TO: <target-agent> | TASK: <what needs doing> | URGENCY: <low|medium|high> | TIME: $(date -Iseconds)" \
  "help-request,<target-agent>,<topic>"
```

### 3. Search for Relevant Shared Knowledge

```bash
~/bin/letta archival-search <agent-id> "SHARED_KNOWLEDGE: <topic>"
```

### 4. Search for Pending Help Requests

```bash
~/bin/letta archival-search <agent-id> "HELP_REQUEST: TO: <your-agent>"
```

### 5. Share Configuration Change

```bash
~/bin/letta archival-insert <agent-id> \
  "CONFIG_CHANGE: <what changed> | FROM: <your-agent> | FILES: <affected files> | IMPACT: <who needs to know> | TIME: $(date -Iseconds)" \
  "config-change,shared,<topic>"
```

### 6. Register Task Completion

```bash
~/bin/letta archival-insert <agent-id> \
  "TASK_COMPLETE: <task> | AGENT: <your-agent> | RESULT: <outcome> | ARTIFACTS: <files created/modified> | TIME: $(date -Iseconds)" \
  "task-complete,shared,<category>"
```

## Communication Patterns

### Pattern: Knowledge Sharing
```
Agent A discovers X → stores SHARED_KNOWLEDGE to Letta
Agent B working on related task → searches memory → finds Agent A's discovery
Agent B uses the knowledge → stores TASK_COMPLETE with result
```

### Pattern: Help Request
```
Agent A needs Docker expertise → stores HELP_REQUEST targeting kilocode
kilocode searches for HELP_REQUEST → finds request → executes task
kilocode stores TASK_COMPLETE → Agent A searches and gets result
```

### Pattern: Config Propagation
```
Agent A changes nginx config → stores CONFIG_CHANGE
All agents search CONFIG_CHANGE before making related changes
Ensures no conflicting configurations
```

## Tag Convention for Cross-Agent Messages

- `shared` - General shared knowledge
- `knowledge` - Specific knowledge item
- `help-request` - Request for another agent
- `task-complete` - Completed task notification
- `config-change` - Configuration change notification
- `<agent-name>` - Target agent tag
- `<topic>` - Topic-specific tag (docker, nginx, database, etc.)

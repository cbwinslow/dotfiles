---
name: letta_workflows
description: "Workflow automation powered by Letta memory. Store workflow state, track progress, and resume interrupted tasks across sessions and agents."
version: "1.0.0"
category: automation
---

# Letta Workflow Automation Skill

Enables persistent workflow execution with Letta memory backing. Workflows store their state in Letta so they can be resumed, tracked, and coordinated across agents.

## When to Use

- Multi-step tasks that span sessions
- Workflows that need to remember progress
- Tasks that multiple agents contribute to
- Automated maintenance or monitoring workflows

## Operations

### 1. Start a Workflow

Store workflow state in archival memory:
```bash
~/bin/letta archival-insert <agent-id> \
  "WORKFLOW: <name> | STATUS: started | STEP: 1/N | DETAIL: <description> | STARTED: $(date -Iseconds)" \
  "workflow,<name>,active"
```

### 2. Update Workflow Step

```bash
~/bin/letta archival-insert <agent-id> \
  "WORKFLOW: <name> | STATUS: in_progress | STEP: 3/N | DETAIL: completed X, starting Y | TIME: $(date -Iseconds)" \
  "workflow,<name>,active,step"
```

### 3. Complete Workflow

```bash
~/bin/letta archival-insert <agent-id> \
  "WORKFLOW: <name> | STATUS: completed | RESULT: <summary> | COMPLETED: $(date -Iseconds)" \
  "workflow,<name>,completed"
```

### 4. Check Active Workflows

```bash
~/bin/letta archival-search <agent-id> "workflow active STATUS: started"
~/bin/letta archival-search <agent-id> "workflow active STATUS: in_progress"
```

### 5. Resume Interrupted Workflow

```bash
# Find the last step
~/bin/letta archival-search <agent-id> "workflow <name> STEP"

# Continue from last recorded step
~/bin/letta archival-insert <agent-id> \
  "WORKFLOW: <name> | STATUS: resumed | STEP: <last+1>/N | DETAIL: resuming from <context>" \
  "workflow,<name>,active,resumed"
```

### 6. List All Workflows

```bash
~/bin/letta archival-search <agent-id> "WORKFLOW:"
```

## Workflow State Schema

Every workflow state entry follows this format:
```
WORKFLOW: <name> | STATUS: <started|in_progress|completed|failed|paused> | STEP: <current>/<total> | DETAIL: <what happened> | TIME: <ISO timestamp>
```

Tags: `workflow`, `<name>`, `<status>`

## Built-in Workflows

### Infrastructure Maintenance
```bash
~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
  "WORKFLOW: infra-maintenance | STATUS: started | STEP: 1/5 | DETAIL: checking Docker containers" \
  "workflow,infra-maintenance,active"
```

### Code Review
```bash
~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
  "WORKFLOW: code-review | STATUS: started | STEP: 1/4 | DETAIL: reviewing PR #42" \
  "workflow,code-review,active"
```

### Server Setup
```bash
~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
  "WORKFLOW: server-setup | STATUS: started | STEP: 1/10 | DETAIL: configuring PostgreSQL" \
  "workflow,server-setup,active"
```

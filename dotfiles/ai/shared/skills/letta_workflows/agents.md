# Letta Workflows Skill
# Stateful workflow automation backed by Letta archival memory.

## What This Skill Does

Enables multi-step workflows that persist across sessions:
- Start a workflow and track its progress in Letta
- Resume interrupted workflows from the last completed step
- Log decisions made during workflow execution
- Hand off workflows between agents with full context

## When to Use This Skill

- Tasks spanning multiple sessions (deploys, migrations, investigations)
- Multi-agent workflows where different agents handle different steps
- Complex operations that need rollback capability
- User asks to "track progress" on a long task

## How It Works

Workflow state is stored as tagged archival memories in Letta:
```
WORKFLOW: <name> | STATUS: in_progress | STEP: 2/5 | DETAIL: completed X | TIME: <timestamp>
```

Searching for `workflow <name>` retrieves the current state.

## Files

- `SKILL.md` — Full workflow state schema and operations
- `agents.md` — THIS FILE

## Quick Reference

```bash
source ~/.bash_secrets
AGENT="agent-e5e8aab5-9e87-45c1-8025-700503b524c6"

# Start
~/bin/letta archival-insert "$AGENT" "WORKFLOW: deploy | STATUS: started | STEP: 1/5" "workflow,deploy,active"

# Update step
~/bin/letta archival-insert "$AGENT" "WORKFLOW: deploy | STATUS: in_progress | STEP: 2/5" "workflow,deploy,active"

# Complete
~/bin/letta archival-insert "$AGENT" "WORKFLOW: deploy | STATUS: completed | RESULT: success" "workflow,deploy,completed"

# Check status
~/bin/letta archival-search "$AGENT" "workflow deploy"
```

## Why This Exists

User requirement: "I need workflows that can be resumed across sessions. If an agent dies mid-task, another agent should be able to pick up where it left off."

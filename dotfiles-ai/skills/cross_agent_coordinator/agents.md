# Cross-Agent Coordinator Skill
# Multi-agent collaboration through Letta shared memory.

## What This Skill Does

Enables agents to communicate and coordinate through Letta:
- **Post findings**: Share discoveries for other agents to find
- **Request help**: Ask another agent to handle something
- **Share config changes**: Notify all agents of infrastructure changes
- **Register completions**: Mark tasks as done so others know

## When to Use This Skill

- You found something another agent's specialty covers
- You changed a config that other agents might interact with
- User asks to coordinate between agents
- You need help from an agent with different capabilities

## How It Works

All communication is through Letta archival memories with structured tags:
```
SHARED_KNOWLEDGE: <topic> | FROM: kilocode | CONTENT: <finding> | RELEVANT_TO: all
```

Agents search for `SHARED_KNOWLEDGE: <topic>` or `HELP_REQUEST: TO: <agent>` to find messages.

## Agent Registry

| Agent | Specialty |
|-------|-----------|
| kilocode | Server admin, skills, config, Docker, Letta |

(Add more agents as they're set up with Letta IDs)

## Files

- `SKILL.md` — Full communication patterns and tag conventions
- `agents.md` — THIS FILE

## Quick Reference

```bash
source ~/.bash_secrets
AGENT="agent-e5e8aab5-9e87-45c1-8025-700503b524c6"

# Share knowledge
~/bin/letta archival-insert "$AGENT" "SHARED_KNOWLEDGE: nginx | FROM: kilocode | CONTENT: config updated on port 8083" "shared,knowledge,nginx"

# Request help
~/bin/letta archival-insert "$AGENT" "HELP_REQUEST: TO: opencode | TASK: review Python code" "help-request,opencode"

# Search shared knowledge
~/bin/letta archival-search "$AGENT" "SHARED_KNOWLEDGE: nginx"
```

## Why This Exists

User requirement: "I have multiple AI agents. They need to share knowledge and not step on each other's toes. If one agent makes a change, the others should know about it."

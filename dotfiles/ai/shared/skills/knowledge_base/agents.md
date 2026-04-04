# Knowledge Base Skill
# Structured knowledge capture and retrieval from Letta.

## What This Skill Does

Converts raw agent work into structured, searchable knowledge:
- **Decision records**: What was decided and why
- **Runbooks**: Step-by-step procedures for recurring tasks
- **Architecture decisions**: System design choices and tradeoffs
- **Debugging knowledge**: Known issues and their solutions

## When to Use This Skill

- After fixing a bug → document root cause and fix
- After configuring a service → document the configuration
- After making a technical choice → record the decision and rationale
- User asks "what do we know about X?" → search the knowledge base

## Knowledge Entry Format

```
KB: <category> | TOPIC: <topic> | SUMMARY: <1-line> | DETAIL: <full detail> | SOURCE: <origin> | CONFIDENCE: high|medium|low | TIME: <timestamp>
```

## Categories

| Category | Use For |
|----------|---------|
| `config` | Configuration knowledge |
| `docker` | Docker/container knowledge |
| `database` | Database knowledge |
| `security` | Security knowledge |
| `decision` | Decision records |
| `runbook` | Operational procedures |
| `debugging` | Debugging knowledge |
| `performance` | Performance tuning |

## Files

- `SKILL.md` — Full entry formats and search patterns
- `agents.md` — THIS FILE

## Quick Reference

```bash
source ~/.bash_secrets
AGENT="agent-e5e8aab5-9e87-45c1-8025-700503b524c6"

# Store knowledge
~/bin/letta archival-insert "$AGENT" "KB: database | TOPIC: pgvector-tuning | SUMMARY: Set maintenance_work_mem=2GB for 1M vectors | DETAIL: ..." "kb,database,pgvector"

# Search knowledge
~/bin/letta archival-search "$AGENT" "kb pgvector"

# Store decision
~/bin/letta archival-insert "$AGENT" "KB: decision | TOPIC: proxy-choice | DECISION: Use Nginx | RATIONALE: Already installed, mature ecosystem" "kb,decision,nginx"

# Search runbooks
~/bin/letta archival-search "$AGENT" "KB: runbook"
```

## Why This Exists

User requirement: "I need my AI agents to build up knowledge over time. When one agent learns something, that knowledge should be searchable by all agents in the future. I don't want to re-learn the same things."

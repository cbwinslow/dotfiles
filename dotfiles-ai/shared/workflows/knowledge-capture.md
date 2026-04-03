---
name: knowledge-capture
description: "Capture and structure knowledge from agent activities into a searchable knowledge base in Letta. Converts raw work into reusable knowledge entries."
version: "1.0.0"
triggers: [task_complete, research_complete, fix_complete]
agents: [all]
---

# Knowledge Capture Workflow

Converts completed work into structured, searchable knowledge in Letta.

## When to Capture Knowledge

- After fixing a bug (document the root cause and fix)
- After learning how something works (document the mechanism)
- After completing research (document findings)
- After solving a novel problem (document the solution)
- After configuring a new service (document the configuration)

## Steps

1. **Identify the knowledge** from completed work:
   - What was the problem/question?
   - What was the solution/answer?
   - What would someone need to know to reproduce this?
   - What pitfalls or gotchas exist?

2. **Format as structured entry**:
   ```
   KB: <category> | TOPIC: <topic> | SUMMARY: <1-line> | DETAIL: <full explanation with commands/config> | SOURCE: <where this came from> | CONFIDENCE: <high|medium|low> | TIME: <timestamp>
   ```

3. **Store in Letta**:
   ```bash
   source ~/.bash_secrets
   ~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
     "KB: <category> | TOPIC: <topic> | SUMMARY: <summary> | DETAIL: <detail with commands> | SOURCE: <origin> | CONFIDENCE: high | TIME: $(date -Iseconds)" \
     "kb,<category>,<topic>"
   ```

4. **Store as runbook** if it's a procedure:
   ```bash
   ~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
     "KB: runbook | TOPIC: <procedure> | STEPS: <1. step one; 2. step two; ...> | WHEN: <trigger condition> | PREREQUISITES: <what's needed> | TIME: $(date -Iseconds)" \
     "kb,runbook,<topic>"
   ```

## Knowledge Categories

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
| `integration` | Service integration patterns |

## Example

```bash
source ~/.bash_secrets

# After learning how to tune PostgreSQL for pgvector
~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
  "KB: database | TOPIC: pgvector-performance | SUMMARY: PostgreSQL pgvector tuning for 768d embeddings | DETAIL: Set maintenance_work_mem=2GB, ivfflat.probes=10 for 1M vectors, CREATE INDEX CONCURRENTLY for no downtime, analyze after bulk inserts | SOURCE: Tuning cbw_rag database | CONFIDENCE: high | TIME: 2026-04-02T11:00:00-04:00" \
  "kb,database,pgvector,performance"
```

## Searching Knowledge

```bash
# Search by topic
~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "kb pgvector"

# Search by category
~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "KB: database"

# Search runbooks
~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "KB: runbook"
```

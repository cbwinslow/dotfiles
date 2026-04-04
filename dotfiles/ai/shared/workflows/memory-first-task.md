---
name: memory-first-task
description: "Universal workflow: always search Letta memory before starting work, store results after completing. Applies to every agent on every task."
version: "1.0.0"
triggers: [task_start, task_complete]
agents: [all]
---

# Memory-First Task Workflow

This is the **universal workflow** that ALL agents should follow for every task.

## Steps

### Phase 1: Pre-Task (BEFORE doing anything)

1. **Source secrets**: `source ~/.bash_secrets`
2. **Search memory** for the current task:
   ```bash
   ~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "<task summary>"
   ```
3. **Read results** — if relevant memories found, incorporate that context
4. **Check workflows** for active related work:
   ```bash
   ~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "workflow active <topic>"
   ```

### Phase 2: Execute Task

5. Perform the task, referencing prior knowledge when available
6. Note any decisions made and why

### Phase 3: Post-Task (AFTER completing)

7. **Store result** with structured format:
   ```bash
   ~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
     "$(date +%Y-%m-%d): <description of what was done and key outcomes>" \
     "<relevant,tags,here>"
   ```
8. **Store decision** if one was made:
   ```bash
   ~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
     "DECISION: <what was decided> | RATIONALE: <why> | TOPIC: <topic>" \
     "decision,<topic>"
   ```
9. **Update workflow** if this was part of a multi-step workflow

## Tag Requirements

Every archival memory must have at least 2 tags:
- One category tag: `config`, `docker`, `database`, `skills`, `infra`, `security`, `fix`, `feature`
- One context tag: topic-specific (e.g., `nginx`, `postgresql`, `letta`, `rag`)

## Quick Reference

```bash
# Full pattern
source ~/.bash_secrets
~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "query"
# ... do work ...
~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "YYYY-MM-DD: summary" "tag1,tag2"
```

# Shared Workflows
# Multi-step automation patterns available to ALL AI agents.
# These workflows use Letta memory to persist state across sessions.

## Purpose

Workflows define repeatable multi-step processes. Each workflow is a markdown file with YAML frontmatter. Workflows store their execution state in Letta archival memory, enabling:
- Resumable tasks across sessions
- Progress tracking
- Cross-agent workflow handoffs

## Available Workflows

| File | Name | Trigger | Description |
|------|------|---------|-------------|
| `memory-first-task.md` | memory-first-task | task_start, task_complete | Universal: search memory before task, store after |
| `cross-agent-decision.md` | cross-agent-decision | decision_made | Record important decisions for all agents |
| `knowledge-capture.md` | knowledge-capture | task_complete, research_complete | Convert work into searchable knowledge |
| `skill-sync.md` | skill-sync | skill_added, manual | Sync skill registries across locations |
| `server-health-check.md` | server-health-check | manual, scheduled | Comprehensive health monitoring |

## How to Use Workflows

Workflows are not "loaded" like skills — they are **rules and patterns** that agents follow. When an agent sees a workflow file, it should incorporate those steps into its behavior.

### Example: memory-first-task

This workflow says: "Before EVERY task, search Letta. After EVERY task, store results." An agent reading this should automatically:
1. `source ~/.bash_secrets && ~/bin/letta archival-search <agent-id> "<task summary>"`
2. Do the task
3. `~/bin/letta archival-insert <agent-id> "<summary>" "tags"`

## Creating a New Workflow

1. Create file: `workflows/my-workflow.md`
2. Add YAML frontmatter:
   ```yaml
   ---
   name: my-workflow
   description: "What this workflow does"
   version: 1.0.0
   triggers: [manual]
   agents: [all]
   ---
   ```
3. Document the steps with exact commands
4. Add row to the table above
5. Update `~/AGENTS.md` if it's a universal workflow

## Relationship to Letta

All workflow state is stored in Letta archival memory with the `workflow` tag:
```
WORKFLOW: <name> | STATUS: <status> | STEP: <n>/<total> | DETAIL: <what happened>
```

Search active workflows: `~/bin/letta archival-search <agent-id> "workflow active"`

## Important Rule

The `memory-first-task` workflow is **mandatory for all agents**. No exceptions. User explicitly required: "every AI agent should search memory before starting work and store results after."

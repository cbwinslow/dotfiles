---
name: knowledge_base
description: "Build and maintain a searchable knowledge base from all agent activities. Structured knowledge capture with entity extraction, categorization, and retrieval."
version: "1.0.0"
category: knowledge
---

# Knowledge Base Skill

Builds a structured, searchable knowledge base from all agent activities. Uses Letta archival memory with structured entries for fast retrieval.

## When to Use

- User asks "what do we know about X?"
- You need to build on prior research
- Maintaining documentation from agent work
- Extracting reusable patterns from past tasks

## Knowledge Entry Format

Every knowledge entry follows this structure:
```
KB: <category> | TOPIC: <topic> | SUMMARY: <1-line summary> | DETAIL: <full details> | SOURCE: <where this came from> | CONFIDENCE: <high|medium|low> | TIME: $(date -Iseconds)
```

## Operations

### 1. Store Knowledge

```bash
~/bin/letta archival-insert <agent-id> \
  "KB: <category> | TOPIC: <topic> | SUMMARY: <summary> | DETAIL: <full detail> | SOURCE: <source> | CONFIDENCE: <high|medium|low> | TIME: $(date -Iseconds)" \
  "kb,<category>,<topic>"
```

### 2. Search Knowledge

```bash
~/bin/letta archival-search <agent-id> "KB: <category> TOPIC: <topic>"
~/bin/letta archival-search <agent-id> "kb <topic>"
```

### 3. Store Decision Record

```bash
~/bin/letta archival-insert <agent-id> \
  "KB: decision | TOPIC: <topic> | DECISION: <what was decided> | RATIONALE: <why> | ALTERNATIVES: <what else was considered> | TIME: $(date -Iseconds)" \
  "kb,decision,<topic>"
```

### 4. Store Runbook

```bash
~/bin/letta archival-insert <agent-id> \
  "KB: runbook | TOPIC: <procedure name> | STEPS: <step-by-step procedure> | WHEN: <when to use> | PREREQUISITES: <what's needed> | TIME: $(date -Iseconds)" \
  "kb,runbook,<topic>"
```

### 5. Store Architecture Decision Record

```bash
~/bin/letta archival-insert <agent-id> \
  "KB: adr | TOPIC: <decision title> | STATUS: <accepted|superseded|deprecated> | CONTEXT: <situation> | DECISION: <what> | CONSEQUENCES: <tradeoffs> | TIME: $(date -Iseconds)" \
  "kb,adr,<topic>"
```

## Knowledge Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `config` | Configuration knowledge | nginx.conf patterns, PostgreSQL tuning |
| `docker` | Docker and container knowledge | Compose patterns, networking |
| `database` | Database knowledge | Schema design, query patterns |
| `security` | Security knowledge | Auth patterns, firewall rules |
| `decision` | Decision records | Technology choices, tradeoffs |
| `runbook` | Operational procedures | Deploy, backup, recovery |
| `adr` | Architecture decisions | System design choices |
| `debugging` | Debugging knowledge | Known issues, solutions |
| `performance` | Performance knowledge | Optimization patterns |
| `integration` | Integration knowledge | API patterns, service configs |

## Query Patterns

### Find all decisions about Docker
```bash
~/bin/letta archival-search <agent-id> "KB: decision TOPIC: docker"
```

### Find runbooks for database operations
```bash
~/bin/letta archival-search <agent-id> "KB: runbook TOPIC: database"
```

### Find all knowledge about nginx
```bash
~/bin/letta archival-search <agent-id> "kb nginx"
```

### Get recent knowledge (by searching time)
```bash
~/bin/letta archival-search <agent-id> "KB: TIME: 2026-04"
```

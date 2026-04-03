---
description: Workflow for memory operations and knowledge management
tags: [letta, memory, workflow, knowledge]
---

# Letta Memory Operations Workflow

## Overview
Complete workflow for managing agent memories: saving, searching, organizing, and maintaining knowledge bases.

## Quick Reference

| Operation | Command |
|-----------|---------|
| Save memory | `letta-memory-cli memory save --agent X --content Y --type Z` |
| Search | `letta-memory-cli memory search --agent X --query Y` |
| List | `letta-memory-cli memory list --agent X` |
| Delete | `letta-memory-cli memory delete --agent X --id Y` |

## Phase 1: Memory Planning

### 1.1 Define Memory Strategy
```bash
# Questions to answer:
# - What types of info to store? (core vs archival)
# - Tagging scheme?
# - Retention policy?
# - Search strategy?

# Document strategy
cat > memory_strategy.md << 'EOF'
# Memory Strategy for Agent: coding_assistant

## Types
- CORE: Coding standards, user preferences, project structure
- ARCHIVAL: Conversations, code examples, solutions

## Tags
- category:{coding,ops,docs}
- topic:{python,docker,k8s}
- priority:{high,medium,low}
- source:{conversation,docs,code}

## Retention
- Core: Permanent
- Archival: 90 days (auto-cleanup)
- Context: 7 days

## Search Priority
1. Core memories (preferences, standards)
2. Recent archival (last 30 days)
3. Older archival (semantic relevance)
EOF
```

### 1.2 Plan Initial Memories
```bash
# Create seed memories for new agent
AGENT_NAME="coding_assistant"

# Core preferences
letta-memory-cli memory save \
  --agent "$AGENT_NAME" \
  --content "User prefers Python 3.11+, type hints mandatory, docstrings for public APIs, black formatter, pytest for testing." \
  --type core \
  --tags "preference,coding,python,standards"

# Project knowledge
letta-memory-cli memory save \
  --agent "$AGENT_NAME" \
  --content "Project structure: /src (source), /tests (pytest), /docs (mkdocs), /scripts (utilities). Main entry: src/main.py. Config: pyproject.toml" \
  --type core \
  --tags "project,structure,config"

# Common patterns
letta-memory-cli memory save \
  --agent "$AGENT_NAME" \
  --content "Common refactoring pattern: Extract function when >50 lines, Create class when >5 related functions, Module split when >300 lines." \
  --type core \
  --tags "patterns,refactoring,best-practices"
```

## Phase 2: Daily Memory Operations

### 2.1 Context Saving
```bash
# At start of session
save_session_context() {
  local agent="$1"
  local task="$2"
  
  letta-memory-cli memory save \
    --agent "$agent" \
    --content "Current focus: $task. Started: $(date). Tools: Python, Docker, PostgreSQL." \
    --type context \
    --tags "session,context,$(date +%Y-%m-%d)"
}

# Usage
save_session_context "coding_assistant" "refactoring auth module"
```

### 2.2 Important Facts
```bash
# When learning important info
save_key_fact() {
  local agent="$1"
  local fact="$2"
  local category="$3"
  
  letta-memory-cli memory save \
    --agent "$agent" \
    --content "$fact" \
    --type core \
    --tags "fact,$category,important"
}

# Examples
save_key_fact "coding_assistant" "Database connection pool max: 20 connections" "config"
save_key_fact "coding_assistant" "API rate limit: 100 requests/minute" "api"
```

### 2.3 Conversation Archiving
```bash
# Save completed conversation
archive_conversation() {
  local agent="$1"
  local topic="$2"
  shift 2
  local messages="$@"
  
  # Format as JSON array
  json_messages=$(echo "$messages" | python3 -c "
import json
import sys
lines = sys.stdin.read().strip().split('\n')
messages = []
for line in lines:
    if line.startswith('USER:'):
        messages.append({'role': 'user', 'content': line[5:].strip()})
    elif line.startswith('AGENT:'):
        messages.append({'role': 'assistant', 'content': line[6:].strip()})
print(json.dumps(messages))
")
  
  letta-memory-cli conversation save \
    --agent "$agent" \
    --messages "$json_messages" \
    --tags "conversation,$topic,archive"
}

# Usage
archive_conversation "coding_assistant" "docker-setup" << 'EOF'
USER: How do I setup Docker for this project?
AGENT: You need docker-compose.yml, Dockerfile, and .dockerignore...
USER: What base image should I use?
AGENT: Use python:3.11-slim for production...
EOF
```

## Phase 3: Memory Retrieval

### 3.1 Context Retrieval
```bash
# Get relevant memories before task
get_context() {
  local agent="$1"
  local query="$2"
  
  # Search all memory types
  echo "=== Relevant Memories ==="
  
  # Core memories (preferences, standards)
  echo "Core:"
  letta-memory-cli memory search \
    --agent "$agent" \
    --query "$query" \
    --type core \
    --limit 3
  
  # Recent archival
  echo -e "\nRecent:"
  letta-memory-cli memory search \
    --agent "$agent" \
    --query "$query" \
    --type archival \
    --limit 5
}

# Usage before task
get_context "coding_assistant" "docker deployment"
```

### 3.2 Knowledge Base Queries
```bash
# Query specific knowledge areas
query_kb() {
  local agent="$1"
  local area="$2"
  local query="$3"
  
  echo "=== Knowledge Base: $area ==="
  
  letta-memory-cli memory search \
    --agent "$agent" \
    --query "$query $area" \
    --limit 10 | \
  while read -r line; do
    if echo "$line" | grep -q "Content:"; then
      echo "  - $line"
    fi
  done
}

# Usage
query_kb "coding_assistant" "python" "best practices"
```

### 3.3 Cross-Agent Search
```bash
# Find knowledge across all agents
find_global_knowledge() {
  local query="$1"
  
  echo "=== Cross-Agent Search: $query ==="
  
  letta-memory-cli search all \
    --query "$query" \
    --limit 3
}

# Usage
find_global_knowledge "kubernetes deployment"
```

## Phase 4: Memory Organization

### 4.1 Tag Management
```bash
# List all tags used by agent
list_tags() {
  local agent="$1"
  
  # Extract tags from memories
  letta-memory-cli memory list --agent "$agent" | \
  grep "Tags:" | \
  sed 's/Tags: //' | \
  tr ',' '\n' | \
  sort | uniq -c | sort -rn
}

# Usage
list_tags "coding_assistant"
```

### 4.2 Memory Cleanup
```bash
#!/bin/bash
# cleanup_memories.sh

AGENT_NAME="$1"
DAYS_OLD="${2:-90}"
MEMORY_TYPE="${3:-archival}"

echo "Cleaning up $AGENT_NAME memories..."
echo "Type: $MEMORY_TYPE, Older than: $DAYS_OLD days"

# Use Python for complex filtering
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')
from unified_memory import search_files_content
from datetime import datetime, timedelta

# This would integrate with actual memory cleanup
# For now, just list what would be cleaned

print(f"Would clean memories older than $DAYS_OLD days")
print("Use with caution - implement actual deletion logic")
EOF
```

### 4.3 Duplicate Detection
```bash
#!/bin/bash
# find_duplicates.sh

AGENT_NAME="$1"

echo "=== Finding Duplicate Memories: $AGENT_NAME ==="

# Search for similar content
python3 << 'EOF'
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="'$AGENT_NAME'")
memories = letta.get_memories()

# Find potential duplicates
seen = {}
for mem in memories:
    content = mem['content'][:100]  # First 100 chars
    if content in seen:
        print(f"Potential duplicate:")
        print(f"  Original: {seen[content]}")
        print(f"  Duplicate: {mem['id']}")
    else:
        seen[content] = mem['id']
EOF
```

## Phase 5: Knowledge Base Building

### 5.1 Extract and Store Entities
```bash
# Extract entities from text and store
extract_and_store() {
  local agent="$1"
  local text="$2"
  
  letta-memory-cli entities extract \
    --agent "$agent" \
    --text "$text"
}

# Usage
text="Edit the config at /etc/nginx/nginx.conf then run sudo nginx -t and check https://nginx.org/en/docs/"
extract_and_store "ops_agent" "$text"
# Stores: file path, command, URL as separate memories
```

### 5.2 Structured Knowledge
```bash
# Save structured knowledge
save_knowledge() {
  local agent="$1"
  local topic="$2"
  local knowledge="$3"
  
  letta-memory-cli memory save \
    --agent "$agent" \
    --content "TOPIC: $topic
KNOWLEDGE:
$knowledge
SOURCE: manual_entry
DATE: $(date)" \
    --type core \
    --tags "knowledge,$topic,structured"
}

# Usage
save_knowledge "coding_assistant" "python-decorators" "Decorators wrap functions. Use @wraps from functools to preserve metadata. Can be stacked."
```

### 5.3 Decision Logging
```bash
# Log important decisions
log_decision() {
  local agent="$1"
  local decision="$2"
  local context="$3"
  local alternatives="$4"
  
  letta-memory-cli decision create \
    --agent "$agent" \
    --decision "$decision" \
    --context "$context" \
    --tags "decision,$(date +%Y-%m)"
  
  # Also save as memory for searchability
  letta-memory-cli memory save \
    --agent "$agent" \
    --content "DECISION: $decision\nCONTEXT: $context\nALTERNATIVES: $alternatives\nDATE: $(date)" \
    --type archival \
    --tags "decision,architecture,$(date +%Y-%m)"
}

# Usage
log_decision "coding_assistant" \
  "Use PostgreSQL over MongoDB for user data" \
  "Need ACID compliance for financial transactions" \
  "MongoDB (flexible), MySQL (familiar), PostgreSQL (features)"
```

## Phase 6: Memory Analytics

### 6.1 Memory Statistics
```bash
#!/bin/bash
# memory_stats.sh

AGENT_NAME="$1"

echo "=== Memory Statistics: $AGENT_NAME ==="

# Count by type
echo -e "\nBy Type:"
for type in core archival context; do
  count=$(letta-memory-cli memory list --agent "$AGENT_NAME" --type "$type" 2>/dev/null | wc -l)
  echo "  $type: $count"
done

# Recent activity
echo -e "\nRecent Activity (last 7 days):"
# Would use Python for date filtering

# Top tags
echo -e "\nTop Tags:"
list_tags "$AGENT_NAME" | head -10
```

### 6.2 Knowledge Gap Analysis
```bash
#!/bin/bash
# find_gaps.sh

AGENT_NAME="$1"
EXPECTED_TOPICS="python docker kubernetes testing"

echo "=== Knowledge Gap Analysis ==="

for topic in $EXPECTED_TOPICS; do
  count=$(letta-memory-cli memory search \
    --agent "$AGENT_NAME" \
    --query "$topic" \
    --limit 100 2>/dev/null | wc -l)
  
  if [ "$count" -lt 5 ]; then
    echo "⚠️  Low coverage: $topic ($count memories)"
  else
    echo "✅ Good coverage: $topic ($count memories)"
  fi
done
```

## Complete Automation

### Daily Memory Routine
```bash
#!/bin/bash
# daily_memory_routine.sh

AGENT_NAME="$1"

echo "=== Daily Memory Routine: $AGENT_NAME ==="

# 1. Archive completed context
# (Would need to track what's completed)

# 2. Extract entities from today's work
# (Would integrate with actual work tracking)

# 3. Save key learnings
# (Manual or extracted)

# 4. Run analytics
echo "Memory stats:"
bash memory_stats.sh "$AGENT_NAME"

# 5. Cleanup old context
echo "Cleaning old context..."
# bash cleanup_memories.sh "$AGENT_NAME" 7 context

echo "Routine complete"
```

## Best Practices

### Do:
- ✅ Tag consistently
- ✅ Use appropriate memory types
- ✅ Search before saving (avoid duplicates)
- ✅ Archive conversations regularly
- ✅ Clean up old context
- ✅ Extract entities automatically

### Don't:
- ❌ Store sensitive data (passwords, keys)
- ❌ Save everything (be selective)
- ❌ Use only one memory type
- ❌ Forget to tag
- ❌ Ignore cleanup

## Troubleshooting

### Search Returns Nothing
```bash
# Check if memories exist
letta-memory-cli memory list --agent my_agent

# Try broader search
letta-memory-cli memory search --agent my_agent --query "*"

# Check memory type filter
```

### Memory Not Saving
```bash
# Check server health
letta-memory-cli health

# Verify agent exists
letta-memory-cli agent list | grep my_agent

# Check content isn't empty
```

### Too Many Duplicates
```bash
# Find duplicates
bash find_duplicates.sh my_agent

# Clean up manually or with script
```

## Related Skills
- letta_memory - Detailed memory operations
- letta_agents - Agent management
- letta_backup - Backup memories

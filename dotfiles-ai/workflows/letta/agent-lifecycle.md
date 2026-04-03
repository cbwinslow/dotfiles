---
description: Complete agent lifecycle management from creation to deletion
tags: [letta, agents, lifecycle, automation]
---

# Letta Agent Lifecycle Workflow

## Overview
Complete workflow for managing Letta agents through their entire lifecycle: creation, configuration, operation, maintenance, and deletion.

## Prerequisites
- Letta server running
- letta_integration package installed
- Environment variables configured

## Phase 1: Planning

### 1.1 Define Agent Purpose
```bash
# Answer these questions:
# - What is the agent's primary role?
# - What knowledge does it need?
# - Which other agents will it interact with?
# - What memories should it persist?

# Document the plan
cat > agent_plan.md << 'EOF'
# New Agent Plan

**Name:** coding_reviewer
**Purpose:** Review code changes and suggest improvements
**Type:** Specialist (code review)

**Required Blocks:**
- persona_code_reviewer
- config_dev
- knowledge_python
- knowledge_best_practices

**Interactions:**
- Receives code from coding agent
- Stores review results
- Flags critical issues

**Memory Requirements:**
- Core: User preferences, coding standards
- Archival: Past reviews, common issues
EOF
```

### 1.2 Check Existing Agents
```bash
# List current agents
letta-memory-cli agent list

# Check for naming conflicts
letta-memory-cli agent list | grep -i "coding_reviewer"

# Review similar agents for patterns
letta-memory-cli agent list | grep -i "review"
```

## Phase 2: Creation

### 2.1 Create Base Agent
```bash
AGENT_NAME="coding_reviewer"
PERSONA="I am an expert code reviewer. I analyze code for quality, security, and performance issues. I provide constructive feedback with specific examples and line references."
HUMAN="User is a senior developer who values detailed explanations and clean code. They prefer actionable feedback over general comments."

echo "Creating agent: $AGENT_NAME"
letta-memory-cli agent create \
  --name "$AGENT_NAME" \
  --persona "$PERSONA" \
  --human "$HUMAN"

# Verify creation
AGENT_ID=$(letta-memory-cli agent list | grep "$AGENT_NAME" | awk '{print $1}')
echo "Agent created with ID: $AGENT_ID"
```

### 2.2 Configure Core Memory Blocks
```bash
# Create persona block if doesn't exist
PERSONA_BLOCK=$(letta-memory-cli block list | grep "persona_code_reviewer" | awk '{print $1}')

if [ -z "$PERSONA_BLOCK" ]; then
  echo "Creating persona block..."
  
  PERSONA_CONTENT="I am CodeReviewBot, specialized in code analysis.

My capabilities:
- Identify bugs and security issues
- Suggest performance improvements
- Check for best practices
- Verify test coverage

Review style:
- Categorize as: Critical, Warning, Suggestion
- Include line numbers
- Provide code examples
- Explain reasoning"

  letta-memory-cli block create \
    --label persona_code_reviewer \
    --value "$PERSONA_CONTENT" \
    --limit 5000
fi

# Attach to agent
PERSONA_BLOCK=$(letta-memory-cli block list | grep "persona_code_reviewer" | awk '{print $1}')
letta-memory-cli block attach \
  --agent "$AGENT_NAME" \
  --block "$PERSONA_BLOCK"
```

### 2.3 Attach Configuration Blocks
```bash
# Attach relevant blocks
BLOCKS=(
  "config_dev"
  "knowledge_python"
  "knowledge_best_practices"
)

for block_label in "${BLOCKS[@]}"; do
  BLOCK_ID=$(letta-memory-cli block list | grep "$block_label" | awk '{print $1}')
  
  if [ -n "$BLOCK_ID" ]; then
    echo "Attaching: $block_label"
    letta-memory-cli block attach \
      --agent "$AGENT_NAME" \
      --block "$BLOCK_ID"
  else
    echo "Warning: Block $block_label not found"
  fi
done
```

### 2.4 Initial Memory Setup
```bash
# Save initial context
letta-memory-cli memory save \
  --agent "$AGENT_NAME" \
  --content "Agent initialized. Core capabilities: code review, quality analysis, security checks. Standards: PEP 8, type hints, docstrings." \
  --type core \
  --tags "init,config,standards"

# Save user preferences (if known)
letta-memory-cli memory save \
  --agent "$AGENT_NAME" \
  --content "User preferences: prefers detailed explanations, wants security issues flagged immediately, appreciates code examples." \
  --type core \
  --tags "preference,user,context"
```

## Phase 3: Verification

### 3.1 Validate Setup
```bash
#!/bin/bash
# verify_agent.sh

AGENT_NAME="$1"

echo "=== Agent Verification: $AGENT_NAME ==="

# 1. Check agent exists
AGENT_INFO=$(letta-memory-cli agent list | grep "$AGENT_NAME")
if [ -z "$AGENT_INFO" ]; then
  echo "❌ Agent not found"
  exit 1
fi
echo "✅ Agent exists"

# 2. Check memory blocks
BLOCK_COUNT=$(letta-memory-cli block list --agent "$AGENT_NAME" 2>/dev/null | wc -l)
if [ "$BLOCK_COUNT" -lt 2 ]; then
  echo "⚠️  Only $BLOCK_COUNT blocks attached (expected at least 2)"
else
  echo "✅ $BLOCK_COUNT blocks attached"
fi

# 3. Check core memories
MEMORY_COUNT=$(letta-memory-cli memory list --agent "$AGENT_NAME" --type core 2>/dev/null | wc -l)
if [ "$MEMORY_COUNT" -eq 0 ]; then
  echo "⚠️  No core memories found"
else
  echo "✅ $MEMORY_COUNT core memories"
fi

# 4. Test server communication
echo "Checking server communication..."
letta-memory-cli stats --agent "$AGENT_NAME" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Server communication OK"
else
  echo "❌ Server communication failed"
fi

echo "=== Verification Complete ==="
```

### 3.2 Test Basic Operations
```bash
# Test memory save
TEST_MEMORY="Test memory created during agent verification $(date)"
letta-memory-cli memory save \
  --agent "$AGENT_NAME" \
  --content "$TEST_MEMORY" \
  --type archival \
  --tags "test,verification"

# Test memory search
RESULT=$(letta-memory-cli memory search \
  --agent "$AGENT_NAME" \
  --query "test memory" \
  --limit 1)

if echo "$RESULT" | grep -q "test"; then
  echo "✅ Memory search working"
else
  echo "❌ Memory search failed"
fi

# Clean up test memory
# (Optional - keep for record)
```

## Phase 4: Operation

### 4.1 Daily Operations
```bash
# Save work context
save_work_context() {
  local agent="$1"
  local context="$2"
  
  letta-memory-cli memory save \
    --agent "$agent" \
    --content "$context" \
    --type context \
    --tags "daily,work,$(date +%Y-%m-%d)"
}

# Usage
save_work_context "$AGENT_NAME" "Currently reviewing authentication module. Focus on: SQL injection prevention, password hashing, session management."
```

### 4.2 Weekly Review
```bash
#!/bin/bash
# weekly_review.sh

AGENT_NAME="$1"

echo "=== Weekly Review: $AGENT_NAME ==="

# 1. Memory statistics
echo -e "\n📊 Memory Statistics"
letta-memory-cli stats --agent "$AGENT_NAME"

# 2. Recent memories
echo -e "\n📝 Recent Memories"
letta-memory-cli memory list \
  --agent "$AGENT_NAME" \
  --limit 10

# 3. Search for patterns
echo -e "\n🔍 Common Topics"
# This would require analysis of memory content
# For now, just list tags

# 4. Health check
echo -e "\n✅ Health Check"
letta-memory-cli stats --agent "$AGENT_NAME" > /dev/null && echo "Healthy" || echo "Issues detected"
```

### 4.3 Memory Maintenance
```bash
# Archive old context memories
archive_old_context() {
  local agent="$1"
  local days="${2:-7}"
  
  # Implementation would use Python for date filtering
  python3 << 'EOF'
from letta_integration import LettaIntegration
from datetime import datetime, timedelta

letta = LettaIntegration(agent_name="'$agent'")
cutoff = datetime.now() - timedelta(days='$days')

memories = letta.get_memories(memory_type="context")
for mem in memories:
    created = datetime.fromisoformat(mem['created_at'])
    if created < cutoff:
        # Could delete or archive
        print(f"Old context: {mem['id'][:8]} from {created}")
EOF
}
```

## Phase 5: Maintenance

### 5.1 Regular Backups
```bash
#!/bin/bash
# backup_agent.sh

AGENT_NAME="$1"
BACKUP_DIR="${2:-$HOME/backups/letta}"

mkdir -p "$BACKUP_DIR"

echo "Creating backup for: $AGENT_NAME"

# Create backup
letta-memory-cli backup create \
  --agent "$AGENT_NAME" \
  --path "$BACKUP_DIR"

# Verify backup
LATEST=$(ls -t "$BACKUP_DIR/${AGENT_NAME}_"*.json 2>/dev/null | head -1)
if [ -f "$LATEST" ]; then
  echo "✅ Backup created: $LATEST"
  ls -lh "$LATEST"
else
  echo "❌ Backup failed"
fi
```

### 5.2 Block Updates
```bash
# Update agent blocks when knowledge changes
update_agent_knowledge() {
  local agent="$1"
  local block_label="$2"
  local new_content="$3"
  
  # Get block ID
  BLOCK_ID=$(letta-memory-cli block list | grep "$block_label" | awk '{print $1}')
  
  if [ -n "$BLOCK_ID" ]; then
    # Update block
    letta-memory-cli block update \
      --label "$block_label" \
      --value "$new_content"
    
    echo "Updated block: $block_label"
    
    # Reattach if needed (usually automatic)
    letta-memory-cli block detach --agent "$agent" --block "$BLOCK_ID" 2>/dev/null || true
    letta-memory-cli block attach --agent "$agent" --block "$BLOCK_ID"
  fi
}
```

### 5.3 Performance Monitoring
```bash
# Monitor agent performance
monitor_agent() {
  local agent="$1"
  
  # Get stats
  STATS=$(letta-memory-cli stats --agent "$agent" 2>&1)
  
  # Check memory count
  MEM_COUNT=$(echo "$STATS" | grep -oP 'memories: \K[0-9]+' || echo "0")
  
  if [ "$MEM_COUNT" -gt 1000 ]; then
    echo "⚠️  High memory count: $MEM_COUNT (consider cleanup)"
  fi
  
  # Check response time (if available)
  # This would require timing the API calls
}
```

## Phase 6: Deletion (when needed)

### 6.1 Pre-Deletion Backup
```bash
# Always backup before deletion
backup_before_delete() {
  local agent="$1"
  
  echo "Creating final backup for: $agent"
  
  letta-memory-cli backup create \
    --agent "$agent" \
    --path "$HOME/backups/letta/final"
  
  echo "Backup complete. Ready for deletion."
}
```

### 6.2 Safe Deletion
```bash
#!/bin/bash
# safe_delete_agent.sh

AGENT_NAME="$1"

echo "=== Safe Agent Deletion: $AGENT_NAME ==="

# 1. Confirm
read -p "Are you sure you want to delete '$AGENT_NAME'? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
  echo "Cancelled"
  exit 0
fi

# 2. Backup
backup_before_delete "$AGENT_NAME"

# 3. Get agent ID
AGENT_ID=$(letta-memory-cli agent list | grep "$AGENT_NAME" | awk '{print $1}')

# 4. Delete
if [ -n "$AGENT_ID" ]; then
  echo "Deleting agent..."
  letta-memory-cli agent delete --id "$AGENT_ID"
  echo "✅ Agent deleted"
else
  echo "❌ Agent not found"
fi

# 5. Verify
if letta-memory-cli agent list | grep -q "$AGENT_NAME"; then
  echo "❌ Deletion failed"
else
  echo "✅ Verified: agent removed"
fi
```

## Complete Automation Script

### Full Lifecycle Script
```bash
#!/bin/bash
# agent_lifecycle.sh

ACTION="$1"  # create, verify, backup, delete
AGENT_NAME="$2"

if [ -z "$ACTION" ] || [ -z "$AGENT_NAME" ]; then
  echo "Usage: $0 {create|verify|backup|delete} <agent_name>"
  exit 1
fi

case "$ACTION" in
  create)
    # Check if exists
    if letta-memory-cli agent list | grep -q "$AGENT_NAME"; then
      echo "Agent $AGENT_NAME already exists"
      exit 1
    fi
    
    # Create with defaults
    letta-memory-cli agent create \
      --name "$AGENT_NAME" \
      --persona "I am $AGENT_NAME, a specialized AI agent." \
      --human "User is a developer."
    
    # Verify
    bash "$0" verify "$AGENT_NAME"
    ;;
    
  verify)
    bash verify_agent.sh "$AGENT_NAME"
    ;;
    
  backup)
    bash backup_agent.sh "$AGENT_NAME"
    ;;
    
  delete)
    bash safe_delete_agent.sh "$AGENT_NAME"
    ;;
    
  *)
    echo "Unknown action: $ACTION"
    exit 1
    ;;
esac
```

## Best Practices

1. **Always Backup Before Major Changes**
2. **Verify After Each Phase**
3. **Document Agent Purpose**
4. **Regular Health Checks**
5. **Clean Up Old Context Memories**
6. **Update Blocks When Knowledge Changes**

## Troubleshooting

### Agent Won't Create
- Check server health: `letta-memory-cli health`
- Verify API key: `echo $LETTA_API_KEY`
- Check name availability: `letta-memory-cli agent list | grep name`

### Verification Fails
- Check blocks attached: `letta-memory-cli block list --agent name`
- Verify memories: `letta-memory-cli memory list --agent name`
- Test server: `letta-memory-cli stats --agent name`

### Backup Fails
- Check disk space: `df -h ~/backups`
- Verify permissions: `ls -la ~/backups`
- Try alternate path: `--path /tmp`

## Related Skills
- letta_agents - Detailed agent management
- letta_memory - Memory operations
- letta_blocks - Block management
- letta_backup - Backup and maintenance

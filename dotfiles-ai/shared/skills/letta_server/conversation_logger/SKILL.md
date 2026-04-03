---
name: conversation-logger
description: Save AI conversation logs to Letta server for persistent memory. Trigger at the end of EVERY conversation session to preserve context for future sessions. Also use when you need to save important decisions, action items, or project updates.
---

# Conversation Logger Skill

This skill enables AI agents to save conversation logs to the Letta server for cross-session memory persistence.

## Core Operations

### 1. Log Current Conversation (Mandatory End-of-Session)
At the end of every significant conversation, save it to Letta:

```bash
# From file (recommended)
python /home/cbwinslow/workspace/epstein/scripts/conversation_logger/cli.py log /path/to/conversation.md

# From stdin (for piping)
cat conversation.md | python /home/cbwinslow/workspace/epstein/scripts/conversation_logger/cli.py log -

# Without saving to Letta (local only)
python /home/cbwinslow/workspace/epstein/scripts/conversation_logger/cli.py log conversation.md --no-letta
```

### 2. Search Previous Conversations
When starting a task, search for relevant context:

```bash
# Search conversations
python /home/cbwinslow/workspace/epstein/scripts/conversation_logger/cli.py search "epstein project"

# Or directly with Letta CLI
letta archival-search agent-1167f15a-a10a-4595-b962-ec0f372aae0d "previous work on entity extraction"
```

### 3. Monitor for Conversation Files
Start a background watcher for automatic logging:

```bash
# Watch specific directories
python /home/cbwinslow/workspace/epstein/scripts/conversation_logger/cli.py watch --directories ~/workspace /tmp

# With custom patterns
python /home/cbwinslow/workspace/epstein/scripts/conversation_logger/cli.py watch --directories ~/projects --patterns "*.md" "*.txt" "*.log"
```

### 4. Export Conversations
Export conversations for backup or sharing:

```bash
# Export to JSON
python /home/cbwinslow/workspace/epstein/scripts/conversation_logger/cli.py export --format json --output ./exports

# Export to Markdown
python /home/cbwinslow/workspace/epstein/scripts/conversation_logger/cli.py export --format markdown --output ./exports
```

## When to Use This Skill

### Mandatory Triggers
1. **End of Session**: ALWAYS log the conversation before ending a session
2. **Major Decisions**: When significant decisions are made
3. **Problem Solved**: When a complex problem is resolved
4. **Project Updates**: When project status changes significantly

### Optional Triggers
1. **Knowledge Transfer**: When important information is discovered
2. **Code Changes**: When significant code changes are made
3. **Debugging Sessions**: When complex debugging is completed
4. **Planning Sessions**: When plans or strategies are developed

## Processing Logic (Internal)

When logging a conversation:

1. **Extract Metadata**:
   - Session ID (from file or generated)
   - Title (from first line or filename)
   - Timestamp (from content or current time)
   - Participants (User, Assistant, System)

2. **Identify Key Elements**:
   - Decisions (look for "decision:", "conclusion:", "we will")
   - Action items (look for checkboxes, "todo:", "action item:")
   - Questions (lines ending with "?")
   - Key points (bullet points, numbered lists)

3. **Save to Letta Server**:
   - Insert as archival memory with tags
   - Update agent persona if significant changes
   - Tag with session ID and topics

4. **Archive Locally**:
   - Save processed JSON to `~/.conversation_logger/archives/`
   - Track processed files to avoid duplicates

## Integration with Other Skills

### Letta Memory
- **Recall**: Use `letta archival-search` before starting tasks
- **Store**: Use conversation logger at end of tasks
- **Sync**: Memories are automatically synced to Letta server

### Project Tracking
- Log conversations about project progress
- Tag with project names (e.g., "epstein", "infra")
- Search by project when resuming work

### Knowledge Management
- Extract and tag key knowledge
- Link conversations to project documentation
- Build searchable knowledge base

## Troubleshooting

### Connection Issues
```bash
# Test Letta connection
python /home/cbwinslow/workspace/epstein/scripts/conversation_logger/cli.py test

# Check Letta server status
letta health
```

### No Conversations Logged
1. Check file patterns: `--patterns "*.md" "*.txt"`
2. Verify file contains conversation indicators
3. Check file size (must be >100 bytes)

### Large Files Not Processing
- Files >10MB are skipped by default
- Adjust `max_file_size` in config if needed

## Configuration

Config file: `~/.conversation_logger/config.yaml`

Key settings:
```yaml
letta:
  agent_id: "agent-1167f15a-a10a-4595-b962-ec0f372aae0d"
  agent_name: "coder"

monitoring:
  watch_directories: ["~/workspace", "/tmp"]
  file_patterns: ["*.md", "*.txt"]
  check_interval_seconds: 60
```

## Gemini CLI Logic (Internal)

1. **End of Every Session**: Log conversation to Letta
2. **Start of Complex Task**: Search Letta for previous context
3. **After Major Decision**: Update agent persona with decision
4. **Regular Check-ins**: Export backups periodically

## Multi-Agent Context

If a task spans multiple agents:
- Log conversation with primary agent ID
- Tag with all relevant agent names
- Use `letta archival-search` across agents for context

---

**Skill Version**: 1.0.0  
**Last Updated**: 2026-03-24  
**Integration**: Letta Server v0.16.6
---
name: conversation-logger
version: "1.0.0"
description: "Automatically log all AI agent conversations to Letta archival memory with cross-agent sharing and session resume capabilities"
category: productivity
agents: [claude, cline, codex, windsurf, kilocode, opencode, openclaw, gemini]
tags: [letta, logging, conversation, memory, session-tracking]
triggers:
  - SESSION_START
  - SESSION_END
  - INTERACTION_COMPLETE
---

# Universal Conversation Logger Workflow

## Overview

This workflow automatically captures every interaction between you and AI agents, storing them in Letta's archival memory. This enables:
- **Session Resume**: Pick up where you left off across any agent
- **Cross-Agent Sharing**: Windsurf can see what you discussed with Claude
- **Conversation Search**: Find past discussions and solutions
- **Audit Trail**: Complete history of your AI-assisted work

## How It Works

### Automatic Logging
```
Every Prompt → Logged to Letta
Every Response → Logged to Letta
Tool Calls → Logged with results
Session Metadata → Timestamps, agent name, context
```

### Storage Architecture
- **Local Backup**: JSONL files in `~/dotfiles/ai/logs/`
- **Letta Archival**: Vector-searchable long-term storage
- **Cross-Agent**: All agents share the same memory pool

## Workflow Triggers

### 1. SESSION_START
```
TRIGGER: When agent initializes or receives first prompt
ACTION:
  - Generate unique session ID
  - Log session start timestamp
  - Record agent name and version
  - Check for previous related sessions
  - Search Letta for relevant context from past sessions
```

### 2. INTERACTION_COMPLETE
```
TRIGGER: After each prompt-response pair
ACTION:
  - Log user prompt
  - Log agent response (truncated if very long)
  - Record tool calls and results
  - Save to both local JSONL and Letta
  - Tag with session ID and context
```

### 3. SESSION_END
```
TRIGGER: When agent exits or after period of inactivity
ACTION:
  - Generate session summary
  - Log end timestamp
  - Calculate session duration
  - Save summary to Letta
  - Update session index
```

## Usage Examples

### Example 1: Session Resume
```markdown
User: "Continue working on the Docker setup from yesterday"

Agent Action:
1. Search Letta: "Docker setup sessions"
2. Find: Session #1234 - "Docker compose for PostgreSQL"
3. Recall: Previous configuration, issues encountered
4. Resume: "I see yesterday we were setting up Docker compose with 
           PostgreSQL and had an SSL configuration issue. 
           Let's continue from there..."
```

### Example 2: Cross-Agent Context
```markdown
User (in Windsurf): "How do I fix this TypeScript error?"

Agent Action:
1. Search Letta: "TypeScript error fixes"
2. Find: Previous session with Claude Code about similar error
3. Apply: "Based on your conversation with Claude Code yesterday,
           this looks like the same interface issue we solved.
           The fix was to add the 'strictNullChecks' option..."
```

### Example 3: Finding Past Solutions
```markdown
User: "What was that npm package I used for PDF generation?"

Agent Action:
1. Search Letta: "npm package PDF generation"
2. Find: Session from 3 days ago mentioning "pdf-lib" and "puppeteer"
3. Answer: "You were evaluating pdf-lib vs puppeteer for PDF generation.
           You chose pdf-lib because it's lighter weight."
```

## Implementation Commands

### Shell Integration
Add to your `.bashrc` or `.zshrc`:
```bash
# Auto-load conversation logger for terminal agents
export CONVERSATION_LOGGER_ENABLED=true
export LETTA_SERVER_URL="http://localhost:8283"

# Optional: Custom log directory
export AI_LOGS_DIR="${HOME}/dotfiles/ai/logs"
```

### Manual Logging
```bash
# Start a named session
letta-session-start "Docker Configuration Task"

# Log a specific interaction
letta-log "User asked about React hooks" "Explained useEffect vs useLayoutEffect"

# End session with summary
letta-session-end "Successfully configured Docker compose with hot reload"
```

### Python API
```python
from letta_integration import ConversationLogger

# Initialize logger
logger = ConversationLogger(agent_name="windsurf")

# Start session
session_id = logger.start_conversation(
    context="Working on TypeScript migration",
    tags=["typescript", "migration", "project-alpha"]
)

# Log interactions
logger.log_interaction(
    prompt="How do I convert this JS file to TS?",
    response="You need to add type annotations for the props...",
    tool_calls=["search_code", "read_file"]
)

# End session
logger.end_conversation(
    summary="Migrated 3 files to TypeScript, identified 2 type issues"
)

# Search past conversations
results = logger.search_archival("TypeScript migration issues")
```

## Configuration Options

### Environment Variables
```bash
# Required
export LETTA_SERVER_URL="http://localhost:8283"

# Optional
export CONVERSATION_LOGGER_ENABLED=true        # Enable/disable
export AI_LOGS_DIR="~/dotfiles/ai/logs"      # Local backup path
export SESSION_TIMEOUT=3600                    # Auto-end after 1 hour
export MAX_RESPONSE_LENGTH=10000              # Truncate long responses
```

### Per-Agent Configuration
```json
{
  "claude": {
    "log_level": "verbose",
    "auto_resume": true
  },
  "windsurf": {
    "log_level": "standard",
    "auto_resume": false
  }
}
```

## Privacy & Security

### What Gets Logged
✅ User prompts and questions  
✅ Agent responses and code  
✅ Tool calls and results  
✅ File paths and project structure  
✅ Error messages and stack traces  

### What Doesn't Get Logged
❌ File contents (unless explicitly shared)  
❌ Environment variables and secrets  
❌ Passwords or API keys  
❌ External API responses (unless requested)  

### Data Retention
- **Local logs**: Kept indefinitely (rotate manually)
- **Letta archival**: Configurable retention (default: permanent)
- **Session metadata**: Always retained for searchability

## Troubleshooting

### Issue: Conversations not appearing in search
**Solution**: 
1. Verify Letta server is running: `curl http://localhost:8283/health`
2. Check agent has correct agent_id configured
3. Ensure `letta-integration` skill is loaded

### Issue: Sessions not resuming
**Solution**:
1. Check session IDs are being generated uniquely
2. Verify `SESSION_START` trigger is firing
3. Search for partial session matches as fallback

### Issue: Local logs not being created
**Solution**:
1. Check `AI_LOGS_DIR` directory exists and is writable
2. Verify directory permissions: `ls -la ~/dotfiles/ai/logs/`
3. Check disk space available

## Integration with Other Skills

### + Memory-Assisted Coding
```
Conversation Logger captures the discussion
↓
Memory Manager extracts solutions
↓
Solutions saved to archival memory
↓
Future sessions recall both conversation AND solution
```

### + Cross-Agent Memory
```
Claude Code logs session about API design
↓
Windsurf searches for "API design" context
↓
Finds Claude's session, continues the discussion
↓
Both agents share the same conversation history
```

## Best Practices

1. **Name Your Sessions**: Use descriptive context strings
   - Good: "React performance optimization - dashboard"
   - Bad: "Working on code"

2. **Use Consistent Tags**: Makes searching easier
   - Project-based: `project-alpha`, `dotfiles-refactor`
   - Tech-based: `react`, `postgresql`, `docker`
   - Type-based: `bugfix`, `feature`, `research`

3. **Review Regularly**: Search for "TODO" or "FIXME" in conversations

4. **Clean Up Old Sessions**: Archive or delete ancient sessions

5. **Export Important Sessions**: Save critical conversations separately
   ```bash
   letta-export-session <session_id> > important-session.md
   ```

## Advanced Features

### Conversation Analytics
```python
from letta_integration import ConversationAnalytics

analytics = ConversationAnalytics()

# Get conversation statistics
stats = analytics.get_session_stats(
    start_date="2026-03-01",
    end_date="2026-03-28"
)

print(f"Total sessions: {stats.total_sessions}")
print(f"Average duration: {stats.avg_duration}")
print(f"Most active agent: {stats.most_active_agent}")
print(f"Common topics: {stats.top_tags}")
```

### Automated Summaries
Enable automatic session summarization:
```bash
export AUTO_SUMMARIZE=true
export SUMMARY_MODEL="claude-3-haiku"  # Lightweight model for summaries
```

### Conversation Branching
When a session diverges into multiple topics:
```python
# Create sub-session for new topic
sub_session = logger.branch_session(
    parent_session_id="original-123",
    new_context="Database optimization (branched from API design)"
)
```

---

**Workflow Version**: 1.0.0  
**Requires**: letta-integration skill v2.0+  
**Compatible Agents**: All agents with shell/python access

# Conversation Logger Skill (Letta)

Log all AI agent conversations to Letta memory system.

**Version**: 2.0.0  
**Location**: `~/dotfiles/ai/shared/scripts/universal_conversation_logger.py`

## Quick Start

```python
from universal_conversation_logger import SimpleConversationLogger

logger = SimpleConversationLogger(agent_name="windsurf", tool="windsurf")
session_id = logger.start_conversation()
logger.log_interaction("Hello", "Hi there!")
logger.end_conversation(summary="Greeting completed")
```

## Features

- Stores conversations in Letta (not local files)
- Cross-agent search: any agent can find any conversation
- Session tracking with unique IDs
- Simple 3-method API: start, log, end

## API

### Start
```python
session_id = logger.start_conversation(metadata={"task": "coding"})
```

### Log
```python
logger.log_interaction(
    user_input="User message",
    agent_response="Agent response",
    context={"files": ["main.py"]}  # optional
)
```

### End
```python
logger.end_conversation(summary="What was accomplished")
```

### Search
```python
# Search this agent's conversations
results = logger.search_conversations("database schema")

# Search ALL agents
from universal_conversation_logger import search_all_conversations
results = search_all_conversations("GPU models")
```

## How It Works

1. **Start**: Saves context memory with session ID
2. **Log**: Saves to archival memory with tags
3. **End**: Saves summary to archival memory
4. **Search**: Uses Letta's vector search

All data goes to Letta. No local files.

## Tags

Conversations are auto-tagged:
- `conversation`, `interaction`
- `session_start`, `session_end`
- `{agent_name}` (windsurf, claude, etc.)
- `{tool}` (windsurf, vscode, openclaw)
- `session_{id}`, `YYYY-MM-DD`

## Cross-Agent Example

```python
# Windsurf does work
windsurf = SimpleConversationLogger("windsurf", "windsurf")
windsurf.start_conversation()
windsurf.log_interaction("Design DB", "Here's the schema...")
windsurf.end_conversation("DB designed")

# Claude searches and continues
claude = SimpleConversationLogger("claude", "claude")
results = claude.search_conversations("database schema")
# Finds Windsurf's conversation automatically
```

## One-Shot Logging

```python
from universal_conversation_logger import log_conversation

log_conversation(
    agent_name="windsurf",
    tool="windsurf", 
    user_input="Hello",
    agent_response="Hi!"
)
```

### 2. Shell Integration

```bash
# Add to ~/.bashrc or ~/.zshrc:
source ~/dotfiles/ai/shared/scripts/shell_conversation_logger.sh

# Use the commands:
ai-search "GPU models"           # Search conversations
ai-resume "session_id_abc123"  # Resume a conversation
ai-log windsurf "Hello" "Hi"     # Log an interaction
```

### 3. Cross-Agent Search

```python
# Search conversations from ALL agents
results = logger.search_related_conversations("configure system", limit=5)

for result in results:
    print(f"[{result['agent']}] {result['content'][:100]}...")
```

---

## Core Operations

### Conversation Lifecycle

```python
from universal_conversation_logger import ConversationLogger

logger = ConversationLogger(agent_name="windsurf")

# 1. START - Creates unique session ID
session_id = logger.start_conversation(
    tool="windsurf",
    metadata={"task": "configuration", "priority": "high"}
)

# 2. LOG - Each interaction (automatic)
logger.log_interaction(
    user_input="User's question or command",
    agent_response="AI's response",
    tool="windsurf",
    context={"files": ["/path/to/file"], "commands": ["command"]}
)

# 3. END - Save conversation summary
result = logger.end_conversation(
    summary="Brief summary of what was accomplished"
)
```

### Cross-Agent Conversation Resume

```python
# Find a previous conversation
results = logger.search_related_conversations("GPU model picker")

if results:
    # Get session ID from first result
    session_id = results[0].get('session_id')
    
    # Resume that conversation
    logger.resume_conversation(session_id)
    
    # Get context to continue
    context = logger.get_conversation_context(max_entries=5)
    print(f"Continuing from previous context:\n{context}")
```

---

## Supported AI Agents

| Agent/Tool | Integration Method | Status |
|------------|-------------------|--------|
| **Windsurf** | Python import | ✅ Ready |
| **VSCode AI** | Python import | ✅ Ready |
| **OpenClaw** | Shell wrapper | ✅ Ready |
| **Claude** | Python import | ✅ Ready |
| **Cline** | Python import | ✅ Ready |
| **Codex** | Python import | ✅ Ready |
| **Terminal AI** | Shell functions | ✅ Ready |

---

## Advanced Features

### 1. Automatic Entity Extraction

Conversations automatically extract:
- File paths
- Commands executed
- URLs mentioned
- Code blocks
- Decisions made

```python
# Entities are automatically extracted and stored
logger.log_interaction(
    user_input="Check /etc/config and run `systemctl restart`",
    agent_response="Configuration checked and service restarted",
    tool="openclaw"
)
# Automatically extracts: /etc/config, systemctl restart
```

### 2. Conversation Context Retrieval

```python
# Get recent conversation context
context = logger.get_conversation_context(max_entries=10)

# Use context in responses
response = f"Based on our previous conversation:\n{context}\n\nHere's what I found..."
```

### 3. Session Management

```python
# Check current session
if logger.current_session:
    print(f"Active session: {logger.current_session.session_id}")
    print(f"Entries: {len(logger.current_session.entries)}")
    print(f"Duration: {logger._calculate_duration()}")
```

---

## Configuration

### Environment Variables

```bash
# Letta server connection
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_API_KEY="your-api-key"

# Logging options
export CONVERSATION_LOG_LEVEL="standard"  # minimal, standard, full
export CONVERSATION_LOG_DIR="~/dotfiles/ai/logs/conversations"
```

### Python Configuration

```python
logger = ConversationLogger(
    agent_name="windsurf",
    server_url="http://localhost:8283",
    api_key="your-key",
    log_level="full"  # minimal, standard, full
)
```

---

## Shell Integration

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ai-search <query>` | Search all conversations | `ai-search "GPU models"` |
| `ai-resume <id>` | Resume a conversation | `ai-resume "abc123"` |
| `ai-log <tool> <input> <response>` | Log an interaction | `ai-log windsurf "Hi" "Hello"` |
| `ai-openclaw <input>` | Run OpenClaw with logging | `ai-openclaw "configure system"` |
| `ai-windsurf <input>` | Run Windsurf with logging | `ai-windsurf "help"` |

### Wrapper Functions

```bash
# Wrap any AI command with logging
with_conversation_logging windsurf "windsurf --help"

# Create custom wrappers
my_ai_tool() {
    local input="$1"
    local output=$(actual_ai_tool "$input")
    log_ai_interaction "my_tool" "$input" "$output"
    echo "$output"
}
```

---

## Integration Examples

### Windsurf IDE Integration

```python
# In Windsurf's AI handler:
import sys
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')
from universal_conversation_logger import ConversationLogger

class WindsurfAI:
    def __init__(self):
        self.logger = ConversationLogger(agent_name="windsurf")
        self.logger.start_conversation(tool="windsurf")
    
    def handle_request(self, user_input):
        # Check for related conversations
        related = self.logger.search_related_conversations(user_input)
        if related:
            context = self.logger.get_conversation_context()
            # Include context in processing
        
        # Generate response
        response = self.generate_response(user_input)
        
        # Log interaction
        self.logger.log_interaction(
            user_input=user_input,
            agent_response=response,
            tool="windsurf"
        )
        
        return response
    
    def cleanup(self):
        self.logger.end_conversation()
```

### OpenClaw Terminal Integration

```python
#!/usr/bin/env python3
# Wrapper for OpenClaw with logging

import sys
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')
from universal_conversation_logger import log_shell_interaction

# Get user input
user_input = sys.argv[1] if len(sys.argv) > 1 else ""

# Call actual OpenClaw
import subprocess
result = subprocess.run(
    ["openclaw", "original", user_input],
    capture_output=True,
    text=True
)
response = result.stdout

# Log the interaction
log_shell_interaction(
    user_input=user_input,
    agent_response=response,
    tool="openclaw",
    agent_name="openclaw"
)

print(response)
```

### VSCode AI Integration

```python
# In VSCode extension:
import sys
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')
from universal_conversation_logger import ConversationLogger

class VSCodeAIHandler:
    def __init__(self):
        self.logger = ConversationLogger(agent_name="vscode")
        self.session_id = self.logger.start_conversation(tool="vscode")
    
    def on_user_message(self, message):
        # Search for context from other agents
        context = self.logger.search_related_conversations(message[:50])
        
        # Generate response with context
        response = self.generate_ai_response(message, context)
        
        # Log the interaction
        self.logger.log_interaction(
            user_input=message,
            agent_response=response,
            tool="vscode"
        )
        
        return response
```

---

## Best Practices

### 1. Always Start with Context

```python
# Before responding, check for previous conversations
related = logger.search_related_conversations(user_input)
if related:
    # Acknowledge previous work
    response = f"I see we discussed this before. Continuing from where we left off..."
```

### 2. Use Consistent Tool Names

```python
# Use the same tool name across sessions
logger.start_conversation(tool="windsurf")  # Not "Windsurf" or "WINDSURF"
```

### 3. Include Rich Context

```python
logger.log_interaction(
    user_input=user_input,
    agent_response=response,
    tool="windsurf",
    context={
        "files_modified": ["/path/to/file.py"],
        "commands_executed": ["pip install package"],
        "decisions_made": ["Used Approach A over B"],
        "errors_encountered": []
    }
)
```

### 4. End Conversations Properly

```python
# Always end with a summary
logger.end_conversation(
    summary="Configured GPU models with llama.cpp, tested embeddings with bge-m3"
)
```

---

## API Reference

### ConversationLogger Class

```python
class ConversationLogger:
    def __init__(self, agent_name, server_url=None, api_key=None, log_level="standard")
    def start_conversation(self, tool=None, metadata=None) -> str
    def log_interaction(self, user_input, agent_response, tool=None, context=None) -> ConversationEntry
    def end_conversation(self, summary=None) -> Dict
    def search_related_conversations(self, query, limit=5) -> List[Dict]
    def resume_conversation(self, session_id) -> Optional[ConversationSession]
    def get_conversation_context(self, max_entries=10) -> str
```

### Convenience Functions

```python
def log_shell_interaction(user_input, agent_response, tool, agent_name)
def search_conversations(query) -> List[Dict]
def resume_any_conversation(session_id, agent_name) -> bool
```

---

## Troubleshooting

### Common Issues

1. **Letta server not connected**
   ```bash
   curl http://localhost:8283/health
   ```

2. **Import errors**
   ```python
   import sys
   sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')
   ```

3. **No memories found**
   - Check agent name consistency
   - Verify Letta server is running
   - Check API key configuration

### Debug Commands

```bash
# Test the logger
python3 -c "from universal_conversation_logger import ConversationLogger; print('OK')"

# Check Letta connection
curl http://localhost:8283/v1/agents

# View local logs
cat ~/dotfiles/ai/logs/conversations/windsurf_*.jsonl
```

---

## Examples

### Example 1: Multi-Agent Collaboration

```python
# Agent 1 (Windsurf) starts work
windsurf = ConversationLogger(agent_name="windsurf")
sid = windsurf.start_conversation(tool="windsurf")
windsurf.log_interaction("Design the database schema", "Here's the schema...", tool="windsurf")

# Agent 2 (Claude) continues the work
claude = ConversationLogger(agent_name="claude")
# Search for related work
related = claude.search_related_conversations("database schema")
if related:
    claude.resume_conversation(related[0]['session_id'])
    claude.log_interaction("Implement the schema", "Schema implemented...", tool="claude")
```

### Example 2: Long-Running Task Resume

```python
# Start a long task
logger = ConversationLogger(agent_name="windsurf")
session_id = logger.start_conversation(tool="windsurf")
logger.log_interaction("Step 1", "Completed step 1", tool="windsurf")

# ... system restart ...

# Resume the task
new_logger = ConversationLogger(agent_name="windsurf")
new_logger.resume_conversation(session_id)
context = new_logger.get_conversation_context()
new_logger.log_interaction("Step 2", "Continuing from: " + context, tool="windsurf")
```

### Example 3: Search and Reference

```python
# Search for previous GPU configurations
results = logger.search_related_conversations("GPU model picker")

if results:
    print("I found previous work on GPU configuration:")
    for r in results[:3]:
        print(f"  - {r['content'][:100]}...")
    
    # Reference the previous work
    logger.log_interaction(
        user_input="Configure GPU models",
        agent_response=f"Based on our previous work ({results[0]['timestamp']}), I'll use the same configuration...",
        tool="windsurf"
    )
```

---

## Version History

- **1.0.0** (2026-03-28): Initial release
  - Automatic conversation logging
  - Cross-agent search and resume
  - Shell integration
  - Local file backup

---

## See Also

- `letta_model_picker/SKILL.md` - GPU model configuration
- `memory/SKILL.md` - Core memory management
- `~/dotfiles/ai/shared/scripts/session_memory_logger.py` - Session memory creation

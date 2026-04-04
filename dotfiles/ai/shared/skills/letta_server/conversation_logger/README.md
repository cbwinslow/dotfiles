# Conversation Logger - Epstein Project

A comprehensive system for capturing, processing, and saving AI conversation logs to the Letta server for persistent memory across sessions.

## Overview

This system provides:
1. **Automatic conversation capture** - Monitor directories for conversation files
2. **Intelligent processing** - Extract key decisions, action items, and topics
3. **Letta server integration** - Save to self-hosted Letta server for memory persistence
4. **Local archiving** - Keep backup copies of all conversations
5. **Search capability** - Find previous conversations by topic or content

## Quick Start

### 1. Log a Conversation from File
```bash
python /home/cbwinslow/workspace/epstein/scripts/log_conversation.py /path/to/conversation.md
```

### 2. Log from Stdin
```bash
cat conversation.md | python /home/cbwinslow/workspace/epstein/scripts/log_conversation.py -
```

### 3. Start Watching for Conversations
```bash
python /home/cbwinslow/workspace/epstein/scripts/log_conversation.py --watch
```

### 4. Test Letta Connection
```bash
python /home/cbwinslow/workspace/epstein/scripts/log_conversation.py --test
```

## Architecture

### Components

1. **ConversationLogger** (`logger.py`)
   - Main orchestrator
   - Manages logging workflow
   - Coordinates between processor and Letta client

2. **ConversationProcessor** (`processor.py`)
   - Extracts metadata from conversations
   - Identifies key decisions and action items
   - Generates summaries and extracts topics

3. **LettaClient** (`letta_client.py`)
   - Interfaces with Letta server CLI
   - Manages memory insertion and search
   - Handles agent updates

4. **Config** (`config.py`)
   - Manages configuration from YAML files
   - Supports environment variable overrides
   - Provides default settings

### Data Flow

```
Conversation File → Processor → Extracted Data → LettaClient → Letta Server
                    ↓
              Local Archive (JSON)
```

## Skill Integration

This system is implemented as a **skill** for AI agents. The skill definition is in `SKILL.md`.

### When to Use
- **End of every session**: Log the conversation
- **After major decisions**: Save key decisions
- **Problem solving**: Document solutions
- **Project updates**: Track progress

### Usage by AI Agents
```bash
# Log current conversation
python /path/to/log_conversation.py /path/to/conversation.md

# Search previous context
letta archival-search agent-1167f15a-a10a-4595-b962-ec0f372aae0d "previous work on entity extraction"
```

## Configuration

Configuration file location: `~/.conversation_logger/config.yaml`

Example configuration:
```yaml
letta:
  server_url: "http://localhost:8283"
  agent_id: "agent-1167f15a-a10a-4595-b962-ec0f372aae0d"
  agent_name: "coder"

monitoring:
  watch_directories: ["~/workspace", "/tmp"]
  file_patterns: ["*.md", "*.txt"]
  check_interval_seconds: 60
```

## Features

### Conversation Processing
- Extracts session ID from content
- Identifies participants (User, Assistant, System)
- Extracts key points from bullet lists
- Identifies decisions using keywords
- Finds action items (checkboxes, todo items)
- Extracts questions
- Identifies main topics
- Generates concise summaries

### Letta Server Integration
- Stores conversations as archival memory
- Tags with relevant keywords (session ID, topics, dates)
- Updates agent persona with recent activity
- Searches previous conversations by semantic similarity
- Maintains conversation history across sessions

### File Monitoring
- Watches directories for new conversation files
- Configurable file patterns
- Automatic processing of new files
- Prevents duplicate processing
- Configurable check intervals

## Integration with Epstein Project

### Memory System Integration
- **Custom Letta memory** (`scripts/letta_memory.py`): Project-specific memories
- **Letta server** (Docker): Persistent cross-session memory
- Both systems work together for comprehensive memory management

### Current Memories in Letta Server
- Project overview and technical architecture
- Processing status updates (NER extraction, text content)
- Conversation logs from planning sessions
- Verification procedures and results

### Search Examples
```bash
# Search for project overview
letta archival-search agent-1167f15a-a10a-4595-b962-ec0f372aae0d "project overview"

# Search for NER progress
letta archival-search agent-1167f15a-a10a-4595-b962-ec0f372aae0d "NER extraction progress"

# Search for conversation logs
letta archival-search agent-1167f15a-a10a-4595-b962-ec0f372aae0d "session conversation"
```

## Testing

### Run Tests
```bash
# Test Letta connection
python /home/cbwinslow/workspace/epstein/scripts/log_conversation.py --test

# Test with sample conversation
echo "## User: Test conversation\n## Assistant: This is a test." | python /home/cbwinslow/workspace/epstein/scripts/log_conversation.py -

# Check statistics
python /home/cbwinslow/workspace/epstein/scripts/log_conversation.py --stats
```

### Expected Output
```
✅ Letta server is connected!
✅ Memory insertion successful!
✅ Conversation logged successfully!
```

## Troubleshooting

### "Cannot connect to Letta server"
```bash
# Check server status
letta health

# Restart server if needed
cd /home/cbwinslow/infra/letta
./deploy_letta_server.sh
```

### "Module not found" errors
```bash
# Run from correct directory
cd /home/cbwinslow/workspace/epstein

# Or use absolute path
/home/cbwinslow/workspace/epstein/.venv/bin/python scripts/log_conversation.py
```

### "No conversations logged"
1. Check file patterns in config
2. Verify file contains conversation indicators
3. Check file size (must be >100 bytes)
4. Look for errors in log file: `~/.conversation_logger/conversation_logger.log`

## Files

```
scripts/conversation_logger/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point for -m execution
├── cli.py                # Command-line interface
├── config.py             # Configuration management
├── letta_client.py       # Letta server interface
├── logger.py             # Main logger orchestrator
├── processor.py          # Conversation processing
├── SKILL.md              # Skill definition for AI agents
├── README.md             # This file
└── config/
    └── config.example.yaml  # Example configuration

scripts/
└── log_conversation.py   # Simple wrapper for easy access
```

## Dependencies

- Python 3.8+
- PyYAML (for configuration)
- Letta CLI (for server communication)

## Version History

- **1.0.0** (2026-03-24): Initial release
  - Core conversation logging functionality
  - Letta server integration
  - File monitoring and watching
  - Skill definition for AI agents
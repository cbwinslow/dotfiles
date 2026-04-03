# Letta Integration Package

Comprehensive Letta server integration for AI agents.

## Features

- **Automatic Conversation Saving**: All conversations automatically stored in Letta
- **Persistent Storage**: All agent data is automatically persisted via Agent Memory
- **Memory Management**: Full CRUD operations for all memory types
- **Entity Extraction**: Automatic extraction and storage of entities
- **Cross-Agent Search**: Search memories across all agents
- **Server Health Monitoring**: Monitor Letta server status
- **Backup Operations**: Backup memories to file/PostgreSQL

## Installation

```bash
cd /home/cbwinslow/dotfiles/ai/packages/letta_integration
pip install -e .
```

## Environment Variables

```bash
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_API_KEY="your-api-key"
```

## Usage

### Python API

```python
from letta_integration import LettaIntegration

# Initialize
letta = LettaIntegration(
    server_url="http://localhost:8283",
    api_key="your-api-key",
    agent_name="my_agent"
)

# Save conversation
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
]
result = letta.save_conversation(messages, tags=["greeting"])

# Search memories
results = letta.search_memories("agent configuration", limit=10)

# Check server health
health = letta.check_server_health()

# Get memory stats
stats = letta.get_memory_stats()
```

### CLI

```bash
# Save conversation
letta-memory-cli save --type conversation --content "Hello, world!"

# Search memories
letta-memory-cli search --query "entity extraction"

# Get statistics
letta-memory-cli stats

# Check health
letta-memory-cli health

# Backup memories
letta-memory-cli backup

# List agents
letta-memory-cli list agents

# List memories
letta-memory-cli list memories --limit 50
```

## Memory Types

- **core**: Permanent knowledge (never expires)
- **archival**: Long-term storage (365 days)
- **context**: Session context (30 days)
- **persona**: Agent personality (never expires)
- **human**: User preferences (never expires)

## Auto-Save Features

The integration automatically:
- Saves all conversations
- Extracts entities (code, files, URLs, commands)
- Creates memories from decisions
- Creates memories from action items
- Backs up to PostgreSQL (via Agent Memory)

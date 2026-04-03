---
name: "Letta Self-Hosted Integration"
description: "Complete Letta integration using official letta-client SDK. Supports agent management, memory blocks, shared memory, archival memory, MCP tools, and agent file operations."
version: "2.0.0"
category: "memory"
tags: ["letta", "memory", "agents", "sdk", "self-hosted"]
agents: ["all"]
---

# Letta Self-Hosted Integration Skill

## Overview
Complete Letta integration for self-hosted deployment using the official `letta-client` SDK. Supports all Letta features including memory blocks, archival memory, multi-agent shared memory, MCP tools, and agent file operations.

**Location**: `~/dotfiles/ai/packages/letta_integration/`
**Server**: Self-hosted at `http://localhost:8283`
**Database**: Bare metal PostgreSQL with pgvector

## Installation

```bash
pip install letta-client
```

## Auto-Loading for Terminal AI Agents

The Letta skill auto-loads for all terminal AI agents. Add to your `~/.bashrc`:

```bash
source ~/dotfiles/ai/skills/letta_integration/shell_loader.sh
```

Or run the setup script:
```bash
bash ~/dotfiles/ai/skills/letta_integration/setup.sh
```

### Available Aliases (Auto-loaded)

```bash
letta-health     # Check server status
letta-agents     # List all agents  
init_letta_agent # Initialize any agent
letta-log        # Log conversation
```

### Quick Agent Initialization

Any AI agent can auto-initialize:

```bash
# For Windsurf
source ~/dotfiles/ai/skills/letta_integration/shell_loader.sh
init_letta_agent windsurf

# For Claude
init_letta_agent claude

# For OpenClaw
init_letta_agent openclaw
```

### Python Auto-Load

Python scripts auto-load the integration:

```python
# Any Python script can:
from agent_initializer import init_letta_for_agent

letta = init_letta_for_agent("windsurf")
# Agent is created and ready to use
```

### Environment Variables

Set in your shell:

```bash
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_DEFAULT_MODEL="letta/letta-free"
export LETTA_DEFAULT_EMBEDDING="ollama/bge-m3:latest"
```

## Quick Start

```python
from letta_integration import LettaIntegration

# Initialize for self-hosted server
letta = LettaIntegration(
    agent_name="my_agent",
    server_url="http://localhost:8283"
)

# Check server health
health = letta.check_server_health()
print(f"Server: {health['status']}")
```

## Features

### 1. Agent Management

Create and manage AI agents with memory and configuration:

```python
# Create basic agent
agent = letta.create_agent_with_memory_blocks(
    agent_name="windsurf",
    memory_blocks=[
        {"label": "persona", "value": "I am a helpful coding assistant"},
        {"label": "human", "value": "User is a developer"}
    ]
)

# List all agents
agents = letta.list_agents()
for agent in agents:
    print(f"{agent.name}: {agent.id}")

# Get specific agent
agent = letta.get_agent(agent_id)

# Delete agent
letta.delete_agent(agent_id)
```

### 2. Memory Blocks

Persistent, editable memory sections in the agent's context window:

```python
# Update memory block
letta.update_memory_block(
    label="human",
    value="User prefers Python and likes clean code"
)

# Retrieve memory block
block = letta.get_memory_block("human")
print(block.value)

# List all blocks for agent
blocks = letta.list_memory_blocks()
```

**Standard Block Labels:**
- `persona` - Agent's personality and role
- `human` - User information and preferences
- `conversation_log` - Conversation history
- `custom blocks` - Any label you define

### 3. Multi-Agent Shared Memory

Share memory blocks across multiple agents:

```python
# Create shared block
shared = letta.create_shared_block(
    label="team_context",
    value="Project: AI agent system. Deadline: End of month."
)

# Attach to multiple agents
letta.attach_shared_block(shared.id)  # Agent 1
letta2.attach_shared_block(shared.id)  # Agent 2

# Detach when needed
letta.detach_shared_block(shared.id)
```

### 4. Archival Memory (Searchable)

Long-term searchable storage using vector similarity:

```python
# Save to archival memory
letta.save_to_archival(
    text="Important decision: Using Letta for memory management",
    tags=["decision", "architecture", "2024-03"]
)

# Search archival memory
results = letta.search_archival(
    query="memory management decisions",
    limit=10
)

# Get all archival entries
all_memories = letta.get_archival_memory()
```

### 5. Messages and Streaming

Send messages to agents with optional streaming:

```python
# Send message
response = letta.send_message("Hello, how are you?")
for message in response.messages:
    print(message.content)

# Streaming (real-time response)
stream = letta.send_message_streaming("Tell me a story")
for chunk in stream:
    print(chunk.content, end="")

# Get message history
history = letta.get_message_history(limit=50)
```

### 6. Agent File Operations (.af)

Export and import agents:

```python
# Export agent to file
letta.export_agent_to_file(
    filepath="/path/to/agent.af",
    agent_id="agent-123"
)

# Import agent from file
imported = letta.import_agent_from_file(
    filepath="/path/to/agent.af",
    agent_name="restored_agent"
)
```

### 7. MCP Tools

Connect external tools via Model Context Protocol:

```python
# Create MCP server connection
server = letta.create_mcp_server(
    server_name="weather",
    server_url="https://weather-api.example.com/mcp"
)

# List available tools
tools = letta.list_mcp_tools(server.id)

# Attach tool to agent
letta.attach_mcp_tool_to_agent(tools[0].id)
```

### 8. Sleep-Time Agents

Enable background processing agents:

```python
agent = letta.create_agent(
    agent_name="background_processor",
    enable_sleeptime=True  # Creates sleep-time agent
)
```

## Environment Variables

```bash
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_DEFAULT_MODEL="letta/letta-free"
export LETTA_DEFAULT_EMBEDDING="ollama/bge-m3:latest"
export LETTA_API_KEY=""  # Optional for self-hosted
```

## Complete API Reference

### LettaIntegration Class

#### Initialization
```python
LettaIntegration(
    server_url: str = "http://localhost:8283",
    api_key: str = None,
    agent_name: str = "default_agent"
)
```

#### Agent Management
- `create_agent()` - Create new agent with full config
- `create_agent_with_memory_blocks()` - Create with memory blocks
- `list_agents()` - List all agents
- `get_agent(agent_id)` - Get specific agent
- `delete_agent(agent_id)` - Delete agent
- `get_or_create_agent(name)` - Get or create

#### Memory Blocks
- `update_memory_block(label, value, agent_id)` - Update block
- `get_memory_block(label, agent_id)` - Retrieve block
- `list_memory_blocks(agent_id)` - List all blocks

#### Shared Memory
- `create_shared_block(label, value)` - Create shared block
- `attach_shared_block(block_id, agent_id)` - Attach to agent
- `detach_shared_block(block_id, agent_id)` - Detach from agent

#### Archival Memory
- `save_to_archival(text, tags, agent_id)` - Save to long-term
- `search_archival(query, limit, agent_id)` - Vector search
- `get_archival_memory(agent_id)` - List all archival

#### Messages
- `send_message(message, agent_id)` - Send and get response
- `send_message_streaming(message, agent_id)` - Real-time streaming
- `get_message_history(limit, agent_id)` - Get past messages

#### Agent Files
- `export_agent_to_file(filepath, agent_id)` - Export .af file
- `import_agent_from_file(filepath, name)` - Import .af file

#### MCP Tools
- `create_mcp_server(name, url, type)` - Connect external server
- `list_mcp_tools(server_id)` - List available tools
- `attach_mcp_tool_to_agent(tool_id, agent_id)` - Enable tool

#### Utilities
- `check_server_health()` - Verify server status

## Testing

Run comprehensive tests:

```bash
cd ~/dotfiles/ai/packages/letta_integration
python3 test_all_features.py
```

Tests cover:
- Server connection
- Agent creation
- Memory block operations
- Shared memory
- Archival memory
- Agent listing

## Usage Examples

### Basic Agent Conversation

```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="chatbot")

# Create agent with personality
agent = letta.create_agent_with_memory_blocks(
    agent_name="chatbot",
    memory_blocks=[
        {"label": "persona", "value": "Friendly and helpful assistant"},
        {"label": "human", "value": "User's name is Alex"}
    ]
)

# Send message
response = letta.send_message("What's my name?")
print(response)
```

### Cross-Agent Memory Sharing

```python
# Create shared context
shared = letta.create_shared_block(
    label="project_info",
    value="Building AI agent system with Letta"
)

# Share with multiple agents
for agent_name in ["coder", "reviewer", "documenter"]:
    letta = LettaIntegration(agent_name=agent_name)
    agent = letta.create_agent_with_memory_blocks(agent_name=agent_name)
    letta.agent_id = agent.id
    letta.attach_shared_block(shared.id)
```

### Conversation Logging (Built-in)

Automatically log all conversations to Letta archival memory with cross-agent sharing:

```python
from letta_integration import LettaIntegration, ConversationLogger

# Initialize Letta
letta = LettaIntegration(agent_name="my_agent")

# Create conversation logger
logger = ConversationLogger(letta, agent_name="windsurf")

# Log interactions
logger.log_interaction(
    user_input="Hello, how are you?",
    agent_response="I'm doing great! How can I help you today?"
)

# Log tool calls
logger.log_tool_call(
    tool_name="read_file",
    tool_input={"file_path": "/tmp/test.txt"},
    tool_output="File contents...",
    success=True
)

# End session
logger.end_session("Conversation completed successfully")
```

**Cross-Agent Search:** Any agent can search any other agent's conversations!

```python
# Search all conversations across all agents
results = logger.search_conversations("deployment strategy", limit=10)
for result in results:
    print(result['text'])
```

**Quick One-Off Logging:**

```python
from letta_integration import quick_log

# Log without managing logger instance
quick_log(
    user_input="What's the weather?",
    agent_response="It's sunny today!",
    agent_name="claude"
)
```

**Auto-Logger for Terminal Agents:**

```python
from letta_integration import AutoLogger

# Automatically detects which agent is running
auto = AutoLogger()
auto.start()  # Start logging

# All interactions automatically logged
auto.log("Hello", "Hi there!")

auto.end()  # End session
```

## Integration with Model Picker

Combine with GPU-enabled model picker:

```python
from letta_integration import LettaIntegration
from letta_model_picker import ModelPicker

picker = ModelPicker()
config = picker.get_recommended_config()

letta = LettaIntegration(agent_name="gpu_agent")
agent = letta.create_agent_with_memory_blocks(
    agent_name="gpu_agent",
    model=config['llm']['model_name'],
    embedding=config['embedding']['model_name']
)
```

## Troubleshooting

**Server not responding:**
```python
health = letta.check_server_health()
if health['status'] != 'healthy':
    print(f"Server error: {health.get('error')}")
```

**Agent not found:**
```python
# Always use get_or_create_agent for safety
agent_id = letta.get_or_create_agent("my_agent")
```

**Memory block errors:**
- Ensure agent exists before accessing blocks
- Use `get_or_create_agent()` to guarantee agent availability

## Related Skills

- **Model Picker** - `~/dotfiles/ai/skills/letta_model_picker/SKILL.md`
- **Conversation Logger** - `~/dotfiles/ai/skills/conversation_logger/SKILL.md`
- **Memory Management** - `~/dotfiles/ai/shared/skills/memory/letta/SKILL.md`

## Version

- **Letta Client SDK**: 0.1.x
- **Server**: Self-hosted (localhost:8283)
- **Last Updated**: 2024-03

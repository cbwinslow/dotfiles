# Letta Self-Hosted Memory System Documentation

## Overview

This document describes the Letta self-hosted memory server architecture and how our AI agent system integrates with it. Letta provides a stateful AI agent memory system that persists across all interactions.

**Architecture**: Local memory creation → Local PostgreSQL storage → Letta Web UI (via Cloudflare tunnel) for visualization

## What is Letta?

Letta (formerly MemGPT) is a platform for building stateful AI agents that remember and learn across conversations. Unlike traditional LLM interactions where context is lost after each session, Letta provides persistent memory management.

**Key Features**:
- Persistent agent memory across sessions
- Multiple memory types (core, archival, context, persona, human)
- Memory blocks that stay in the context window
- Built-in tools for agents to self-edit memory
- REST API for external integration

## Self-Hosted Setup

### Docker Deployment

The recommended way to run Letta locally is via Docker:

```bash
# Basic deployment with OpenAI
docker run -d \
  --name letta-server \
  -v ~/.letta/.persist/pgdata:/var/lib/postgresql/data \
  -p 8283:8283 \
  -e OPENAI_API_KEY="your_openai_api_key" \
  letta/letta:latest

# With Anthropic Claude
docker run -d \
  --name letta-server \
  -v ~/.letta/.persist/pgdata:/var/lib/postgresql/data \
  -p 8283:8283 \
  -e ANTHROPIC_API_KEY="your_api_key" \
  letta/letta:latest

# With password protection
  -e SECURE=true \
  -e LETTA_SERVER_PASSWORD="yourpassword" \
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | One provider required |
| `ANTHROPIC_API_KEY` | Anthropic API key | One provider required |
| `LETTA_SERVER_PASSWORD` | Password protection | Optional |
| `SECURE` | Enable password protection | Optional |
| `E2B_API_KEY` | Enable tool sandboxing | Optional |

### Verifying Installation

```bash
# Check health endpoint
curl http://localhost:8283/v1/health

# Expected response:
# {"status": "healthy", "version": "0.x.x"}
```

## Memory Architecture

Letta uses a multi-tier memory system:

### 1. Core Memory (Memory Blocks)

**Purpose**: Always-visible context prepended to every prompt

**Structure**:
```xml
<memory_blocks>
  <persona>
    <description>The persona block: Stores details about your current persona</description>
    <value>I am a helpful coding assistant...</value>
  </persona>
  <human>
    <description>The human block: Stores key details about the person</description>
    <value>The user is a software engineer who prefers concise answers</value>
  </human>
</memory_blocks>
```

**Properties**:
- **Label**: Unique identifier (e.g., "persona", "human", "scratchpad")
- **Description**: Explains purpose to the agent
- **Value**: The actual content
- **Limit**: Character limit (default 5000)
- **Always visible**: Never retrieved, always in context

**Use Cases**:
- Agent personality/persona
- User preferences (human block)
- Working memory/scratchpad
- Tool usage guidelines
- Real-time external state
- Multi-agent coordination

### 2. Archival Memory

**Purpose**: Long-term storage for conversations and large data

**Characteristics**:
- Retrieved via search when needed
- Stores conversation history
- Can hold large amounts of data
- Agents can search and retrieve

**API Endpoints**:
- `GET /v1/agents/{id}/archival_memory` - List archival memories
- `POST /v1/agents/{id}/archival_memory` - Create archival memory
- `POST /v1/agents/{id}/archival_memory/search` - Search archival

### 3. Context Memory

**Purpose**: Session-specific working state

**Characteristics**:
- Temporary session state
- Working context for current task
- Can be evicted from context window
- Agents can read/write via tools

### 4. Persona Memory

**Purpose**: Agent identity and behavior guidelines

**Implementation**: Often implemented as a "persona" memory block

### 5. Human Memory

**Purpose**: Information about the user

**Implementation**: Often implemented as a "human" memory block

## Memory Blocks API

### Creating Blocks

```python
from letta_client import Letta

client = Letta(api_key="your-api-key")

# Create standalone block
block = client.blocks.create(
    label="scratchpad",
    value="Working notes...",
    description="Agent working memory for calculations",
    limit=3000
)

# Create agent with blocks
agent = client.agents.create(
    memory_blocks=[
        {
            "label": "persona",
            "value": "I am a helpful coding assistant",
            "limit": 5000
        },
        {
            "label": "human",
            "value": "The user is a senior developer",
            "limit": 5000
        }
    ],
    model="openai/gpt-4o-mini"
)
```

### Managing Blocks

```python
# Retrieve block content
block = client.blocks.retrieve(block_id)
print(block.value)

# List all blocks
blocks = client.blocks.list()

# Filter by label
human_blocks = client.blocks.list(label="human")

# Search labels
results = client.blocks.list(label_search="organization")

# Update block (completely replaces content)
client.blocks.update(
    block_id,
    value="Updated content",
    limit=6000,
    description="Updated description"
)

# Delete block
client.blocks.delete(block_id)
```

### Agent-Scoped Block Operations

```python
# List agent's blocks
agent_blocks = client.agents.blocks.list(agent_id)

# Get specific block by label
persona = client.agents.blocks.retrieve(agent_id, "persona")

# Modify agent's block
client.agents.blocks.modify(
    agent_id,
    "scratchpad",
    value="New working notes"
)

# Detach block from agent
client.agents.blocks.detach(agent_id, block_id)
```

## REST API Reference

### Agents

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/agents` | GET | List all agents |
| `/v1/agents` | POST | Create new agent |
| `/v1/agents/{id}` | GET | Get agent details |
| `/v1/agents/{id}` | DELETE | Delete agent |
| `/v1/agents/{id}/memory` | GET | Get agent memories |
| `/v1/agents/{id}/memory` | POST | Create memory |
| `/v1/agents/{id}/memory/search` | POST | Search memories |

### Memory Blocks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/blocks` | GET | List blocks |
| `/v1/blocks` | POST | Create block |
| `/v1/blocks/{id}` | GET | Retrieve block |
| `/v1/blocks/{id}` | PUT | Update block |
| `/v1/blocks/{id}` | DELETE | Delete block |

### Messages

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/agents/{id}/messages` | GET | List messages |
| `/v1/agents/{id}/messages` | POST | Send message |

### Health

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/health` | GET | Server health |
| `/v1/stats` | GET | Server statistics |

## Connecting the ADE (Agent Development Environment)

The Letta ADE is a web interface that can connect to your self-hosted server:

### Via Cloudflare Tunnel (Recommended for Remote Access)

```bash
# Install cloudflared
# Create tunnel
cloudflared tunnel create letta-server

# Configure tunnel to point to localhost:8283
# Get the public URL
cloudflared tunnel route dns <tunnel-id> letta.yourdomain.com

# Run tunnel
cloudflared tunnel run <tunnel-id>
```

### Direct Connection

```bash
# Local development
curl http://localhost:8283/v1/health

# With password
curl -u admin:yourpassword http://localhost:8283/v1/health
```

## Integration Architecture

### Our System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (Local)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Agent Code → Local Memory Operations                │  │
│  │  ├─ Create memories                                  │  │
│  │  ├─ Store conversations                            │  │
│  │  ├─ Manage blocks                                  │  │
│  │  └─ Search/retrieve                                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ PostgreSQL (Direct)
                         │ (No API Key Required)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Local PostgreSQL Database                     │
│              (Letta Data Storage)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│  │   Agents     │ │  Memories    │ │   Blocks     │      │
│  └──────────────┘ └──────────────┘ └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Letta Server (via Docker)
                         │ Serves Web UI & API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Letta Server (localhost:8283)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  REST API Endpoint                                   │  │
│  │  Web UI (ADE)                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Cloudflare Tunnel (Optional)
                         │ For remote UI access
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Letta Web Interface (Browser)                    │
│           https://letta.yourdomain.com                     │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Direct PostgreSQL Access**: Our agents write directly to PostgreSQL for efficiency
2. **Letta Server for UI**: Letta server provides the web interface for visualization
3. **No API Key for Local**: Local operations don't require authentication
4. **Cloudflare for Remote UI**: Secure remote access to the web interface only

## Best Practices

### Memory Block Design

1. **Use descriptive labels**: `coding_standards`, `user_preferences`, `project_context`
2. **Write clear descriptions**: Help the agent understand block purpose
3. **Set appropriate limits**: Don't waste context window on rarely used data
4. **Read-only for policies**: Set `read_only=true` for blocks agents shouldn't modify

### Memory Organization

1. **Core (Blocks)**: Personality, user info, tool guidelines
2. **Archival**: Conversations, large documents, history
3. **Context**: Current task state, working memory

### Security

1. **Password protect**: Use `SECURE=true` for production
2. **API key rotation**: Regularly rotate LLM API keys
3. **Network isolation**: Don't expose 8283 publicly without tunnel
4. **Backups**: Regular PostgreSQL backups

## Troubleshooting

### Connection Issues

```bash
# Check if server is running
docker ps | grep letta

# Check logs
docker logs letta-server

# Verify port is open
netstat -tlnp | grep 8283
```

### Database Issues

```bash
# Reset database (WARNING: Destroys all data)
docker rm letta-server
docker volume rm letta_data

# Backup before major changes
docker exec letta-server pg_dump ...
```

### API Errors

```bash
# Test basic connectivity
curl -v http://localhost:8283/v1/health

# Check with authentication
curl -u admin:password http://localhost:8283/v1/health
```

## Resources

- [Letta Documentation](https://docs.letta.com)
- [Docker Setup Guide](https://docs.letta.com/guides/docker/)
- [Memory Blocks Guide](https://docs.letta.com/guides/agents/memory-blocks/)
- [API Reference](https://docs.letta.com/api-reference/)
- [GitHub Repository](https://github.com/letta-ai/letta)

## Comparison: Our Setup vs Letta Best Practices

| Aspect | Letta Best Practice | Our Current Setup | Gap |
|--------|---------------------|-------------------|-----|
| Memory Types | Core, Archival, Context, Persona, Human | Only Archival (conversations) | Missing Core blocks, Context |
| Block Management | Full CRUD via API | Not implemented | Missing |
| Sources/Attribution | Track memory sources | Not implemented | Missing |
| Agent Self-Editing | Built-in memory tools | Not available | Missing |
| ADE Integration | Cloudflare tunnel | Configured | Good |
| Backup Strategy | pg_dump + file backup | Partial | Needs work |

---

*Document created from Letta official documentation*  
*Sources: docs.letta.com, letta/letta GitHub, letta-ai/lettabot*

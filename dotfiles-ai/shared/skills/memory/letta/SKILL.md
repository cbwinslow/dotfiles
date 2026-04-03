# Letta Memory Management Skill

**Description**: Advanced memory management for AI agents using Letta server integration with GPU model support and automatic conversation logging. Provides persistent storage, retrieval, and context management across sessions with cross-agent conversation sharing.

**Version**: 2.0.0
**Author**: AI Agent System
**Framework**: LangChain, CrewAI, AutoGen compatible

---

## Overview

This skill enables AI agents to have persistent "state" by using your self-hosted Letta server. It provides comprehensive memory management capabilities including:

- **Archival Memory**: Long-term storage of important information and decisions
- **Core Memory**: Pinned context that's always available during conversations
- **Agent Context**: Agent-specific state management
- **Memory Search**: Vector-based search across stored memories
- **Cross-Session Intelligence**: Retain knowledge across multiple agent sessions
- **GPU Model Support**: Configure GPU-enabled llama.cpp models
- **Automatic Conversation Logging**: Log all AI agent conversations automatically
- **Cross-Agent Sharing**: Any agent can resume conversations from other agents

## New Features (v2.0.0)

### 🆕 Model Picker Integration
```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="windsurf")

# Configure GPU llama.cpp model
letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35
)

# Apply preset
letta.apply_model_preset("fast_gpu")

# Check current configuration
letta.print_model_info()
```

### 🆕 Universal Conversation Logger
```python
from universal_conversation_logger import ConversationLogger

logger = ConversationLogger(agent_name="windsurf")
session_id = logger.start_conversation(tool="windsurf")

# Log interactions (automatic)
logger.log_interaction(
    user_input="Configure the system",
    agent_response="System configured successfully",
    tool="windsurf"
)

# Search across all agents
results = logger.search_related_conversations("GPU models")

# Resume conversation
logger.resume_conversation(session_id)
```

---

## Core Operations

### 1. The Recall Phase (Mandatory Start)
At the beginning of any non-trivial task, search Letta to see what we've done before.

```bash
# Search archival memories
letta archival-search <agent-id> "<topic or keywords>"

# Get core memory
letta memory-get <agent-id>

# List recent memories
letta archival-list <agent-id> --limit 10
```

**Default Agent**: `coder` (agent-1167f15a-a10a-4595-b962-ec0f372aae0d) for development tasks

### 2. The Storage Phase (In-flight)
When a key decision is made or a complex fact is discovered, commit it to archival memory.

```bash
# Store important information
letta archival-insert <agent-id> "Fact: <details>" "tag1,tag2"

# Update core memory
letta memory-update <agent-id> core "Important context for this agent"

# Store agent context
letta memory-update <agent-id> context "key:value"
```

### 3. The Persona Sync (Human/Agent Profile)
If the user's preferences change or the agent's "role" needs updating:

```bash
# Update agent persona
letta memory-update <agent-id> persona "I am now focused on <new role>."

# Update human preferences
letta memory-update <agent-id> human "User prefers <preference>."
```

## Advanced Memory Features

### Archival vs Core Memory

- **Core Memory**: Pinned to every request. Use for high-frequency rules and essential context.
- **Archival Memory**: Vector-searchable. Use for historical logs and deep knowledge.

### Multi-Agent Context

If a task spans multiple domains, search across relevant agents:

- `ops-monitor`: For system health and logs
- `infra-assistant`: For Docker/Postgres setup
- `researcher`: For documentation and external facts
- `agent-processor`: For agent data processing

### Memory Tags and Organization

Use tags to organize and retrieve memories efficiently:

```bash
# Store with tags
letta archival-insert <agent-id> "Project setup complete" "setup,project,complete"

# Search by tags
letta archival-search <agent-id> "setup" --tags "project"
```

## Integration with Agent Memory System

This skill integrates seamlessly with the Agent Memory System package:

```python
from agent_memory import (
    store_memory,
    search_memories,
    store_agent_context,
    get_agent_context
)

# Store memory with Agent system
memory_id = store_memory(
    memory_type="processing_status",
    title="Entity extraction complete",
    content="Processed 1000 documents, extracted 50000 entities",
    tags=["ner", "entities", "processing"]
)

# Search memories
results = search_memories("entity extraction", memory_type="processing_status")

# Store agent context
store_agent_context(
    agent_name="agent_processor",
    context_key="current_focus",
    context_value="entity_extraction"
)
```

## Agent Configuration

### LangChain Integration

```yaml
# agents/opencode/config.yaml
memory:
  backend: letta
  config:
    server_url: http://localhost:8283
    api_key: ${LETTA_API_KEY}
    agent_id: "coder"
```

### CrewAI Integration

```yaml
# frameworks/crewai/config.yaml
agents:
  researcher:
    memory_backend: letta
    letta_config:
      agent_id: "researcher"
      memory_type: "archival"
```

### AutoGen Integration

```yaml
# frameworks/autogen/config.yaml
agents:
  assistant:
    memory_config:
      type: "letta"
      server_url: "http://localhost:8283"
      api_key: "${LETTA_API_KEY}"
```

## Best Practices

### 1. Memory Storage Guidelines

- **Store decisions**: Key architectural choices, tool selections
- **Store context**: Project-specific information, user preferences
- **Store results**: Important findings, analysis outcomes
- **Store errors**: Common mistakes and how to avoid them

### 2. Memory Retrieval Strategy

- **Start with recall**: Always search for relevant context before beginning
- **Use specific queries**: Include agent names, project names, dates
- **Check multiple agents**: Search across relevant agent contexts
- **Verify information**: Cross-reference with current state

### 3. Memory Organization

- **Use consistent tags**: Establish naming conventions
- **Categorize by type**: processing_status, technical_architecture, etc.
- **Include metadata**: Timestamps, source information, confidence levels
- **Regular cleanup**: Remove outdated or irrelevant memories

## Troubleshooting

### Common Issues

1. **Letta server not responding**
   - Check if Letta server is running: `docker ps`
   - Verify connection: `curl http://localhost:8283`
   - Check API key in environment variables

2. **Memory search returning no results**
   - Verify agent ID is correct
   - Check if memories were actually stored
   - Try broader search terms or remove tag filters

3. **Memory storage failing**
   - Check available disk space
   - Verify PostgreSQL connection
   - Check memory size limits

### Debug Commands

```bash
# Check Letta server status
curl http://localhost:8283/health

# List all agents
letta list

# Check specific agent memory
letta memory-get <agent-id> --verbose

# Test memory storage
letta archival-insert <agent-id> "Test memory" "test"
```

## Security Considerations

- **API Keys**: Store Letta API keys in environment variables
- **Sensitive Data**: Avoid storing sensitive information in memories
- **Access Control**: Limit memory access to authorized agents only
- **Data Retention**: Implement memory cleanup policies

## Performance Optimization

- **Batch Operations**: Group multiple memory operations
- **Selective Storage**: Only store high-value information
- **Efficient Search**: Use specific queries with appropriate tags
- **Memory Cleanup**: Regularly remove outdated memories

## Examples

### Example 1: Project Setup

```bash
# Store project setup information
letta archival-insert coder "Project setup complete: PostgreSQL, LangChain, Agent memory system" "setup,project,database"

# Update core memory with project context
letta memory-update coder core "Working on Agent system project with multi-agent architecture"
```

### Example 2: Research Task

```bash
# Before starting research, recall previous findings
letta archival-search researcher "entity extraction methods"

# During research, store important findings
letta archival-insert researcher "Found optimal OCR pipeline: PyMuPDF + Surya + Docling" "ocr,pipeline,optimization"

# After research, update agent context
letta memory-update researcher context "current_task:ocr_pipeline_optimization"
```

### Example 3: Cross-Agent Collaboration

```bash
# Researcher finds information
letta archival-insert researcher "Database schema: documents, entities, relationships" "database,schema"

# Developer retrieves information
letta archival-search coder "database schema" --agent researcher

# Store implementation details
letta archival-insert coder "Implemented PostgreSQL schema with FTS5 indexing" "database,implementation"
```

## Integration with Other Skills

This skill works seamlessly with other skills in the system:

- **Model Picker Skill**: GPU-enabled model configuration and management
- **Conversation Logger Skill**: Automatic conversation logging across agents
- **Data Processing Skills**: Store processing results and configurations
- **Code Generation Skills**: Remember coding patterns and preferences
- **Analysis Skills**: Retain analytical frameworks and findings
- **Integration Skills**: Remember API endpoints and authentication methods

## Related Skills

| Skill | Purpose | Location |
|-------|---------|----------|
| **Model Picker** | GPU llama.cpp and Ollama configuration | `~/dotfiles/ai/skills/model_picker/SKILL.md` |
| **Conversation Logger** | Automatic conversation logging | `~/dotfiles/ai/skills/conversation_logger/SKILL.md` |
| **Memory (this)** | Core memory management | `~/dotfiles/ai/shared/skills/memory/letta/SKILL.md` |

## Version History

- **2.0.0** (2026-03-28): Major update with GPU model support and conversation logging
  - Added Model Picker integration for GPU llama.cpp models
  - Added Universal Conversation Logger for cross-agent conversation sharing
  - Updated to work with new LettaIntegration class features
  
- **1.0.0**: Initial release with core memory management features
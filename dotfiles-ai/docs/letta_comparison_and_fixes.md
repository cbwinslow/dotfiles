# Letta Self-Hosted Setup Comparison & Fixes

## Executive Summary

This document compares our current AI agent memory system setup with Letta's official self-hosted documentation and identifies gaps and required fixes.

## Architecture Understanding

### Our Current Setup
```
Agent Code → agent_memory (PostgreSQL direct) → Letta Server (Web UI/ADE)
     ↑                                              ↑
     └────────── Local Only ────────────────────────┘
                           ↓
                    Cloudflare Tunnel (optional)
                           ↓
                    Remote Web Browser Access
```

### Letta's Official Architecture
```
Agent Code → Letta REST API → Letta Server → PostgreSQL
     ↑                                              ↓
     └────────── Web UI (ADE) ←─────────────────────┘
```

**Key Difference**: We write directly to PostgreSQL; Letta recommends using their REST API.

## Comparison Matrix

| Component | Letta Official | Our Setup | Status | Action Needed |
|-----------|---------------|-----------|--------|---------------|
| **Memory Types** | | | | |
| Core Memory (Blocks) | ✅ Full support | ⚠️ Partial (no API) | Gap | Add block CRUD operations |
| Archival Memory | ✅ Full support | ✅ Implemented | Good | None |
| Context Memory | ✅ Full support | ❌ Missing | Gap | Add context lifecycle mgmt |
| Persona Memory | ✅ Full support | ⚠️ Via blocks only | Gap | Add persona-specific handling |
| Human Memory | ✅ Full support | ⚠️ Via blocks only | Gap | Add human/user memory |
| **API Operations** | | | | |
| Agent CRUD | ✅ Full support | ✅ Implemented | Good | None |
| Memory Block CRUD | ✅ Full support | ⚠️ Basic only | Gap | Add full block management |
| Memory Search | ✅ Full support | ✅ Implemented | Good | None |
| Sources/Attribution | ✅ Full support | ❌ Missing | Gap | Add source tracking |
| Memory Passages | ✅ Full support | ❌ Missing | Gap | Add passage-level retrieval |
| **Features** | | | | |
| ADE Web Interface | ✅ Available | ✅ Configured | Good | Verify tunnel setup |
| Agent Self-Editing | ✅ Built-in tools | ❌ Not available | Gap | Add memory editing tools |
| Multi-Agent Shared Memory | ✅ Supported | ⚠️ Via PostgreSQL | Gap | Add shared block support |
| **Infrastructure** | | | | |
| Docker Compose | ✅ Official | ✅ Configured | Good | Update to match latest |
| Password Protection | ✅ Supported | ⚠️ Optional | Good | Document setup |
| Backup/Restore | ✅ pg_dump | ⚠️ Partial | Gap | Complete backup system |

## Critical Gaps Identified

### 1. Memory Block Management (HIGH PRIORITY)

**Current State**: Basic block storage only
**Required**: Full CRUD + agent attachment/detachment

**Missing Operations**:
```python
# Block lifecycle
client.blocks.create(label, value, description, limit)
client.blocks.retrieve(block_id)
client.blocks.update(block_id, value, limit, description)
client.blocks.delete(block_id)
client.blocks.list(label_filter, search)

# Agent-block relationships
client.agents.blocks.list(agent_id)
client.agents.blocks.retrieve(agent_id, label)
client.agents.blocks.modify(agent_id, label, new_value)
client.agents.blocks.attach(agent_id, block_id)
client.agents.blocks.detach(agent_id, block_id)
```

**Implementation Location**: `~/dotfiles/ai/packages/letta_integration/letta_integration/__init__.py`

### 2. Core Memory Types (HIGH PRIORITY)

**Current State**: Only archival memory implemented
**Required**: All 5 memory types per Letta spec

**Memory Type Definitions**:
```python
MEMORY_TYPES = {
    "core": {
        "description": "Always-visible memory blocks in context window",
        "ttl_days": -1,  # Never expires
        "max_entries": None,  # Limited by context window
        "examples": ["persona", "human", "scratchpad", "guidelines"]
    },
    "archival": {
        "description": "Long-term storage, retrieved via search",
        "ttl_days": 365,
        "max_entries": 10000,
        "examples": ["conversations", "documents", "history"]
    },
    "context": {
        "description": "Session-specific working state",
        "ttl_days": 30,
        "max_entries": 100,
        "examples": ["current_task", "working_memory"]
    },
    "persona": {
        "description": "Agent identity and behavior (stored as core block)",
        "ttl_days": -1,
        "max_entries": 1,
        "examples": ["agent_personality"]
    },
    "human": {
        "description": "User information (stored as core block)",
        "ttl_days": -1,
        "max_entries": 1,
        "examples": ["user_preferences", "user_profile"]
    }
}
```

### 3. Sources & Attribution (MEDIUM PRIORITY)

**Current State**: No source tracking
**Required**: Track where memories come from

**Implementation**:
```python
def store_memory_with_source(
    memory_type: str,
    content: str,
    source_type: str,  # "conversation", "document", "tool", "user"
    source_id: str,
    source_metadata: Dict
):
    """Store memory with full attribution"""
    pass
```

### 4. Agent Self-Editing Tools (MEDIUM PRIORITY)

**Current State**: No built-in tools for agents to modify memory
**Required**: Letta-style built-in memory tools

**Required Tools**:
```python
# Core memory tools
memory_edit(block_label, new_value)
memory_append(block_label, content_to_add)
memory_search(query, memory_type)
memory_delete(memory_id)

# Archival memory tools
archival_memory_insert(content, tags)
archival_memory_search(query, limit)
archival_memory_delete(memory_id)

# Context management
context_set(key, value)
context_get(key)
context_clear()
```

### 5. Backup & Restore (MEDIUM PRIORITY)

**Current State**: Partial implementation
**Required**: Complete backup system matching Letta

**Implementation**:
```python
def backup_all_memories(backup_path: str) -> Dict:
    """
    Backup all memory types:
    - Core memory blocks
    - Archival memories
    - Context state
    - Agent configurations
    """
    pass

def restore_from_backup(backup_path: str) -> Dict:
    """Complete restore with verification"""
    pass
```

## Recommended Fixes & Implementation Plan

### Phase 1: Core Memory Block API (Immediate)

1. **Add Block CRUD to LettaIntegration class**
   - Location: `letta_integration/__init__.py`
   - Methods: `create_block`, `get_block`, `update_block`, `delete_block`, `list_blocks`

2. **Add Agent-Block Relationship Methods**
   - Methods: `attach_block_to_agent`, `detach_block_from_agent`, `get_agent_blocks`

3. **Update Memory Management Skill**
   - Location: `skills/letta_server/memory_management.py`
   - Add block lifecycle management functions

### Phase 2: Memory Types Implementation (Next)

1. **Define Memory Type Schema**
   - Create `memory_types.yaml` configuration
   - Define validation rules per type

2. **Implement Context Memory**
   - Session-based storage
   - Auto-cleanup after TTL
   - Working memory for current tasks

3. **Enhance Persona/Human Memory**
   - Standardized block labels
   - Template system for common personas

### Phase 3: Advanced Features (Future)

1. **Sources & Attribution**
   - Add source tracking to all memory operations
   - Query by source type/id

2. **Agent Self-Editing**
   - Create tool definitions
   - Add to agent configurations

3. **Backup System**
   - Complete backup/restore
   - Automated scheduled backups

## Configuration Updates Needed

### 1. Update base_agent.yaml
```yaml
# Add to ~/dotfiles/ai/base/base_agent.yaml

letta:
  memory_types:
    core:
      enabled: true
      blocks:
        - persona
        - human
        - scratchpad
    archival:
      enabled: true
      auto_save_conversations: true
    context:
      enabled: true
      session_ttl: 30
  
  # Add block management
  block_management:
    auto_create_default_blocks: true
    default_blocks:
      - label: "persona"
        description: "Agent personality and behavior"
        limit: 5000
      - label: "human"
        description: "User information and preferences"
        limit: 5000
      - label: "scratchpad"
        description: "Working memory for calculations"
        limit: 3000
```

### 2. Update Skills Registry
```yaml
# Add to ~/dotfiles/ai/skills/registry.yaml

core:
  memory_block_management:
    path: skills/letta_server
    description: "Full memory block CRUD operations"
    required: true
    operations:
      - create_block
      - retrieve_block
      - update_block
      - delete_block
      - list_blocks
      - attach_to_agent
      - detach_from_agent
```

## Docker Compose Updates

### Current: ~/dotfiles/ai/infra/letta/docker-compose.letta.yml
```yaml
version: '3.8'
services:
  letta:
    image: letta/letta:latest
    ports:
      - "8283:8283"
    volumes:
      - letta-data:/var/lib/postgresql/data
      - ./configs:/app/configs  # Add config mount
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - LETTA_SERVER_PASSWORD=${LETTA_SERVER_PASSWORD:-}
      - SECURE=${SECURE:-false}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8283/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  letta-data:
```

## Testing & Validation

### 1. Block Operations Test
```python
# Test script for block management
def test_block_operations():
    letta = LettaIntegration()
    
    # Create block
    block = letta.create_block(
        label="test_persona",
        value="I am a test agent",
        limit=5000
    )
    
    # Attach to agent
    letta.attach_block_to_agent(agent_id, block["id"])
    
    # Verify in context
    agent_data = letta.get_agent(agent_id)
    assert "test_persona" in agent_data["memory_blocks"]
    
    # Update block
    letta.update_block(block["id"], value="Updated persona")
    
    # Cleanup
    letta.detach_block_from_agent(agent_id, block["id"])
    letta.delete_block(block["id"])
```

### 2. Memory Types Test
```python
def test_memory_types():
    letta = LettaIntegration()
    
    # Test core memory
    core_mem = letta.create_memory(
        content="Important fact",
        memory_type="core"
    )
    assert core_mem["memory_type"] == "core"
    
    # Test archival
    archival_mem = letta.create_memory(
        content="Conversation log",
        memory_type="archival"
    )
    assert archival_mem["memory_type"] == "archival"
    
    # Test context
    context_mem = letta.create_memory(
        content="Current task state",
        memory_type="context"
    )
    assert context_mem["memory_type"] == "context"
```

## Migration Guide

### For Existing Users

1. **Update Package Name**
   ```bash
   cd ~/dotfiles/ai/packages/agent_memory
   pip install -e .  # Reinstall with new name
   ```

2. **Update Imports in Custom Code**
   ```python
   # Old
   from epstein_memory import store_memory
   
   # New
   from agent_memory import store_memory
   ```

3. **Run Memory System Update**
   ```bash
   agent-memory-cli init-memories
   ```

## Documentation Updates

### Files to Update:
1. `~/dotfiles/ai/docs/letta_server_skills_guide.md` - Add block operations
2. `~/dotfiles/ai/README.md` - Update architecture diagram
3. `~/dotfiles/ai/QUICKSTART.md` - Add block management examples
4. `~/dotfiles/ai/global_rules/agent_init_rules.md` - Update memory requirements

## Success Metrics

After implementing fixes:
- [ ] All 5 Letta memory types functional
- [ ] Full block CRUD operations working
- [ ] Agent self-editing tools available
- [ ] Sources tracked on all memories
- [ ] Backup/restore system complete
- [ ] ADE web interface fully functional via Cloudflare
- [ ] All 10 agents using unified memory system

---

*Document created: March 25, 2026*  
*Based on Letta documentation v0.x*  
*System version: 1.0.0*

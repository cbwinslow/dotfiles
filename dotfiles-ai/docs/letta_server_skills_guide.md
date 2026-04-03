# Letta Server Skills Usage Guide

**Version**: 1.0.0  
**Purpose**: Complete guide for using Letta Server skills in AI agents  
**Audience**: AI Agent Developers and Administrators

## 🎯 Overview

The Letta Server Skills system provides centralized memory management and server operations for all AI agents. This guide explains how to integrate and use these skills effectively.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Memory Management Skills](#memory-management-skills)
3. [Server Management Skills](#server-management-skills)
4. [Agent Integration Skills](#agent-integration-skills)
5. [Agent Configuration Examples](#agent-configuration-examples)
6. [Usage Patterns](#usage-patterns)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### 1. Import Skills in Agent Code

```python
from skills.letta_server import (
    store_conversation,
    search_memories,
    check_server_health,
    setup_agent_memory
)
```

### 2. Configure Agent

```yaml
# In agent config.yaml
skills:
  - letta_server

tools:
  - letta_server.store_conversation
  - letta_server.search_memories
  - letta_server.check_server_health

letta_server:
  server_url: "${LETTA_SERVER_URL}"
  api_key: "${LETTA_API_KEY}"
  agent_name: "your_agent_name"
```

### 3. Use Skills in Agent Logic

```python
# Store conversation
memory_id = store_conversation({
    "agent_name": "opencode",
    "conversation_history": conversation,
    "tags": ["code_generation", "python"]
})

# Search for relevant memories
relevant_memories = search_memories({
    "query": "entity extraction",
    "agent_name": "opencode"
})

# Check server health
health = check_server_health({})
```

## 🧠 Memory Management Skills

### `store_conversation`

**Purpose**: Save conversation history to Letta server  
**When to Use**: After every conversation or task completion

```python
# Basic usage
memory_id = store_conversation({
    "agent_name": "opencode",
    "conversation_history": [
        {"role": "user", "content": "Write a Python script"},
        {"role": "assistant", "content": "Here's the script..."}
    ],
    "tags": ["code_generation", "python"]
})

# With metadata
memory_id = store_conversation({
    "agent_name": "opencode",
    "conversation_history": conversation,
    "metadata": {
        "task_type": "code_generation",
        "complexity": "medium"
    },
    "tags": ["code_generation", "python", "data_analysis"]
})
```

### `search_memories`

**Purpose**: Search for relevant memories before starting tasks  
**When to Use**: At the beginning of tasks to leverage existing knowledge

```python
# Basic search
results = search_memories({
    "query": "entity extraction",
    "agent_name": "opencode"
})

# Advanced search with filters
results = search_memories({
    "query": "Python data processing",
    "agent_name": "opencode",
    "tags": ["python", "data_processing"],
    "date_range": {
        "start": "2026-03-01",
        "end": "2026-03-24"
    }
})

# Use search results
if results:
    relevant_context = [result["content_preview"] for result in results[:3]]
    # Use context in task execution
```

### `get_memory_stats`

**Purpose**: Get comprehensive memory statistics  
**When to Use**: For monitoring and debugging memory usage

```python
# Get memory statistics
stats = get_memory_stats()

print(f"Total memories: {stats['total_memories']}")
print(f"Memory types: {stats['memory_types']}")
print(f"Agent contexts: {stats['agent_contexts']}")
```

### `store_entity_extraction`

**Purpose**: Store extracted entities for future reference  
**When to Use**: After NLP processing and entity extraction

```python
# Store extracted entities
entities = [
    {"text": "John Smith", "label": "PERSON", "confidence": 0.95},
    {"text": "New York", "label": "LOCATION", "confidence": 0.88}
]

memory_id = store_entity_extraction({
    "agent_name": "kilocode",
    "entities": entities,
    "context": "Document analysis",
    "extraction_metadata": {
        "model": "en_core_web_sm",
        "processing_time": "2.5s"
    }
})
```

### `manage_memory_lifecycle`

**Purpose**: Handle memory cleanup and organization  
**When to Use**: Periodically to maintain system performance

```python
# Clean up old memories
cleanup_result = manage_memory_lifecycle({
    "agent_name": "opencode",
    "cleanup_days": 30,
    "max_memory_size_mb": 50,
    "optimize_search": True
})

print(f"Memories cleaned: {cleanup_result['memories_cleaned']}")
print(f"Space freed: {cleanup_result['total_space_freed_mb']} MB")
```

## 🖥️ Server Management Skills

### `check_server_health`

**Purpose**: Monitor Letta server health and status  
**When to Use**: Regularly for monitoring, before critical operations

```python
# Check server health
health = check_server_health()

if health["status"] == "healthy":
    print("Server is healthy")
elif health["status"] == "unhealthy":
    print("Server has issues:")
    for issue in health["issues"]:
        print(f"  - {issue}")
```

### `initialize_server`

**Purpose**: Setup and configure Letta server  
**When to Use**: During initial setup or server restart

```python
# Initialize server
config = {
    "host": "localhost",
    "port": 8283,
    "api_key": "your-api-key",
    "debug": False
}

database_url = "postgresql://user:pass@localhost:5432/letta"

result = initialize_server({
    "config": config,
    "database_url": database_url
})

if result["status"] == "success":
    print("Server initialized successfully")
else:
    print(f"Initialization failed: {result['errors']}")
```

### `backup_server_data`

**Purpose**: Create backups of Letta data  
**When to Use**: Regularly for data protection

```python
# Create backup
backup_result = backup_server_data({
    "backup_path": "/home/user/backups/letta_backup_20260324"
})

if backup_result["status"] == "success":
    print(f"Backup created: {backup_result['archive_path']}")
    print(f"Size: {backup_result['size_mb']:.2f} MB")
```

### `restore_server_data`

**Purpose**: Restore from backups  
**When to Use**: After data loss or system failure

```python
# Restore from backup
restore_result = restore_server_data({
    "backup_path": "/home/user/backups/letta_backup_20260324.tar.gz"
})

if restore_result["status"] == "success":
    print("Server restored successfully")
else:
    print(f"Restore failed: {restore_result['errors']}")
```

## 🔗 Agent Integration Skills

### `setup_agent_memory`

**Purpose**: Configure agent-specific memory settings  
**When to Use**: During agent initialization

```python
# Setup agent memory
memory_config = {
    "backend": "letta_server",
    "default_ttl_days": 30,
    "max_memory_size_mb": 50
}

skills = ["memory_management", "entity_extraction", "conversation_logging"]

result = setup_agent_memory({
    "agent_name": "opencode",
    "memory_config": memory_config,
    "skills": skills
})

if result["status"] == "success":
    print("Agent memory setup completed")
```

### `sync_agent_context`

**Purpose**: Synchronize agent context with Letta  
**When to Use**: Regularly to keep context up-to-date

```python
# Sync agent context
sync_result = sync_agent_context({
    "agent_name": "opencode"
})

if sync_result["status"] == "success":
    print(f"Context synced, {sync_result['changes_applied']} changes applied")
```

### `create_agent_profile`

**Purpose**: Create agent profiles in Letta  
**When to Use**: When setting up new agents

```python
# Create agent profile
profile_data = {
    "framework": "langchain",
    "provider": "openai",
    "model": "gpt-4o",
    "version": "1.0.0"
}

skills = ["memory_management", "code_generation", "data_processing"]

result = create_agent_profile({
    "agent_name": "opencode",
    "profile_data": profile_data,
    "skills": skills
})

if result["status"] == "success":
    print("Agent profile created successfully")
```

### `get_agent_status`

**Purpose**: Get comprehensive agent status information  
**When to Use**: For monitoring and debugging

```python
# Get agent status
status = get_agent_status({
    "agent_name": "opencode"
})

print(f"Agent status: {status['status']}")
print(f"Memory usage: {status['memory_usage']['total_memories']} memories")
print(f"Last activity: {status['memory_usage']['last_activity']}")
```

## 🤖 Agent Configuration Examples

### General Agent Configuration Template

```yaml
# agents/{agent_name}/config.yaml
name: {agent_name}_agent
framework: langchain|autogen|crewai
provider: openai|anthropic|google
model: gpt-4o|claude-sonnet-4-5|gemini-pro

skills:
  - letta_server

tools:
  - letta_server.store_conversation
  - letta_server.search_memories
  - letta_server.check_server_health
  # Add other skills as needed

memory:
  backend: letta_server
  default_ttl_days: 30
  max_memory_size_mb: 50

letta_server:
  server_url: "${LETTA_SERVER_URL}"
  api_key: "${LETTA_API_KEY}"
  agent_name: "{agent_name}"
  auto_sync: true
  skills:
    - "memory_management"
    - "entity_extraction"
    - "conversation_logging"
    # Add skills based on agent requirements
```

### Framework-Specific Examples

#### LangChain Agent
```yaml
framework: langchain
tools:
  - letta_server.store_conversation
  - letta_server.search_memories
  - letta_server.get_memory_stats
```

#### AutoGen Agent
```yaml
framework: autogen
tools:
  - letta_server.check_server_health
  - letta_server.setup_agent_memory
  - letta_server.sync_agent_context
```

#### CrewAI Agent
```yaml
framework: crewai
tools:
  - letta_server.store_entity_extraction
  - letta_server.manage_memory_lifecycle
  - letta_server.create_agent_profile
```

## 🔄 Usage Patterns

### Pattern 1: Memory-Aware Task Execution

```python
def execute_task_with_memory(agent_name, task_description):
    """Execute task with memory search and storage"""
    
    # 1. Search for relevant memories
    relevant_memories = search_memories({
        "query": task_description,
        "agent_name": agent_name
    })
    
    # 2. Execute task with context
    context = [mem["content_preview"] for mem in relevant_memories[:5]]
    result = execute_task(task_description, context=context)
    
    # 3. Store results
    store_conversation({
        "agent_name": agent_name,
        "conversation_history": [
            {"role": "user", "content": task_description},
            {"role": "assistant", "content": result}
        ],
        "tags": ["task_execution", agent_name]
    })
    
    return result
```

### Pattern 2: Automatic Conversation Saving

```python
def handle_conversation(agent_name, conversation):
    """Handle conversation with automatic memory saving"""
    
    # Process conversation
    response = process_conversation(conversation)
    
    # Save to Letta server
    memory_id = store_conversation({
        "agent_name": agent_name,
        "conversation_history": conversation,
        "tags": ["conversation", agent_name]
    })
    
    return response, memory_id
```

### Pattern 3: Periodic Health Monitoring

```python
def monitor_agent_health(agent_name):
    """Monitor agent and server health"""
    
    # Check server health
    server_health = check_server_health({})
    
    # Check agent status
    agent_status = get_agent_status({
        "agent_name": agent_name
    })
    
    # Sync agent context
    sync_result = sync_agent_context({
        "agent_name": agent_name
    })
    
    # Report issues
    if server_health["status"] != "healthy":
        handle_server_issues(server_health)
    
    if agent_status["status"] != "active":
        handle_agent_issues(agent_status)
    
    return {
        "server_health": server_health,
        "agent_status": agent_status,
        "sync_result": sync_result
    }
```

### Pattern 4: Entity Extraction Pipeline

```python
def process_document_with_entities(agent_name, document):
    """Process document and extract entities"""
    
    # Extract entities
    entities = extract_entities(document)
    
    # Store entities
    memory_id = store_entity_extraction({
        "agent_name": agent_name,
        "entities": entities,
        "context": "Document processing",
        "extraction_metadata": {
            "document_type": "PDF",
            "processing_time": "3.2s"
        }
    })
    
    # Store document processing result
    store_conversation({
        "agent_name": agent_name,
        "conversation_history": [
            {"role": "system", "content": f"Processed document with {len(entities)} entities"},
            {"role": "user", "content": document[:100] + "..."},
            {"role": "assistant", "content": f"Extracted {len(entities)} entities"}
        ],
        "tags": ["document_processing", "entity_extraction"]
    })
    
    return entities, memory_id
```

## 💡 Best Practices

### 1. Memory Management

- **Tag Consistently**: Use consistent tags across all agents
- **Limit Memory Size**: Set appropriate TTL and size limits
- **Regular Cleanup**: Use `manage_memory_lifecycle` regularly
- **Search Before Creating**: Always search existing memories first

### 2. Server Management

- **Monitor Health**: Check server health regularly
- **Backup Frequently**: Create backups daily or weekly
- **Use Environment Variables**: Store sensitive config in environment variables
- **Handle Errors Gracefully**: Implement proper error handling

### 3. Agent Integration

- **Initialize Properly**: Always call `setup_agent_memory` during agent setup
- **Sync Regularly**: Use `sync_agent_context` to keep context current
- **Monitor Status**: Regularly check agent status with `get_agent_status`
- **Update Skills**: Use `update_agent_skills` when adding new capabilities

### 4. Performance Optimization

- **Batch Operations**: Group multiple memory operations when possible
- **Use Specific Queries**: Make search queries as specific as possible
- **Limit Result Sets**: Use pagination for large result sets
- **Cache Results**: Cache frequently accessed memory data

## 🔧 Troubleshooting

### Common Issues

#### 1. Memory Storage Failed
```python
# Error: Failed to store conversation
# Solution: Check database connection and permissions

# Check database connection
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=int(os.getenv("PG_PORT")),
        database=os.getenv("PG_DBNAME"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
    )
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### 2. Server Connection Failed
```python
# Error: API connection failed
# Solution: Check server URL and API key

# Verify server is running
import requests
try:
    response = requests.get(f"{os.getenv('LETTA_SERVER_URL')}/health")
    if response.status_code == 200:
        print("Server is healthy")
    else:
        print(f"Server returned status: {response.status_code}")
except Exception as e:
    print(f"Server connection failed: {e}")
```

#### 3. Search Performance Issues
```python
# Error: Search is slow
# Solution: Use more specific queries and filters

# Instead of broad search
results = search_memories({"query": "data"})

# Use specific search
results = search_memories({
    "query": "entity extraction",
    "agent_name": "opencode",
    "tags": ["nlp", "processing"],
    "date_range": {"start": "2026-03-01", "end": "2026-03-24"}
})
```

#### 4. Agent Context Issues
```python
# Error: Agent context not found
# Solution: Initialize agent context

# Initialize agent context
result = setup_agent_memory({
    "agent_name": "opencode",
    "memory_config": {
        "backend": "letta_server",
        "default_ttl_days": 30
    },
    "skills": ["memory_management"]
})
```

### Debugging Tips

1. **Enable Debug Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Memory Statistics**
   ```python
   stats = get_memory_stats()
   print(f"Total memories: {stats['total_memories']}")
   print(f"Memory types: {stats['memory_types']}")
   ```

3. **Verify Agent Status**
   ```python
   status = get_agent_status({"agent_name": "opencode"})
   print(f"Agent status: {status['status']}")
   print(f"Memory usage: {status['memory_usage']}")
   ```

4. **Test Server Health**
   ```python
   health = check_server_health({})
   print(f"Server status: {health['status']}")
   print(f"Issues: {health['issues']}")
   ```

## 📞 Support

For additional support:

1. **Check Logs**: Review agent and server logs for errors
2. **Verify Configuration**: Ensure all environment variables are set
3. **Test Connectivity**: Verify database and server connections
4. **Review Documentation**: Check this guide and the main README
5. **Contact Support**: Reach out to the development team

---

**Note**: This guide is designed to help you effectively use the Letta Server Skills system. Always refer to the latest documentation and test changes in a development environment before deploying to production.
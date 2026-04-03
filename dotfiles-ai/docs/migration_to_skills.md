# Migration Guide: From Standalone Scripts to Letta Server Skills

**Version**: 1.0.0  
**Purpose**: Guide for migrating from standalone scripts to the new Letta Server Skills system  
**Audience**: Existing users with standalone scripts

## 🎯 Overview

This guide helps you migrate from standalone memory management scripts to the new Letta Server Skills system. The skills system provides better integration, reusability, and maintainability.

## 📋 Migration Checklist

- [ ] Identify existing standalone scripts
- [ ] Map scripts to equivalent skills
- [ ] Update agent configurations
- [ ] Replace script calls with skill calls
- [ ] Test new skill integration
- [ ] Remove old script dependencies
- [ ] Update documentation

## 🔄 Script-to-Skill Mapping

### Memory Management Scripts

| Old Script | New Skill | Description |
|------------|-----------|-------------|
| `save_conversation_to_letta.py` | `store_conversation` | Save conversation history |
| `search_letta_memories.py` | `search_memories` | Search existing memories |
| `add_verification_memories.py` | `store_entity_extraction` | Store extracted entities |
| `get_memory_stats.py` | `get_memory_stats` | Get memory statistics |

### Server Management Scripts

| Old Script | New Skill | Description |
|------------|-----------|-------------|
| `check_server_health.py` | `check_server_health` | Monitor server health |
| `initialize_letta_server.py` | `initialize_server` | Setup server configuration |
| `backup_letta_data.py` | `backup_server_data` | Create data backups |
| `restore_letta_data.py` | `restore_server_data` | Restore from backups |

### Agent Management Scripts

| Old Script | New Skill | Description |
|------------|-----------|-------------|
| `setup_agent_memory.py` | `setup_agent_memory` | Configure agent memory |
| `sync_agent_context.py` | `sync_agent_context` | Synchronize agent context |
| `create_agent_profile.py` | `create_agent_profile` | Create agent profiles |

## 🚀 Migration Steps

### Step 1: Identify Existing Scripts

Find all standalone scripts in your project:

```bash
# Find memory management scripts
find /home/cbwinslow/workspace -name "*letta*.py" -type f

# Find agent management scripts  
find /home/cbwinslow/workspace -name "*agent*.py" -type f

# Find server management scripts
find /home/cbwinslow/infra -name "*server*.py" -type f
```

### Step 2: Map Scripts to Skills

Create a mapping document:

```yaml
# migration_mapping.yaml
scripts_to_migrate:
  - old_script: "save_conversation_to_letta.py"
    new_skill: "store_conversation"
    usage: "After every conversation"
    
  - old_script: "search_letta_memories.py"
    new_skill: "search_memories"
    usage: "Before starting tasks"
    
  - old_script: "add_verification_memories.py"
    new_skill: "store_entity_extraction"
    usage: "After entity extraction"
```

### Step 3: Update Agent Configurations

Replace script references with skill references:

**Before (Old Configuration):**
```yaml
# agents/opencode/config.yaml
tools:
  - file_system
  - terminal
  - search
  - /home/cbwinslow/workspace/scripts/save_conversation_to_letta.py
  - /home/cbwinslow/workspace/scripts/search_letta_memories.py
```

**After (New Configuration):**
```yaml
# agents/opencode/config.yaml
skills:
  - letta_server

tools:
  - file_system
  - terminal
  - search
  - letta_server.store_conversation
  - letta_server.search_memories

letta_server:
  server_url: "${LETTA_SERVER_URL}"
  api_key: "${LETTA_API_KEY}"
  agent_name: "opencode"
```

### Step 4: Replace Script Calls with Skill Calls

**Before (Using Scripts):**
```python
# old_agent_code.py
import subprocess

def handle_conversation(agent_name, conversation):
    # Process conversation
    response = process_conversation(conversation)
    
    # Save using script
    subprocess.run([
        "python", "/home/cbwinslow/workspace/scripts/save_conversation_to_letta.py",
        "--agent", agent_name,
        "--conversation", json.dumps(conversation)
    ])
    
    return response
```

**After (Using Skills):**
```python
# new_agent_code.py
from skills.letta_server import store_conversation

def handle_conversation(agent_name, conversation):
    # Process conversation
    response = process_conversation(conversation)
    
    # Save using skill
    memory_id = store_conversation({
        "agent_name": agent_name,
        "conversation_history": conversation,
        "tags": ["conversation", agent_name]
    })
    
    return response
```

### Step 5: Update Import Statements

**Before:**
```python
# old_imports.py
import sys
sys.path.append('/home/cbwinslow/workspace/scripts')
from save_conversation_to_letta import save_conversation_to_letta
from search_letta_memories import search_letta_memories
```

**After:**
```python
# new_imports.py
from skills.letta_server import (
    store_conversation,
    search_memories,
    check_server_health
)
```

### Step 6: Update Command Line Usage

**Before (Script Commands):**
```bash
# Old script usage
python /home/cbwinslow/workspace/scripts/save_conversation_to_letta.py \
    --agent opencode \
    --conversation "Hello world"

python /home/cbwinslow/workspace/scripts/search_letta_memories.py \
    --query "entity extraction" \
    --agent opencode
```

**After (Skill Usage):**
```python
# New skill usage in agent code
from skills.letta_server import store_conversation, search_memories

# Store conversation
memory_id = store_conversation({
    "agent_name": "opencode",
    "conversation_history": [{"role": "user", "content": "Hello world"}],
    "tags": ["conversation", "opencode"]
})

# Search memories
results = search_memories({
    "query": "entity extraction",
    "agent_name": "opencode"
})
```

## 🔄 Migration Examples

### Example 1: Memory Management Migration

**Old Implementation:**
```python
# old_memory_manager.py
import subprocess
import json

class OldMemoryManager:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.script_path = "/home/cbwinslow/workspace/scripts"
    
    def save_conversation(self, conversation):
        """Save conversation using standalone script"""
        cmd = [
            "python", f"{self.script_path}/save_conversation_to_letta.py",
            "--agent", self.agent_name,
            "--conversation", json.dumps(conversation)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def search_memories(self, query):
        """Search memories using standalone script"""
        cmd = [
            "python", f"{self.script_path}/search_letta_memories.py",
            "--query", query,
            "--agent", self.agent_name
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout) if result.returncode == 0 else []
```

**New Implementation:**
```python
# new_memory_manager.py
from skills.letta_server import store_conversation, search_memories

class NewMemoryManager:
    def __init__(self, agent_name):
        self.agent_name = agent_name
    
    def save_conversation(self, conversation):
        """Save conversation using skills"""
        try:
            memory_id = store_conversation({
                "agent_name": self.agent_name,
                "conversation_history": conversation,
                "tags": ["conversation", self.agent_name]
            })
            return True
        except Exception as e:
            print(f"Failed to save conversation: {e}")
            return False
    
    def search_memories(self, query):
        """Search memories using skills"""
        try:
            results = search_memories({
                "query": query,
                "agent_name": self.agent_name
            })
            return results
        except Exception as e:
            print(f"Failed to search memories: {e}")
            return []
```

### Example 2: Server Management Migration

**Old Implementation:**
```python
# old_server_manager.py
import subprocess
import os

class OldServerManager:
    def __init__(self):
        self.script_path = "/home/cbwinslow/infra/scripts"
    
    def check_health(self):
        """Check server health using script"""
        cmd = ["python", f"{self.script_path}/check_server_health.py"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def backup_data(self, backup_path):
        """Backup data using script"""
        cmd = [
            "python", f"{self.script_path}/backup_letta_data.py",
            "--path", backup_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
```

**New Implementation:**
```python
# new_server_manager.py
from skills.letta_server import check_server_health, backup_server_data

class NewServerManager:
    def __init__(self):
        pass
    
    def check_health(self):
        """Check server health using skills"""
        try:
            health = check_server_health({})
            return health["status"] == "healthy"
        except Exception as e:
            print(f"Failed to check server health: {e}")
            return False
    
    def backup_data(self, backup_path):
        """Backup data using skills"""
        try:
            result = backup_server_data({"backup_path": backup_path})
            return result["status"] == "success"
        except Exception as e:
            print(f"Failed to backup data: {e}")
            return False
```

### Example 3: Agent Integration Migration

**Old Implementation:**
```python
# old_agent_setup.py
import subprocess
import json

def setup_agent_memory_old(agent_name, config):
    """Setup agent memory using script"""
    cmd = [
        "python", "/home/cbwinslow/workspace/scripts/setup_agent_memory.py",
        "--agent", agent_name,
        "--config", json.dumps(config)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```

**New Implementation:**
```python
# new_agent_setup.py
from skills.letta_server import setup_agent_memory

def setup_agent_memory_new(agent_name, config):
    """Setup agent memory using skills"""
    try:
        result = setup_agent_memory({
            "agent_name": agent_name,
            "memory_config": config["memory"],
            "skills": config["skills"]
        })
        return result["status"] == "success"
    except Exception as e:
        print(f"Failed to setup agent memory: {e}")
        return False
```

## 🧪 Testing the Migration

### Test 1: Verify Skill Functionality

```python
# test_migration.py
from skills.letta_server import (
    store_conversation,
    search_memories,
    check_server_health
)

def test_skill_functionality():
    """Test that skills work correctly"""
    
    # Test conversation storage
    test_conversation = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    
    memory_id = store_conversation({
        "agent_name": "test_agent",
        "conversation_history": test_conversation,
        "tags": ["test"]
    })
    
    print(f"Conversation stored with ID: {memory_id}")
    
    # Test memory search
    results = search_memories({
        "query": "Hello",
        "agent_name": "test_agent"
    })
    
    print(f"Search returned {len(results)} results")
    
    # Test server health
    health = check_server_health({})
    print(f"Server health: {health['status']}")
    
    return True
```

### Test 2: Compare Old vs New Results

```python
# compare_migration.py
import subprocess
import json
from skills.letta_server import store_conversation, search_memories

def compare_old_vs_new():
    """Compare results between old scripts and new skills"""
    
    test_data = {
        "agent_name": "comparison_test",
        "conversation": [
            {"role": "user", "content": "Test message"},
            {"role": "assistant", "content": "Test response"}
        ]
    }
    
    # Test old script
    old_cmd = [
        "python", "/home/cbwinslow/workspace/scripts/save_conversation_to_letta.py",
        "--agent", test_data["agent_name"],
        "--conversation", json.dumps(test_data["conversation"])
    ]
    old_result = subprocess.run(old_cmd, capture_output=True, text=True)
    
    # Test new skill
    new_result = store_conversation({
        "agent_name": test_data["agent_name"],
        "conversation_history": test_data["conversation"],
        "tags": ["test"]
    })
    
    print(f"Old script result: {old_result.returncode == 0}")
    print(f"New skill result: {new_result is not None}")
    
    return old_result.returncode == 0 and new_result is not None
```

### Test 3: Integration Testing

```python
# integration_test.py
from skills.letta_server import (
    setup_agent_memory,
    store_conversation,
    search_memories,
    get_agent_status
)

def test_full_integration():
    """Test complete integration workflow"""
    
    agent_name = "integration_test_agent"
    
    # 1. Setup agent memory
    setup_result = setup_agent_memory({
        "agent_name": agent_name,
        "memory_config": {
            "backend": "letta_server",
            "default_ttl_days": 30,
            "max_memory_size_mb": 50
        },
        "skills": ["memory_management", "conversation_logging"]
    })
    
    if setup_result["status"] != "success":
        print("Agent setup failed")
        return False
    
    # 2. Store conversation
    conversation = [
        {"role": "user", "content": "What is AI?"},
        {"role": "assistant", "content": "AI is artificial intelligence."}
    ]
    
    memory_id = store_conversation({
        "agent_name": agent_name,
        "conversation_history": conversation,
        "tags": ["test", "ai"]
    })
    
    if not memory_id:
        print("Conversation storage failed")
        return False
    
    # 3. Search memories
    results = search_memories({
        "query": "AI",
        "agent_name": agent_name
    })
    
    if len(results) == 0:
        print("Memory search failed")
        return False
    
    # 4. Check agent status
    status = get_agent_status({"agent_name": agent_name})
    
    if status["status"] != "active":
        print("Agent status check failed")
        return False
    
    print("Integration test passed!")
    return True
```

## 🗑️ Cleanup After Migration

### Remove Old Scripts

```bash
# Backup old scripts before removal
mkdir /home/cbwinslow/backup/old_scripts
cp /home/cbwinslow/workspace/scripts/*.py /home/cbwinslow/backup/old_scripts/

# Remove old scripts (after verifying migration)
rm /home/cbwinslow/workspace/scripts/save_conversation_to_letta.py
rm /home/cbwinslow/workspace/scripts/search_letta_memories.py
rm /home/cbwinslow/workspace/scripts/add_verification_memories.py
```

### Update Documentation

```yaml
# Update project documentation
# docs/migration_complete.md
migration_complete: true
old_scripts_removed: true
skills_implemented: true
agents_updated: ["opencode", "cline", "kilocode"]
test_results: "All tests passed"
```

### Update CI/CD Pipelines

```yaml
# .github/workflows/migration.yml
name: Migration Verification
on: [push, pull_request]

jobs:
  verify_migration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Test Skills Integration
        run: |
          python test_migration.py
          python integration_test.py
      
      - name: Verify Old Scripts Removed
        run: |
          if [ -f "/home/cbwinslow/workspace/scripts/save_conversation_to_letta.py" ]; then
            echo "Old script still exists!"
            exit 1
          fi
```

## 📊 Migration Benefits

### Before (Standalone Scripts)
- ❌ **Duplication**: Each agent had separate script calls
- ❌ **Maintenance**: Scripts needed to be updated individually
- ❌ **Integration**: Poor integration with agent frameworks
- ❌ **Monitoring**: Difficult to monitor and debug
- ❌ **Reusability**: Scripts couldn't be easily shared

### After (Skills System)
- ✅ **Centralized**: All skills in one place
- ✅ **Maintainable**: Single point of updates
- ✅ **Integrated**: Seamless framework integration
- ✅ **Observable**: Better monitoring and debugging
- ✅ **Reusable**: Skills shared across all agents

## 🆘 Troubleshooting Migration Issues

### Issue 1: Import Errors
```python
# Error: ModuleNotFoundError: No module named 'skills.letta_server'
# Solution: Ensure skills directory is in Python path

import sys
sys.path.append('/home/cbwinslow/dotfiles/ai')
from skills.letta_server import store_conversation
```

### Issue 2: Configuration Errors
```python
# Error: Missing required configuration
# Solution: Check agent configuration

# Verify configuration
import os
print(f"LETTA_SERVER_URL: {os.getenv('LETTA_SERVER_URL')}")
print(f"LETTA_API_KEY: {os.getenv('LETTA_API_KEY')}")
```

### Issue 3: Permission Errors
```python
# Error: Permission denied accessing database
# Solution: Check database permissions

# Test database connection
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

### Issue 4: Skill Not Found
```python
# Error: AttributeError: module 'skills.letta_server' has no attribute 'store_conversation'
# Solution: Check skill implementation

# Verify skill exists
import skills.letta_server
print(dir(skills.letta_server))
```

## 📞 Migration Support

For migration support:

1. **Review Migration Guide**: Check this document for common issues
2. **Test Incrementally**: Migrate one agent at a time
3. **Compare Results**: Verify old and new implementations produce same results
4. **Monitor Performance**: Check that skills perform as well as scripts
5. **Update Team**: Ensure all team members understand new system

---

**Note**: This migration guide helps you transition smoothly from standalone scripts to the new Letta Server Skills system. Take your time with the migration and test thoroughly at each step.
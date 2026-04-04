# Global Agent Initialization Rules

**Version**: 1.0.0  
**Purpose**: Universal rules that must be loaded into every AI agent instance  
**Scope**: All AI agents (OpenCode, Gemini, Claude, Cline, KiloCode, VS Code, Windsurf, OpenClaw)

## 🎯 Core Principles

### 1. **Memory First Policy**
- **MANDATORY**: Every conversation must be saved to Letta memory system
- **MANDATORY**: All entities, decisions, and important information must be stored
- **MANDATORY**: Use Epstein Memory System for all persistent storage

### 2. **Centralized Configuration**
- **MANDATORY**: All agents must load configurations from `/home/cbwinslow/dotfiles/ai/`
- **MANDATORY**: Use environment variables for sensitive data
- **PREFERRED**: Use shared skills and tools from the centralized system

### 3. **Cross-Agent Collaboration**
- **REQUIRED**: Search existing memories before starting new tasks
- **REQUIRED**: Store results for future agent use
- **REQUIRED**: Use consistent naming conventions and tags

## 📋 **Universal Agent Requirements**

### **Memory Management Requirements**

```python
# Every agent MUST implement these memory operations:

def save_conversation_to_letta(agent_name, conversation_history):
    """Save entire conversation to Letta system"""
    # Implementation using epstein_memory package
    pass

def search_existing_memories(query, agent_name=None):
    """Search for relevant existing information"""
    # Implementation using epstein_memory package
    pass

def store_entity_extraction_results(entities, context):
    """Store extracted entities for future use"""
    # Implementation using epstein_memory package
    pass
```

### **Configuration Loading Requirements**

```yaml
# Every agent MUST load these configurations:

memory_backend: "epstein_memory"
memory_config:
  server_url: "${LETTA_SERVER_URL}"
  api_key: "${LETTA_API_KEY}"
  database_url: "${DATABASE_URL}"

skills:
  - "memory_management"
  - "entity_extraction"
  - "conversation_logging"
  - "cross_agent_search"

tools:
  - "file_system"
  - "terminal"
  - "search"
  - "memory_operations"
```

### **Agent Initialization Sequence**

1. **Load Global Rules** (THIS FILE)
2. **Load Agent-Specific Configuration**
3. **Initialize Memory System**
4. **Load Shared Skills and Tools**
5. **Verify Letta Connection**
6. **Start Task with Memory Search**

## 🔧 **Implementation Guidelines**

### **For LangChain Agents**

```python
from epstein_memory import EpsteinMemory
from langchain.memory import ConversationBufferMemory

class GlobalAgentRules:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.memory = EpsteinMemory(agent_name)
        
    def initialize_agent(self):
        """Initialize agent with global rules"""
        # 1. Load global configurations
        self.load_global_configs()
        
        # 2. Initialize memory system
        self.memory.initialize()
        
        # 3. Load shared skills
        self.load_shared_skills()
        
        # 4. Verify Letta connection
        self.verify_letta_connection()
        
    def save_conversation(self, conversation):
        """Universal conversation saving"""
        return self.memory.save_conversation(conversation)
```

### **For CrewAI Agents**

```python
from crewai import Agent
from epstein_memory import get_agent_context, store_agent_context

class EpsteinAgent(Agent):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.global_rules = GlobalAgentRules(name)
        self.global_rules.initialize_agent()
        
    def _execute_task(self, task):
        """Execute task with global rules"""
        # 1. Search existing memories
        relevant_memories = self.global_rules.search_memories(task.description)
        
        # 2. Execute task
        result = super()._execute_task(task)
        
        # 3. Save results to memory
        self.global_rules.save_results(task, result)
        
        return result
```

### **For AutoGen Agents**

```python
from autogen import AssistantAgent
from epstein_memory import store_agent_context

class EpsteinAssistant(AssistantAgent):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.global_rules = GlobalAgentRules(name)
        self.global_rules.initialize_agent()
        
    def _process_message(self, message):
        """Process message with global rules"""
        # 1. Save incoming message
        self.global_rules.save_message(message)
        
        # 2. Process message
        response = super()._process_message(message)
        
        # 3. Save response
        self.global_rules.save_response(response)
        
        return response
```

## 📚 **Required Skills for All Agents**

### **1. Memory Management Skill**
```yaml
# skills/memory_management/SKILL.md
name: "memory_management"
description: "Universal memory operations for all agents"

operations:
  - name: "save_conversation"
    description: "Save entire conversation to Letta system"
    parameters:
      - name: "agent_name"
        type: "string"
      - name: "conversation"
        type: "list"
    returns: "memory_id"
  
  - name: "search_memories"
    description: "Search existing memories for relevant information"
    parameters:
      - name: "query"
        type: "string"
      - name: "agent_name"
        type: "string"
    returns: "list of memories"
  
  - name: "store_entity"
    description: "Store extracted entities"
    parameters:
      - name: "entities"
        type: "list"
      - name: "context"
        type: "string"
    returns: "entity_id"
```

### **2. Cross-Agent Communication Skill**
```yaml
# skills/cross_agent_communication/SKILL.md
name: "cross_agent_communication"
description: "Enable communication and knowledge sharing between agents"

operations:
  - name: "broadcast_result"
    description: "Share results with other agents"
    parameters:
      - name: "result"
        type: "string"
      - name: "tags"
        type: "list"
    returns: "broadcast_id"
  
  - name: "request_assistance"
    description: "Request help from specialized agents"
    parameters:
      - name: "task_description"
        type: "string"
      - name: "required_skills"
        type: "list"
    returns: "response"
```

## 🚨 **Enforcement Rules**

### **Mandatory Operations**
1. **Every agent must save conversations** - No exceptions
2. **Every agent must search before creating** - Avoid duplication
3. **Every agent must use centralized configs** - Maintain consistency
4. **Every agent must follow naming conventions** - Enable searchability

### **Prohibited Actions**
1. **No local-only storage** - Everything must go to Letta
2. **No hardcoded configurations** - Use environment variables
3. **No agent isolation** - Always share knowledge
4. **No inconsistent naming** - Follow established conventions

### **Quality Standards**
1. **Memory entries must be tagged** - Enable future retrieval
2. **Conversations must be complete** - No partial saves
3. **Entities must be contextualized** - Include source information
4. **Results must be actionable** - Enable future automation

## 🔗 **Integration Points**

### **Shell Integration**
```bash
# Add to ~/.zshrc or ~/.bashrc
export AI_SKILLS_SYSTEM="/home/cbwinslow/dotfiles/ai"
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_API_KEY="${LETTA_API_KEY}"

# Auto-load global rules for all agents
alias opencode="opencode --init-rules $AI_SKILLS_SYSTEM/global_rules"
alias gemini="gemini --init-rules $AI_SKILLS_SYSTEM/global_rules"
alias claude="claude --init-rules $AI_SKILLS_SYSTEM/global_rules"
```

### **IDE Integration**
```json
// VS Code settings.json
{
  "aiAgents.globalRules": "/home/cbwinslow/dotfiles/ai/global_rules",
  "aiAgents.memoryBackend": "epstein_memory",
  "aiAgents.autoSaveConversations": true
}
```

### **Framework Integration**
```yaml
# Global framework configuration
global_agent_config:
  memory_backend: "epstein_memory"
  rules_file: "/home/cbwinslow/dotfiles/ai/global_rules/agent_init_rules.md"
  auto_initialize: true
  required_skills:
    - "memory_management"
    - "cross_agent_communication"
    - "entity_extraction"
```

## 📖 **Usage Examples**

### **Example 1: New Agent Setup**
```python
# agent_setup.py
from epstein_memory import initialize_agent_with_rules

def setup_new_agent(agent_name, agent_type):
    """Setup any new agent with global rules"""
    agent = initialize_agent_with_rules(
        agent_name=agent_name,
        agent_type=agent_type,
        rules_file="/home/cbwinslow/dotfiles/ai/global_rules/agent_init_rules.md"
    )
    
    # Agent is now fully configured with global rules
    return agent
```

### **Example 2: Conversation Saving**
```python
# conversation_handler.py
from epstein_memory import save_conversation_to_letta

def handle_conversation(agent_name, conversation):
    """Universal conversation handler"""
    # Save to Letta system
    memory_id = save_conversation_to_letta(agent_name, conversation)
    
    # Log completion
    print(f"Conversation saved to Letta with ID: {memory_id}")
    
    return memory_id
```

### **Example 3: Memory Search**
```python
# memory_searcher.py
from epstein_memory import search_memories

def search_agent_memories(agent_name, query, tags=None):
    """Search memories for specific agent or all agents"""
    results = search_memories(
        query=query,
        agent_name=agent_name,
        tags=tags
    )
    
    return results
```

## 🔄 **Maintenance and Updates**

### **Rule Updates**
1. **Version Control**: All rule changes must be committed to Git
2. **Testing**: New rules must be tested before deployment
3. **Rollback**: Previous versions must be available for rollback
4. **Documentation**: All changes must be documented

### **Agent Updates**
1. **Automatic Loading**: Agents should auto-load latest rules
2. **Validation**: Rules should be validated on agent startup
3. **Fallback**: Agents should have fallback behavior if rules fail
4. **Monitoring**: Rule effectiveness should be monitored

## 📋 **Checklist for New Agents**

- [ ] Load global rules file
- [ ] Initialize Epstein Memory System
- [ ] Configure Letta connection
- [ ] Load required skills
- [ ] Set up conversation saving
- [ ] Configure memory search
- [ ] Test cross-agent communication
- [ ] Validate configuration
- [ ] Document agent-specific rules
- [ ] Add to monitoring system

## 🎯 **Success Metrics**

1. **100% Conversation Coverage**: All conversations saved to Letta
2. **Zero Duplication**: No duplicate work due to memory search
3. **100% Rule Compliance**: All agents follow global rules
4. **Cross-Agent Success**: Successful knowledge sharing between agents
5. **System Reliability**: 99.9% uptime for memory system

---

**Note**: This file must be loaded by every AI agent instance. Any agent that does not comply with these rules is considered non-standard and should be updated to comply.
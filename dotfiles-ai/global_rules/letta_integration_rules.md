# AI Assistant System Prompt Update
# Letta Integration & Automatic Memory Management
# Location: ~/dotfiles/ai/global_rules/letta_integration_rules.md

## 🎯 **MANDATORY: Letta Self-Hosted Server Integration**

**ALL AI assistants MUST automatically use the self-hosted Letta server for memory management.**

### **Automatic Memory Operations (Every Conversation)**

You MUST automatically:

1. **Save Full Conversation Logs**
   - Every user message and your response MUST be saved to Letta
   - Use `letta-memory-cli save --type conversation` or Python API
   - Include timestamps and context

2. **Create Useful Memories Automatically**
   Extract and save:
   - **Decisions**: Important choices made during conversation
   - **Action Items**: Tasks identified for future action
   - **Key Facts**: Important information about projects, code, preferences
   - **Code Changes**: Significant code written or modified
   - **File Paths**: Important files discussed or modified
   - **Commands**: Shell commands that were run or should be run

3. **Search Before Acting**
   - ALWAYS search existing Letta memories before starting new tasks
   - Check for prior context, decisions, or relevant information
   - Reference found memories in your response

### **Memory Types to Use**

| Type | Purpose | TTL |
|------|---------|-----|
| `core` | Permanent knowledge (API keys, project structure) | Never |
| `archival` | Full conversation logs, important context | 365 days |
| `context` | Session-specific working memory | 30 days |
| `persona` | Your agent personality/settings | Never |
| `human` | User preferences, working style | Never |

### **How to Save Memories**

#### CLI Method:
```bash
# Save conversation
letta-memory-cli save --type conversation --content "User asked about X, I suggested Y"

# Save decision
letta-memory-cli save --type decision --content "Decided to use OpenRouter free models" --context "All agents updated"

# Save action item
letta-memory-cli save --type action_item --content "Update shell aliases" --priority high

# Save note
letta-memory-cli save --type generic --memory-type archival --content "Important info" --tags note project
```

#### Python Method:
```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="assistant")

# Save conversation
letta.save_conversation(messages, tags=["task", "coding"])

# Create memory from decision
letta.create_memory_from_decision("Using OpenRouter free", "Cost optimization")

# Search memories
results = letta.search_memories("entity extraction")
```

### **Entity Extraction (Automatic)**

You MUST automatically extract and store:
- **Code blocks** - Any code written or modified
- **File paths** - Any files discussed
- **Commands** - Shell commands run or suggested
- **URLs** - Any web resources referenced
- **Names** - Projects, tools, people mentioned
- **Dates/Deadlines** - Any time-sensitive information

### **Cross-Agent Collaboration**

When relevant:
- Search memories from other agents (opencode, cline, etc.)
- Share results of your work via Letta
- Build on prior work from other agents

### **Example Workflow**

```
1. User asks question
   ↓
2. Search Letta for prior context
   ↓
3. Answer question
   ↓
4. Extract entities (code, files, commands, etc.)
   ↓
5. Save full conversation to Letta
   ↓
6. Create memories for:
   - Decisions made
   - Action items identified
   - Key facts learned
   ↓
7. Confirm memories saved to user
```

### **Confirmation to User**

After saving memories, briefly confirm:
```
[Memory saved: 1 conversation, 3 entities, 1 decision, 2 action items]
```

---

## 🚨 **Enforcement**

**These rules are MANDATORY for all AI assistants using this system.**

Failure to save conversations and create memories = non-compliant agent.

# Conversation Logging Skill
# Automatic conversation logging with decision and action item extraction
# Location: ~/dotfiles/ai/skills/conversation_logging/SKILL.md

name: conversation_logging
description: "Automatic conversation logging with decision and action item extraction"
version: 1.0.0

## Overview

This skill provides automatic conversation logging capabilities for AI agents. It:
- Saves entire conversations to Letta archival memory
- Extracts key decisions and action items
- Creates memories for important moments
- Enables conversation search and recall

## Operations

### `log_conversation`
Log an entire conversation to Letta memory.

**Parameters:**
- `messages` (list): List of conversation messages with role and content
- `agent_name` (string): Name of the agent
- `tags` (list, optional): Tags for categorization
- `extract_decisions` (bool, optional): Extract key decisions (default: True)
- `extract_action_items` (bool, optional): Extract action items (default: True)

**Example:**
```python
conversation_logging.log_conversation(
    messages=[
        {"role": "user", "content": "What should we do next?"},
        {"role": "assistant", "content": "We should implement the new feature."}
    ],
    agent_name="opencode",
    tags=["planning", "development"]
)
```

### `extract_decisions`
Extract key decisions from conversation.

**Parameters:**
- `messages` (list): List of conversation messages
- `agent_name` (string): Name of the agent

**Returns:** List of extracted decisions

### `extract_action_items`
Extract action items from conversation.

**Parameters:**
- `messages` (list): List of conversation messages
- `agent_name` (string): Name of the agent

**Returns:** List of extracted action items

### `search_conversations`
Search for past conversations.

**Parameters:**
- `query` (string): Search query
- `agent_name` (string, optional): Filter by agent
- `tags` (list, optional): Filter by tags
- `limit` (int, optional): Max results (default: 10)

**Returns:** List of matching conversations

### `get_conversation_summary`
Get a summary of a conversation.

**Parameters:**
- `conversation_id` (string): Conversation ID

**Returns:** Conversation summary

## Automatic Behavior

When this skill is loaded, the agent automatically:

1. **Logs every conversation** to Letta archival memory
2. **Extracts key decisions** and stores them as separate memories
3. **Extracts action items** and stores them as tasks
4. **Tags conversations** for easy retrieval

## Decision Extraction Patterns

The skill extracts decisions based on these patterns:
- "We decided to..."
- "The plan is to..."
- "We will..."
- "Let's..."
- "I suggest..."
- "We should..."
- "Going forward..."

## Action Item Extraction Patterns

The skill extracts action items based on these patterns:
- "TODO:"
- "Action item:"
- "Need to..."
- "Must..."
- "Should..."
- "Will do..."
- "Assigned to..."

## Storage Format

Conversations are stored with this structure:
```json
{
  "memory_type": "conversation",
  "title": "Conversation with [agent_name]",
  "content": "Full conversation text",
  "metadata": {
    "agent_name": "agent_name",
    "message_count": 10,
    "decisions": ["decision1", "decision2"],
    "action_items": ["action1", "action2"],
    "timestamp": "2026-03-24T12:00:00Z"
  },
  "tags": ["conversation", "agent_name", "decision", "action_item"]
}
```

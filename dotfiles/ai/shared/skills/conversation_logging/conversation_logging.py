"""
Conversation Logging Skill Implementation

Provides automatic conversation logging with decision and action item extraction.
This skill replaces standalone conversation logging scripts with reusable, integrated functions.
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationLogger:
    """Automatic conversation logging with decision and action item extraction."""

    def __init__(self):
        # Patterns for decision extraction
        self.decision_patterns = [
            r"we decided to (.+?)(?:\.|$)",
            r"the plan is to (.+?)(?:\.|$)",
            r"we will (.+?)(?:\.|$)",
            r"let's (.+?)(?:\.|$)",
            r"i suggest (.+?)(?:\.|$)",
            r"we should (.+?)(?:\.|$)",
            r"going forward[,.] (.+?)(?:\.|$)",
            r"from now on[,.] (.+?)(?:\.|$)",
            r"the decision is to (.+?)(?:\.|$)",
            r"we're going to (.+?)(?:\.|$)",
        ]

        # Patterns for action item extraction
        self.action_patterns = [
            r"todo[:\s]+(.+?)(?:\.|$)",
            r"action item[:\s]+(.+?)(?:\.|$)",
            r"need to (.+?)(?:\.|$)",
            r"must (.+?)(?:\.|$)",
            r"should (.+?)(?:\.|$)",
            r"will do (.+?)(?:\.|$)",
            r"assigned to (.+?)(?:\.|$)",
            r"next step[:\s]+(.+?)(?:\.|$)",
            r"follow up[:\s]+(.+?)(?:\.|$)",
            r"remember to (.+?)(?:\.|$)",
        ]

    def extract_decisions(self, messages: List[Dict[str, str]]) -> List[str]:
        """
        Extract key decisions from conversation messages.

        Args:
            messages: List of conversation messages

        Returns:
            List of extracted decisions
        """
        decisions = []

        for message in messages:
            content = message.get("content", "")
            if not content:
                continue

            # Check each decision pattern
            for pattern in self.decision_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    decision = match.group(1).strip()
                    if decision and len(decision) > 10:  # Minimum length check
                        decisions.append(decision)

        # Remove duplicates while preserving order
        seen = set()
        unique_decisions = []
        for decision in decisions:
            if decision not in seen:
                seen.add(decision)
                unique_decisions.append(decision)

        return unique_decisions

    def extract_action_items(self, messages: List[Dict[str, str]]) -> List[str]:
        """
        Extract action items from conversation messages.

        Args:
            messages: List of conversation messages

        Returns:
            List of extracted action items
        """
        action_items = []

        for message in messages:
            content = message.get("content", "")
            if not content:
                continue

            # Check each action pattern
            for pattern in self.action_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    action = match.group(1).strip()
                    if action and len(action) > 5:  # Minimum length check
                        action_items.append(action)

        # Remove duplicates while preserving order
        seen = set()
        unique_actions = []
        for action in action_items:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)

        return unique_actions

    def format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """
        Format conversation messages into readable text.

        Args:
            messages: List of conversation messages

        Returns:
            Formatted conversation text
        """
        formatted = []
        for message in messages:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            formatted.append(f"{role.upper()}: {content}\n")

        return "\n".join(formatted)

    def log_conversation(
        self,
        messages: List[Dict[str, str]],
        agent_name: str,
        tags: List[str] = None,
        extract_decisions: bool = True,
        extract_action_items: bool = True,
    ) -> Dict[str, Any]:
        """
        Log an entire conversation to Letta memory.

        Args:
            messages: List of conversation messages
            agent_name: Name of the agent
            tags: Tags for categorization
            extract_decisions: Whether to extract key decisions
            extract_action_items: Whether to extract action items

        Returns:
            Dict with operation results
        """
        try:
            from cli_operations import store_letta_memory

            # Prepare tags
            memory_tags = tags or []
            memory_tags.extend(["conversation", agent_name])

            # Extract decisions and action items
            decisions = []
            action_items = []

            if extract_decisions:
                decisions = self.extract_decisions(messages)
                if decisions:
                    memory_tags.append("decision")

            if extract_action_items:
                action_items = self.extract_action_items(messages)
                if action_items:
                    memory_tags.append("action_item")

            # Format conversation
            conversation_text = self.format_conversation(messages)

            # Prepare metadata
            metadata = {
                "agent_name": agent_name,
                "message_count": len(messages),
                "decisions": decisions,
                "action_items": action_items,
                "timestamp": datetime.now().isoformat(),
            }

            # Store conversation
            result = store_letta_memory(
                agent_id=agent_name,
                text=f"Conversation with {agent_name}:\n\n{conversation_text}",
                tags=memory_tags,
            )

            if not result["success"]:
                return result

            # Store decisions separately if any
            decision_memories = []
            if decisions:
                for decision in decisions:
                    decision_result = store_letta_memory(
                        agent_id=agent_name,
                        text=f"Decision: {decision}",
                        tags=["decision", agent_name, "conversation"],
                    )
                    if decision_result["success"]:
                        decision_memories.append(decision_result)

            # Store action items separately if any
            action_memories = []
            if action_items:
                for action in action_items:
                    action_result = store_letta_memory(
                        agent_id=agent_name,
                        text=f"Action Item: {action}",
                        tags=["action_item", agent_name, "todo"],
                    )
                    if action_result["success"]:
                        action_memories.append(action_result)

            return {
                "success": True,
                "message": "Conversation logged successfully",
                "agent_name": agent_name,
                "decisions_extracted": len(decisions),
                "action_items_extracted": len(action_items),
                "decision_memories": len(decision_memories),
                "action_memories": len(action_memories),
            }

        except Exception as e:
            logger.error(f"Failed to log conversation: {e}")
            return {"success": False, "error": str(e)}

    def search_conversations(
        self, query: str = None, agent_name: str = None, tags: List[str] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for past conversations.

        Args:
            query: Search query
            agent_name: Filter by agent
            tags: Filter by tags
            limit: Max results

        Returns:
            Search results
        """
        try:
            from cli_operations import advanced_memory_search

            # Prepare search tags
            search_tags = tags or []
            if agent_name:
                search_tags.append(agent_name)
            search_tags.append("conversation")

            # Use advanced search
            results = advanced_memory_search(
                query=query, search_type="text", tags=search_tags, limit=limit
            )

            return results

        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return {"success": False, "error": str(e)}

    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get a summary of a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation summary
        """
        # This would require access to the specific memory
        # For now, return a placeholder
        return {
            "success": True,
            "message": "Conversation summary retrieval not yet implemented",
            "conversation_id": conversation_id,
        }


# Create a global instance
conversation_logger = ConversationLogger()


# Export functions for use in skills
def log_conversation(
    messages: List[Dict[str, str]],
    agent_name: str,
    tags: List[str] = None,
    extract_decisions: bool = True,
    extract_action_items: bool = True,
) -> Dict[str, Any]:
    """Log an entire conversation to Letta memory."""
    return conversation_logger.log_conversation(
        messages, agent_name, tags, extract_decisions, extract_action_items
    )


def extract_decisions(messages: List[Dict[str, str]]) -> List[str]:
    """Extract key decisions from conversation."""
    return conversation_logger.extract_decisions(messages)


def extract_action_items(messages: List[Dict[str, str]]) -> List[str]:
    """Extract action items from conversation."""
    return conversation_logger.extract_action_items(messages)


def search_conversations(
    query: str = None, agent_name: str = None, tags: List[str] = None, limit: int = 10
) -> Dict[str, Any]:
    """Search for past conversations."""
    return conversation_logger.search_conversations(query, agent_name, tags, limit)


def get_conversation_summary(conversation_id: str) -> Dict[str, Any]:
    """Get a summary of a conversation."""
    return conversation_logger.get_conversation_summary(conversation_id)

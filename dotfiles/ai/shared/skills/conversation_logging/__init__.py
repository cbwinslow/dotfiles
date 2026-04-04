"""
Conversation Logging Skill Package

Provides automatic conversation logging with decision and action item extraction.
This skill replaces standalone conversation logging scripts with reusable, integrated functions.
"""

from .conversation_logging import (
    log_conversation,
    extract_decisions,
    extract_action_items,
    search_conversations,
    get_conversation_summary,
    ConversationLogger,
)

__version__ = "1.0.0"
__all__ = [
    "log_conversation",
    "extract_decisions",
    "extract_action_items",
    "search_conversations",
    "get_conversation_summary",
    "ConversationLogger",
]

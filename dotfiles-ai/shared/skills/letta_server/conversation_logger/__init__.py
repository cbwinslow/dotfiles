"""
Conversation Logger - Save AI conversation logs to Letta server.

This module provides utilities for capturing, processing, and storing
AI conversation logs in the Letta server for persistent memory.
"""

__version__ = "1.0.0"
__author__ = "Epstein Files Analysis Project"

from .logger import ConversationLogger
from .processor import ConversationProcessor
from .letta_client import LettaClient
from .config import Config

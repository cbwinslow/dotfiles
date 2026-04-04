"""
Letta Server Client - Interface for saving conversations to Letta server.
"""

import subprocess
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class LettaClient:
    """Client for interacting with Letta server CLI."""

    def __init__(self, agent_id: str = None, letta_path: str = "/home/cbwinslow/bin/letta"):
        """Initialize Letta client.

        Args:
            agent_id: Agent ID to use (default from config)
            letta_path: Path to letta CLI executable
        """
        self.agent_id = agent_id or "agent-1167f15a-a10a-4595-b962-ec0f372aae0d"
        self.letta_path = letta_path
        self.logger = logging.getLogger(__name__)

    def test_connection(self) -> bool:
        """Test connection to Letta server."""
        try:
            result = subprocess.run(
                [self.letta_path, "health"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to connect to Letta server: {e}")
            return False

    def insert_memory(self, text: str, tags: List[str] = None) -> bool:
        """Insert a memory into archival memory.

        Args:
            text: Memory text content
            tags: Optional list of tags

        Returns:
            True if successful, False otherwise
        """
        try:
            # Format tags as comma-separated string
            tags_str = ",".join(tags) if tags else ""

            cmd = [self.letta_path, "archival-insert", self.agent_id, text]
            if tags_str:
                cmd.append(tags_str)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.logger.info(f"✅ Memory inserted successfully")
                return True
            else:
                self.logger.error(f"❌ Failed to insert memory: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Command timed out")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error inserting memory: {e}")
            return False

    def insert_conversation_summary(self, conversation_data: Dict) -> bool:
        """Insert a conversation summary as archival memory.

        Args:
            conversation_data: Dictionary with conversation information

        Returns:
            True if successful
        """
        summary = self._create_conversation_summary(conversation_data)
        tags = self._extract_tags(conversation_data)

        return self.insert_memory(summary, tags)

    def insert_key_decisions(self, decisions: List[str], session_id: str) -> bool:
        """Insert key decisions from a conversation.

        Args:
            decisions: List of decision strings
            session_id: Session identifier

        Returns:
            True if successful
        """
        if not decisions:
            return True

        decisions_text = "\n".join(f"- {d}" for d in decisions)
        text = f"KEY DECISIONS from session {session_id}:\n\n{decisions_text}"
        tags = ["decisions", "session", session_id]

        return self.insert_memory(text, tags)

    def update_persona(self, content: str, label: str = "persona") -> bool:
        """Update agent persona or human memory.

        Args:
            content: New content for the memory block
            label: Memory block label (persona or human)

        Returns:
            True if successful
        """
        try:
            cmd = [self.letta_path, "memory-update", self.agent_id, label, content]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.logger.info(f"✅ Agent {label} updated successfully")
                return True
            else:
                self.logger.warning(f"⚠️ Could not update agent {label}: {result.stderr}")
                return False

        except Exception as e:
            self.logger.warning(f"⚠️ Could not update agent {label}: {e}")
            return False

    def search_memories(self, query: str) -> List[Dict]:
        """Search archival memories.

        Args:
            query: Search query

        Returns:
            List of memory dictionaries
        """
        try:
            cmd = [self.letta_path, "archival-search", self.agent_id, query]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                # Parse JSON response
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return []
            else:
                self.logger.error(f"Search failed: {result.stderr}")
                return []

        except Exception as e:
            self.logger.error(f"Error searching memories: {e}")
            return []

    def list_agents(self) -> List[Dict]:
        """List all available agents.

        Returns:
            List of agent dictionaries
        """
        try:
            cmd = [self.letta_path, "agents"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return []
            return []

        except Exception as e:
            self.logger.error(f"Error listing agents: {e}")
            return []

    def _create_conversation_summary(self, data: Dict) -> str:
        """Create a formatted conversation summary.

        Args:
            data: Conversation data dictionary

        Returns:
            Formatted summary string
        """
        session_id = data.get("session_id", "unknown")
        title = data.get("title", "Conversation")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        message_count = data.get("message_count", 0)
        participants = data.get("participants", ["user", "assistant"])

        summary = f"""CONVERSATION: {title}

Session: {session_id}
Timestamp: {timestamp}
Participants: {", ".join(participants)}
Message count: {message_count}

Key Points:
{self._format_key_points(data.get("key_points", []))}

Decisions Made:
{self._format_decisions(data.get("decisions", []))}

Action Items:
{self._format_action_items(data.get("action_items", []))}

Topics Discussed:
{self._format_topics(data.get("topics", []))}

Summary:
{data.get("summary", "No summary provided.")}
"""
        return summary

    def _format_key_points(self, points: List[str]) -> str:
        """Format key points as bullet list."""
        if not points:
            return "- No key points extracted"
        return "\n".join(f"- {point}" for point in points[:10])  # Limit to 10

    def _format_decisions(self, decisions: List[str]) -> str:
        """Format decisions as bullet list."""
        if not decisions:
            return "- No decisions recorded"
        return "\n".join(f"• {decision}" for decision in decisions[:10])

    def _format_action_items(self, items: List[str]) -> str:
        """Format action items as bullet list."""
        if not items:
            return "- No action items"
        return "\n".join(f"☐ {item}" for item in items[:10])

    def _format_topics(self, topics: List[str]) -> str:
        """Format topics as comma-separated list."""
        if not topics:
            return "No specific topics identified"
        return ", ".join(topics[:15])  # Limit to 15 topics

    def _extract_tags(self, data: Dict) -> List[str]:
        """Extract tags from conversation data."""
        tags = ["conversation"]

        # Add session ID if available
        if "session_id" in data:
            tags.append(data["session_id"][:8])  # First 8 chars

        # Add project tags
        if "project" in data:
            tags.append(data["project"])

        # Add topic tags (first 5)
        if "topics" in data:
            for topic in data["topics"][:5]:
                # Clean topic for use as tag
                clean_topic = topic.lower().replace(" ", "-").replace("/", "-")
                tags.append(clean_topic[:20])

        # Add date tag
        if "timestamp" in data:
            try:
                dt = datetime.fromisoformat(data["timestamp"])
                tags.append(dt.strftime("%Y-%m-%d"))
            except:
                pass

        return list(set(tags))[:10]  # Remove duplicates, limit to 10

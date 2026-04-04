"""
Conversation Processor - Extract key information from conversation logs.
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging


class ConversationProcessor:
    """Process conversation logs and extract key information."""

    def __init__(self, config=None):
        """Initialize processor with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Keywords for identifying different types of content
        self.decision_keywords = [
            "decision:",
            "conclusion:",
            "we will",
            "going to",
            "i'll",
            "we should",
            "let's",
            "plan:",
            "action item:",
            "todo:",
            "next step:",
            "the plan is",
            "we need to",
        ]

        self.action_keywords = [
            "todo",
            "action item",
            "next step",
            "to do",
            "task:",
            "☐",
            "□",
            "○",
            "●",
            "◇",
            "☐",
        ]

        self.question_patterns = [
            r"\?$",
            r"^(what|how|why|when|where|who|which|can|could|should|would|is|are|do|does)\s",
            r"\?$",
        ]

    def process_file(self, file_path: str) -> Dict:
        """Process a conversation log file.

        Args:
            file_path: Path to conversation log file

        Returns:
            Processed conversation data dictionary
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            content = path.read_text(encoding="utf-8")
            return self.process_content(content, file_path)

        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return self._create_error_result(str(e))

    def process_content(self, content: str, source: str = "direct_input") -> Dict:
        """Process conversation content string.

        Args:
            content: Conversation text content
            source: Source identifier

        Returns:
            Processed conversation data dictionary
        """
        try:
            # Extract basic metadata
            session_id = self._extract_session_id(content, source)
            title = self._extract_title(content, source)
            timestamp = self._extract_timestamp(content)

            # Parse conversation structure
            messages = self._parse_messages(content)
            participant_counts = self._count_participants(messages)

            # Extract key information
            key_points = self._extract_key_points(content)
            decisions = self._extract_decisions(content)
            action_items = self._extract_action_items(content)
            questions = self._extract_questions(content)
            topics = self._extract_topics(content)

            # Generate summary
            summary = self._generate_summary(content, key_points, decisions)

            # Calculate metrics
            word_count = len(content.split())
            message_count = len(messages)

            return {
                "session_id": session_id,
                "title": title,
                "source": source,
                "timestamp": timestamp,
                "participants": list(participant_counts.keys()),
                "participant_counts": participant_counts,
                "message_count": message_count,
                "word_count": word_count,
                "key_points": key_points,
                "decisions": decisions,
                "action_items": action_items,
                "questions": questions,
                "topics": topics,
                "summary": summary,
                "processed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error processing content: {e}")
            return self._create_error_result(str(e))

    def _extract_session_id(self, content: str, source: str) -> str:
        """Extract or generate session ID."""
        # Look for session ID in content
        patterns = [
            r"\*\*Session ID:\*\*\s*(.+)",
            r"Session[:\s]+([A-Za-z0-9_-]+)",
            r"ID[:\s]+([A-Za-z0-9_-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Generate from source and timestamp
        source_hash = hash(source) % 10000
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M")
        return f"session_{timestamp_str}_{source_hash}"

    def _extract_title(self, content: str, source: str) -> str:
        """Extract or generate title."""
        # Look for title in first line or header
        lines = content.split("\n")
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()
            elif len(line) > 10 and len(line) < 200:
                # Might be a title
                if not any(
                    keyword in line.lower()
                    for keyword in ["the ", "a ", "an ", "in ", "on ", "at "]
                ):
                    return line

        # Use filename
        if source and source != "direct_input":
            return Path(source).stem.replace("_", " ").title()

        return "Conversation Session"

    def _extract_timestamp(self, content: str) -> str:
        """Extract timestamp from conversation."""
        patterns = [
            r"\*\*Created:\*\*\s*(.+)",
            r"\*\*Timestamp:\*\*\s*(.+)",
            r"(\d{1,2}/\d{1,2}/\d{4},?\s*\d{1,2}:\d{2}\s*[AP]M)",
            r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                timestamp_str = match.group(1).strip()
                # Try to parse and standardize
                try:
                    # Try common formats
                    for fmt in [
                        "%m/%d/%Y, %I:%M %p",
                        "%m/%d/%Y %I:%M %p",
                        "%Y-%m-%dT%H:%M",
                        "%Y-%m-%d %H:%M",
                    ]:
                        try:
                            dt = datetime.strptime(timestamp_str, fmt)
                            return dt.isoformat()
                        except:
                            continue
                except:
                    pass
                return timestamp_str

        return datetime.now().isoformat()

    def _parse_messages(self, content: str) -> List[Dict]:
        """Parse conversation into messages."""
        messages = []

        # Look for message patterns (## User, ## Assistant, etc.)
        message_pattern = (
            r"## (User|Assistant|System)[\s\(]*(?:\([^)]*\))?[\s]*[\n](.*?)(?=\n## |\Z)"
        )
        matches = re.findall(message_pattern, content, re.DOTALL | re.IGNORECASE)

        for role, content_part in matches:
            messages.append(
                {
                    "role": role.lower(),
                    "content": content_part.strip(),
                    "word_count": len(content_part.split()),
                }
            )

        # If no structured messages found, treat whole content as one message
        if not messages:
            messages.append(
                {"role": "unknown", "content": content, "word_count": len(content.split())}
            )

        return messages

    def _count_participants(self, messages: List[Dict]) -> Dict[str, int]:
        """Count messages per participant."""
        counts = {}
        for msg in messages:
            role = msg["role"]
            counts[role] = counts.get(role, 0) + 1
        return counts

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from conversation."""
        key_points = []

        # Look for bullet points and numbered lists
        bullet_pattern = r"[-•*]\s+(.+?)(?:\n|$)"
        numbered_pattern = r"\d+\.\s+(.+?)(?:\n|$)"

        for pattern in [bullet_pattern, numbered_pattern]:
            matches = re.findall(pattern, content)
            for match in matches:
                # Filter out short or trivial points
                if len(match) > 20 and not match.endswith("."):
                    key_points.append(match.strip())

        return list(set(key_points))[:15]  # Remove duplicates, limit to 15

    def _extract_decisions(self, content: str) -> List[str]:
        """Extract decisions from conversation."""
        decisions = []
        lines = content.split("\n")

        for line in lines:
            line_lower = line.lower()
            # Check for decision keywords
            if any(keyword in line_lower for keyword in self.decision_keywords):
                # Clean and add the line
                clean_line = line.strip()
                if clean_line and len(clean_line) > 10:
                    decisions.append(clean_line)

        return decisions[:10]  # Limit to 10

    def _extract_action_items(self, content: str) -> List[str]:
        """Extract action items from conversation."""
        action_items = []
        lines = content.split("\n")

        for line in lines:
            line_lower = line.lower()
            # Check for action item keywords or markers
            if any(keyword in line_lower for keyword in self.action_keywords) or any(
                marker in line for marker in ["☐", "□", "☐"]
            ):
                clean_line = line.strip()
                if clean_line and len(clean_line) > 5:
                    action_items.append(clean_line)

        return action_items[:10]  # Limit to 10

    def _extract_questions(self, content: str) -> List[str]:
        """Extract questions from conversation."""
        questions = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if line and line.endswith("?") and len(line) > 10:
                questions.append(line)

        return questions[:10]  # Limit to 10

    def _extract_topics(self, content: str) -> List[str]:
        """Extract main topics from conversation."""
        # Common topics to look for
        topic_keywords = {
            "epstein": "epstein",
            "database": "database",
            "postgresql": "postgresql",
            "gpu": "gpu",
            "ocr": "ocr",
            "ner": "entity-extraction",
            "memory": "memory-system",
            "letta": "letta",
            "download": "download",
            "pdf": "pdf-processing",
            "entity": "entity-extraction",
            "knowledge graph": "knowledge-graph",
            "verification": "verification",
            "testing": "testing",
            "analysis": "analysis",
        }

        found_topics = []
        content_lower = content.lower()

        for keyword, topic in topic_keywords.items():
            if keyword in content_lower:
                found_topics.append(topic)

        return list(set(found_topics))[:10]  # Remove duplicates, limit to 10

    def _generate_summary(self, content: str, key_points: List[str], decisions: List[str]) -> str:
        """Generate a concise summary of the conversation."""
        # Count key elements
        word_count = len(content.split())

        # Extract first meaningful paragraph
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]
        first_paragraph = paragraphs[0] if paragraphs else ""

        # Truncate if too long
        if len(first_paragraph) > 500:
            first_paragraph = first_paragraph[:500] + "..."

        summary_parts = []

        if first_paragraph:
            summary_parts.append(f"Overview: {first_paragraph}")

        if key_points:
            summary_points = "; ".join(key_points[:3])
            summary_parts.append(f"Key points: {summary_points}")

        if decisions:
            summary_decisions = "; ".join(decisions[:2])
            summary_parts.append(f"Decisions: {summary_decisions}")

        if not summary_parts:
            summary_parts.append(f"Conversation of {word_count} words")

        return " | ".join(summary_parts)

    def _create_error_result(self, error_message: str) -> Dict:
        """Create error result dictionary."""
        return {
            "error": error_message,
            "session_id": f"error_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": "Error Processing Conversation",
            "timestamp": datetime.now().isoformat(),
            "participants": [],
            "message_count": 0,
            "word_count": 0,
            "key_points": [],
            "decisions": [],
            "action_items": [],
            "questions": [],
            "topics": [],
            "summary": f"Error: {error_message}",
            "processed_at": datetime.now().isoformat(),
        }

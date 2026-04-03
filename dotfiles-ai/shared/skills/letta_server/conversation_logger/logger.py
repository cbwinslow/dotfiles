"""
Main Conversation Logger - Captures and saves conversation logs to Letta server.
"""

import os
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from queue import Queue, Empty

from .config import Config
from .processor import ConversationProcessor
from .letta_client import LettaClient


class ConversationLogger:
    """Main conversation logger that captures and saves conversations to Letta."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize conversation logger.

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = Config(config_path)

        # Setup logging
        self._setup_logging()

        # Initialize components
        self.processor = ConversationProcessor(self.config)
        self.letta_client = LettaClient(agent_id=self.config.get("letta", "agent_id"))

        # State
        self.is_running = False
        self.watch_thread = None
        self.message_queue = Queue()
        self.processed_files = set()

        # Load processed files list
        self._load_processed_files()

        self.logger.info("Conversation Logger initialized")
        self.logger.info(f"Letta agent: {self.config.get('letta', 'agent_name')}")

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = self.config.get("logging", "log_level") or "INFO"
        log_file = self.config.get("logging", "log_file")

        # Create logs directory if needed
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file) if log_file else logging.StreamHandler(),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _load_processed_files(self) -> None:
        """Load list of already processed files."""
        processed_file = Path.home() / ".conversation_logger" / "processed_files.json"
        if processed_file.exists():
            try:
                with open(processed_file, "r") as f:
                    self.processed_files = set(json.load(f))
                self.logger.info(f"Loaded {len(self.processed_files)} processed files")
            except Exception as e:
                self.logger.warning(f"Could not load processed files: {e}")

    def _save_processed_files(self) -> None:
        """Save list of processed files."""
        processed_file = Path.home() / ".conversation_logger" / "processed_files.json"
        processed_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(processed_file, "w") as f:
                json.dump(list(self.processed_files), f)
        except Exception as e:
            self.logger.warning(f"Could not save processed files: {e}")

    def log_conversation(
        self, content: str, source: str = "direct_input", save_to_letta: bool = True
    ) -> Dict:
        """Log a conversation.

        Args:
            content: Conversation content
            source: Source identifier
            save_to_letta: Whether to save to Letta server

        Returns:
            Processed conversation data
        """
        self.logger.info(f"Processing conversation from: {source}")

        # Process conversation
        result = self.processor.process_content(content, source)

        if "error" in result:
            self.logger.error(f"Processing error: {result['error']}")
            return result

        # Save to Letta server if requested
        if save_to_letta:
            self._save_to_letta(result)

        # Save to local archive
        self._save_to_archive(result, content)

        # Log summary
        self.logger.info(f"✅ Conversation logged: {result['title']}")
        self.logger.info(f"   Session: {result['session_id']}")
        self.logger.info(f"   Decisions: {len(result['decisions'])}")
        self.logger.info(f"   Action items: {len(result['action_items'])}")

        return result

    def log_file(self, file_path: str, save_to_letta: bool = True) -> Dict:
        """Log a conversation from file.

        Args:
            file_path: Path to conversation file
            save_to_letta: Whether to save to Letta server

        Returns:
            Processed conversation data
        """
        file_path = str(Path(file_path).absolute())

        # Check if already processed
        if file_path in self.processed_files:
            self.logger.info(f"File already processed: {file_path}")
            return {"status": "already_processed", "file": file_path}

        # Process file
        result = self.processor.process_file(file_path)

        if "error" in result:
            self.logger.error(f"File processing error: {result['error']}")
            return result

        # Save to Letta server if requested
        if save_to_letta:
            self._save_to_letta(result)

        # Mark as processed
        self.processed_files.add(file_path)
        self._save_processed_files()

        self.logger.info(f"✅ File logged: {Path(file_path).name}")
        return result

    def _save_to_letta(self, conversation_data: Dict) -> None:
        """Save conversation data to Letta server."""
        try:
            # Insert conversation summary
            success = self.letta_client.insert_conversation_summary(conversation_data)

            if success:
                # Also insert key decisions separately
                if conversation_data.get("decisions"):
                    self.letta_client.insert_key_decisions(
                        conversation_data["decisions"], conversation_data["session_id"]
                    )

                # Update agent persona with recent activity
                if conversation_data.get("topics"):
                    persona_update = (
                        f"Recent activity: Working on {', '.join(conversation_data['topics'][:3])}"
                    )
                    self.letta_client.update_persona(persona_update, "human")

            else:
                self.logger.error("Failed to save conversation to Letta server")

        except Exception as e:
            self.logger.error(f"Error saving to Letta: {e}")

    def _save_to_archive(self, conversation_data: Dict, original_content: str) -> None:
        """Save conversation to local archive."""
        try:
            archive_dir = self.config.get("storage", "archive_dir") or "logs/archives"
            archive_path = Path(archive_dir)
            archive_path.mkdir(parents=True, exist_ok=True)

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = conversation_data.get("session_id", "unknown")
            filename = f"conversation_{timestamp}_{session_id}.json"

            # Save both processed data and original content
            archive_data = {
                "metadata": conversation_data,
                "original_content": original_content[:10000],  # Limit size
                "archived_at": datetime.now().isoformat(),
            }

            archive_file = archive_path / filename
            with open(archive_file, "w", encoding="utf-8") as f:
                json.dump(archive_data, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Archived to: {archive_file}")

        except Exception as e:
            self.logger.error(f"Error saving to archive: {e}")

    def start_watching(self) -> None:
        """Start watching for new conversation files."""
        if self.is_running:
            self.logger.warning("Already watching for conversations")
            return

        self.is_running = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()

        self.logger.info("Started watching for conversation files")

    def stop_watching(self) -> None:
        """Stop watching for new conversation files."""
        self.is_running = False
        if self.watch_thread:
            self.watch_thread.join(timeout=5)
        self.logger.info("Stopped watching for conversation files")

    def _watch_loop(self) -> None:
        """Main loop for watching conversation files."""
        watch_dirs = self.config.get("monitoring", "watch_directories") or []
        patterns = self.config.get("monitoring", "file_patterns") or ["*.md", "*.txt"]
        interval = self.config.get("monitoring", "check_interval_seconds") or 60

        while self.is_running:
            try:
                for watch_dir in watch_dirs:
                    watch_path = Path(watch_dir)
                    if not watch_path.exists():
                        continue

                    for pattern in patterns:
                        for file_path in watch_path.glob(f"**/{pattern}"):
                            if str(file_path) not in self.processed_files:
                                # Check if file looks like a conversation
                                if self._is_conversation_file(file_path):
                                    self.logger.info(f"Found new conversation: {file_path}")
                                    self.message_queue.put(str(file_path))

                # Process any queued files
                self._process_queue()

                # Sleep before next scan
                time.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in watch loop: {e}")
                time.sleep(interval)

    def _is_conversation_file(self, file_path: Path) -> bool:
        """Check if file looks like a conversation log."""
        try:
            # Check file size (not too small, not too large)
            size = file_path.stat().st_size
            if size < 100 or size > 10_000_000:  # 100B to 10MB
                return False

            # Check content for conversation indicators
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_1000 = f.read(1000)

            conversation_indicators = [
                "## User",
                "## Assistant",
                "## System",
                "**Session ID:**",
                "**Created:**",
                "conversation",
                "chat",
                "dialogue",
            ]

            content_lower = first_1000.lower()
            return any(indicator.lower() in content_lower for indicator in conversation_indicators)

        except Exception:
            return False

    def _process_queue(self) -> None:
        """Process queued conversation files."""
        processed = 0
        max_per_cycle = 10  # Limit files per cycle

        while processed < max_per_cycle:
            try:
                file_path = self.message_queue.get_nowait()
                result = self.log_file(file_path, save_to_letta=True)
                if "error" not in result:
                    processed += 1
                self.message_queue.task_done()
            except Empty:
                break
            except Exception as e:
                self.logger.error(f"Error processing queued file: {e}")

    def get_stats(self) -> Dict:
        """Get logger statistics."""
        return {
            "is_running": self.is_running,
            "processed_files": len(self.processed_files),
            "queue_size": self.message_queue.qsize(),
            "letta_connected": self.letta_client.test_connection(),
            "agent_id": self.letta_client.agent_id,
        }

    def search_conversations(self, query: str) -> List[Dict]:
        """Search logged conversations in Letta server."""
        return self.letta_client.search_memories(query)

    def export_archive(self, output_dir: str, format: str = "json") -> List[str]:
        """Export conversation archive.

        Args:
            output_dir: Directory to export to
            format: Export format ('json' or 'markdown')

        Returns:
            List of exported file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exported_files = []
        archive_dir = self.config.get("storage", "archive_dir") or "logs/archives"

        for archive_file in Path(archive_dir).glob("*.json"):
            try:
                with open(archive_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Export based on format
                if format == "json":
                    output_file = output_path / f"{archive_file.stem}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                else:  # markdown
                    output_file = output_path / f"{archive_file.stem}.md"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(self._to_markdown(data))

                exported_files.append(str(output_file))

            except Exception as e:
                self.logger.error(f"Error exporting {archive_file}: {e}")

        return exported_files

    def _to_markdown(self, data: Dict) -> str:
        """Convert conversation data to markdown format."""
        metadata = data.get("metadata", {})
        content = data.get("original_content", "")

        markdown = f"""# {metadata.get("title", "Conversation")}

**Session:** {metadata.get("session_id", "Unknown")}
**Timestamp:** {metadata.get("timestamp", "Unknown")}
**Source:** {metadata.get("source", "Unknown")}

## Summary

{metadata.get("summary", "No summary available")}

## Key Points

"""

        for point in metadata.get("key_points", []):
            markdown += f"- {point}\n"

        markdown += "\n## Decisions\n\n"
        for decision in metadata.get("decisions", []):
            markdown += f"- {decision}\n"

        markdown += "\n## Action Items\n\n"
        for item in metadata.get("action_items", []):
            markdown += f"- {item}\n"

        markdown += f"\n## Original Content\n\n{content[:5000]}"  # Limit content

        return markdown

"""
Configuration management for conversation logger.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for conversation logger."""

    DEFAULT_CONFIG = {
        "letta": {
            "server_url": "http://localhost:8283",
            "agent_id": "agent-1167f15a-a10a-4595-b962-ec0f372aae0d",
            "agent_name": "coder",
        },
        "logging": {
            "log_level": "INFO",
            "log_file": "conversation_logger.log",
            "max_log_size_mb": 10,
            "backup_count": 5,
        },
        "processing": {
            "max_summary_length": 1000,
            "key_decision_keywords": [
                "decision",
                "conclusion",
                "will",
                "going to",
                "plan",
                "action item",
                "todo",
                "next step",
            ],
            "auto_extract_tags": True,
            "max_tags": 10,
        },
        "storage": {
            "archive_dir": "logs/archives",
            "max_archive_days": 30,
            "compress_old_logs": True,
        },
        "monitoring": {
            "watch_directories": ["/home/cbwinslow/workspace", "/tmp"],
            "file_patterns": ["*.md", "*.txt", "*.log"],
            "check_interval_seconds": 60,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_path: Path to YAML config file. If None, uses default.
        """
        self.config = self.DEFAULT_CONFIG.copy()

        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)

        # Override with environment variables
        self._load_from_env()

    def _load_from_file(self, config_path: str) -> None:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    self._merge_config(self.config, file_config)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "LETTA_SERVER_URL": ("letta", "server_url"),
            "LETTA_AGENT_ID": ("letta", "agent_id"),
            "LETTA_AGENT_NAME": ("letta", "agent_name"),
            "CONV_LOG_LEVEL": ("logging", "log_level"),
            "CONV_LOG_FILE": ("logging", "log_file"),
        }

        for env_var, path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested(self.config, path, value)

    def _merge_config(self, base: Dict, override: Dict) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _set_nested(self, d: Dict, path: tuple, value: Any) -> None:
        """Set a nested dictionary value."""
        current = d
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value

    def get(self, *keys) -> Any:
        """Get configuration value using dot notation.

        Example:
            config.get("letta", "agent_id")
        """
        current = self.config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def set(self, *keys, value: Any) -> None:
        """Set configuration value using dot notation."""
        self._set_nested(self.config, keys, value)

    def to_dict(self) -> Dict:
        """Return configuration as dictionary."""
        return self.config.copy()

    def save(self, config_path: str) -> None:
        """Save configuration to file."""
        with open(config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)

    @classmethod
    def get_default_config_path(cls) -> str:
        """Get default configuration file path."""
        return os.path.expanduser("~/.conversation_logger/config.yaml")

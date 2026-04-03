"""
Conversation Logging Module - Built into Letta Integration

Automatically logs all AI agent conversations to Letta archival memory.
Cross-agent conversation sharing enabled - any agent can search any other agent's logs.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List


class ConversationLogger:
    """
    Conversation logger integrated with Letta archival memory.
    
    Features:
    - Auto-logs to Letta archival memory
    - Cross-agent conversation sharing
    - Session management
    - Local JSONL backup
    - Tool call logging
    """
    
    def __init__(self, letta_integration, agent_name: str = "unknown"):
        """
        Initialize conversation logger.
        
        Args:
            letta_integration: LettaIntegration instance
            agent_name: Name of the AI agent (claude, windsurf, etc.)
        """
        self.letta = letta_integration
        self.agent_name = agent_name
        self.session_id = self._generate_session_id()
        self.start_time = datetime.now().isoformat()
        self.interaction_count = 0
        
        # Ensure agent exists
        if not self.letta.agent_id:
            self.letta.get_or_create_agent(f"{agent_name}_conversations")
        
        # Local backup
        self.local_log_file = os.path.expanduser(
            f"~/dotfiles/ai/logs/{agent_name}_{self.session_id}.jsonl"
        )
        os.makedirs(os.path.dirname(self.local_log_file), exist_ok=True)
        
        # Log session start
        self._write_local({
            "type": "session_start",
            "agent": agent_name,
            "session_id": self.session_id,
            "timestamp": self.start_time,
            "letta_agent_id": self.letta.agent_id
        })
        
        # Log to Letta
        self._log_to_letta(
            f"[{agent_name}] Session started: {self.session_id}",
            "system",
            ["session_start", agent_name]
        )
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(os.urandom(16)).hexdigest()[:8]
        return f"{timestamp}_{random_hash}"
    
    def _write_local(self, data: Dict):
        """Write to local JSONL backup"""
        try:
            with open(self.local_log_file, 'a') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"[ConversationLogger] Local log warning: {e}")
    
    def _log_to_letta(self, content: str, role: str, tags: List[str]):
        """Log entry to Letta archival memory"""
        try:
            log_entry = {
                "agent": self.agent_name,
                "session": self.session_id,
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "interaction": self.interaction_count
            }
            
            text = json.dumps(log_entry, indent=2)
            default_tags = ["conversation", self.agent_name, role]
            default_tags.extend(tags)
            
            self.letta.save_to_archival(
                text=text,
                agent_id=self.letta.agent_id,
                tags=default_tags
            )
        except Exception as e:
            print(f"[ConversationLogger] Letta log warning: {e}")
    
    def log_interaction(self, user_input: str, agent_response: str, 
                       metadata: Optional[Dict] = None) -> bool:
        """
        Log a complete user-agent interaction.
        
        Args:
            user_input: User's message
            agent_response: Agent's response
            metadata: Optional metadata (tokens, model, etc.)
        
        Returns:
            True if logged
        """
        self.interaction_count += 1
        timestamp = datetime.now().isoformat()
        
        # Local log
        entry = {
            "type": "interaction",
            "interaction_num": self.interaction_count,
            "timestamp": timestamp,
            "agent": self.agent_name,
            "session": self.session_id,
            "user_input": user_input,
            "agent_response": agent_response,
            "metadata": metadata or {}
        }
        self._write_local(entry)
        
        # Letta log
        self._log_to_letta(
            f"[User]: {user_input}",
            "user",
            ["user_input", f"interaction_{self.interaction_count}"]
        )
        self._log_to_letta(
            f"[{self.agent_name}]: {agent_response}",
            "assistant",
            ["agent_response", f"interaction_{self.interaction_count}"]
        )
        
        return True
    
    def log_tool_call(self, tool_name: str, tool_input: Dict, 
                     tool_output: Any, success: bool = True):
        """Log a tool/function call"""
        entry = {
            "type": "tool_call",
            "interaction_num": self.interaction_count,
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "tool": tool_name,
            "input": tool_input,
            "output": str(tool_output)[:500],
            "success": success
        }
        self._write_local(entry)
        
        self._log_to_letta(
            f"[Tool: {tool_name}] Input: {json.dumps(tool_input)} -> "
            f"Output: {str(tool_output)[:200]}",
            "tool",
            ["tool_call", tool_name, "success" if success else "error"]
        )
    
    def end_session(self, summary: str = "") -> str:
        """End the logging session"""
        end_time = datetime.now().isoformat()
        
        entry = {
            "type": "session_end",
            "agent": self.agent_name,
            "session_id": self.session_id,
            "end_time": end_time,
            "total_interactions": self.interaction_count,
            "summary": summary
        }
        self._write_local(entry)
        
        self._log_to_letta(
            f"[{self.agent_name}] Session ended. "
            f"Total: {self.interaction_count} interactions. {summary}",
            "system",
            ["session_end", f"count_{self.interaction_count}"]
        )
        
        return self.session_id
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search across all conversations.
        Any agent can search any other agent's conversations!
        """
        try:
            results = self.letta.search_archival(
                query=query,
                agent_id=self.letta.agent_id,
                limit=limit
            )
            return results
        except Exception as e:
            print(f"[ConversationLogger] Search failed: {e}")
            return []
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation entries"""
        return self.search_conversations("conversation", limit=limit)


class AutoLogger:
    """
    Automatic conversation logger for terminal AI agents.
    Hooks into agent lifecycle to auto-log.
    """
    
    def __init__(self, agent_name: str = None):
        from . import LettaIntegration, get_letta_integration
        
        self.agent_name = agent_name or self._detect_agent()
        self.letta = get_letta_integration(f"{self.agent_name}_auto")
        self.logger = None
        self._active = False
    
    def _detect_agent(self) -> str:
        """Auto-detect which agent is running"""
        import psutil
        process = psutil.Process()
        cmdline = ' '.join(process.cmdline()).lower()
        
        agents = {
            'windsurf': 'windsurf',
            'claude': 'claude',
            'cline': 'cline',
            'openclaw': 'openclaw',
            'codex': 'codex',
            'kilocode': 'kilocode',
            'opencode': 'opencode',
            'gemini': 'gemini',
            'qwen': 'qwen',
        }
        
        for key, name in agents.items():
            if key in cmdline:
                return name
        
        return 'unknown'
    
    def start(self):
        """Start auto-logging session"""
        self.logger = ConversationLogger(self.letta, self.agent_name)
        self._active = True
        print(f"📝 Conversation logging started for {self.agent_name}")
        print(f"   Session: {self.logger.session_id}")
        return self.logger.session_id
    
    def log(self, user_input: str, agent_response: str):
        """Log an interaction (if active)"""
        if self._active and self.logger:
            self.logger.log_interaction(user_input, agent_response)
    
    def end(self, summary: str = ""):
        """End auto-logging session"""
        if self._active and self.logger:
            session_id = self.logger.end_session(summary)
            self._active = False
            print(f"📝 Conversation logging ended: {session_id}")
            return session_id


def get_logger(agent_name: str = None) -> ConversationLogger:
    """
    Quick function to get a conversation logger.
    
    Usage:
        logger = get_logger("windsurf")
        logger.log_interaction("Hello", "Hi there!")
    """
    from . import get_letta_integration
    
    agent = agent_name or "unknown"
    letta = get_letta_integration(f"{agent}_conversations")
    return ConversationLogger(letta, agent)


def quick_log(user_input: str, agent_response: str, agent_name: str = "quick"):
    """One-off quick log without managing logger instance"""
    logger = get_logger(agent_name)
    logger.log_interaction(user_input, agent_response)
    session_id = logger.end_session("Quick log")
    return session_id

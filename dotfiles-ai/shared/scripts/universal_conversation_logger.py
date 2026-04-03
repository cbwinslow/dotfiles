"""
Universal Conversation Logger for ALL AI Agents
Auto-logs every conversation to Letta archival memory with cross-agent sharing.
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add Letta integration to path
sys.path.insert(0, os.path.expanduser("~/dotfiles/ai/packages/letta_integration"))

try:
    from letta_integration import LettaIntegration
    LETTA_AVAILABLE = True
except ImportError:
    LETTA_AVAILABLE = False
    print("Warning: Letta integration not available. Logging to file only.")


class ConversationLogger:
    """
    Universal conversation logger that works with any AI agent.
    Automatically logs to Letta archival memory for cross-agent sharing.
    """
    
    def __init__(self, agent_name: str = "unknown", session_id: Optional[str] = None):
        self.agent_name = agent_name
        self.session_id = session_id or self._generate_session_id()
        self.start_time = datetime.now().isoformat()
        self.interaction_count = 0
        
        # Initialize Letta if available
        self.letta = None
        self.agent_id = None
        if LETTA_AVAILABLE:
            try:
                self.letta = LettaIntegration(agent_name=f"{agent_name}_logger")
                # Get or create agent for this logger
                self.agent_id = self.letta.get_or_create_agent()
                self._log_to_letta(f"Session started for {agent_name}", "system")
            except Exception as e:
                print(f"Letta logging disabled: {e}")
                self.letta = None
        
        # Local file backup
        self.local_log_file = os.path.expanduser(
            f"~/dotfiles/ai/logs/{agent_name}_{self.session_id}.jsonl"
        )
        os.makedirs(os.path.dirname(self.local_log_file), exist_ok=True)
        
        # Write session start
        self._write_local({
            "type": "session_start",
            "agent": agent_name,
            "session_id": self.session_id,
            "timestamp": self.start_time,
            "letta_enabled": self.letta is not None
        })
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(os.urandom(16)).hexdigest()[:8]
        return f"{timestamp}_{random_hash}"
    
    def _write_local(self, data: Dict):
        """Write to local JSONL file"""
        try:
            with open(self.local_log_file, 'a') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"Failed to write local log: {e}")
    
    def _log_to_letta(self, content: str, role: str = "user", tags: List[str] = None):
        """Log to Letta archival memory"""
        if not self.letta or not self.agent_id:
            return False
        
        try:
            # Format content with metadata
            log_entry = {
                "agent": self.agent_name,
                "session": self.session_id,
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "interaction": self.interaction_count
            }
            
            # Save to archival memory
            text = json.dumps(log_entry, indent=2)
            default_tags = ["conversation", self.agent_name, role]
            if tags:
                default_tags.extend(tags)
            
            return self.letta.save_to_archival(
                text=text,
                agent_id=self.agent_id,
                tags=default_tags
            )
        except Exception as e:
            print(f"Letta log failed: {e}")
            return False
    
    def log_interaction(self, user_input: str, agent_response: str, 
                       metadata: Optional[Dict] = None) -> bool:
        """
        Log a complete interaction (user input + agent response).
        
        Args:
            user_input: What the user said
            agent_response: What the agent replied
            metadata: Optional extra data (tool calls, tokens, etc.)
        
        Returns:
            True if logged successfully
        """
        self.interaction_count += 1
        timestamp = datetime.now().isoformat()
        
        # Local log entry
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
        
        # Write to local file
        self._write_local(entry)
        
        # Log to Letta
        if self.letta:
            # Log user input
            self._log_to_letta(
                f"[User]: {user_input}",
                role="user",
                tags=["user_input", f"interaction_{self.interaction_count}"]
            )
            # Log agent response
            self._log_to_letta(
                f"[{self.agent_name}]: {agent_response}",
                role="assistant",
                tags=["agent_response", f"interaction_{self.interaction_count}"]
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
            "output": str(tool_output)[:500],  # Truncate long outputs
            "success": success
        }
        self._write_local(entry)
        
        if self.letta:
            self._log_to_letta(
                f"[Tool: {tool_name}] Input: {tool_input} -> Output: {str(tool_output)[:200]}",
                role="tool",
                tags=["tool_call", tool_name, "success" if success else "failure"]
            )
    
    def end_session(self, summary: str = ""):
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
        
        if self.letta:
            self._log_to_letta(
                f"Session ended. Total interactions: {self.interaction_count}. Summary: {summary}",
                role="system",
                tags=["session_end", f"interactions_{self.interaction_count}"]
            )
        
        return self.session_id
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search across all logged conversations using Letta.
        Any agent can search any other agent's conversations!
        """
        if not self.letta or not self.agent_id:
            return []
        
        try:
            results = self.letta.search_archival(
                query=query,
                agent_id=self.agent_id,
                limit=limit
            )
            return results
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    @classmethod
    def get_all_logs(cls, agent_name: Optional[str] = None) -> List[str]:
        """Get list of all log files"""
        log_dir = os.path.expanduser("~/dotfiles/ai/logs")
        if not os.path.exists(log_dir):
            return []
        
        files = os.listdir(log_dir)
        if agent_name:
            files = [f for f in files if f.startswith(agent_name)]
        
        return sorted(files, reverse=True)


# Auto-initialization for different agent types
def get_logger_for_agent(agent_name: Optional[str] = None) -> ConversationLogger:
    """
    Get a conversation logger for the current agent.
    Auto-detects agent from environment or uses provided name.
    """
    # Try to detect agent from environment
    if not agent_name:
        # Check common environment variables
        for env_var in ['CURRENT_AI_AGENT', 'AGENT_NAME', 'CLINE_AGENT', 'CLAUDE_AGENT']:
            if os.getenv(env_var):
                agent_name = os.getenv(env_var)
                break
        
        # Try to detect from process
        if not agent_name:
            import psutil
            process = psutil.Process()
            cmdline = ' '.join(process.cmdline()).lower()
            
            if 'windsurf' in cmdline:
                agent_name = 'windsurf'
            elif 'claude' in cmdline:
                agent_name = 'claude'
            elif 'cline' in cmdline:
                agent_name = 'cline'
            elif 'openclaw' in cmdline:
                agent_name = 'openclaw'
            else:
                agent_name = 'unknown'
    
    return ConversationLogger(agent_name=agent_name)


# Convenience function for quick logging
def log_interaction_quick(user_input: str, agent_response: str, 
                          agent_name: str = "quick") -> bool:
    """Quick one-off conversation log"""
    logger = get_logger_for_agent(agent_name)
    return logger.log_interaction(user_input, agent_response)


if __name__ == "__main__":
    # Demo usage
    print("=" * 60)
    print("Universal Conversation Logger Demo")
    print("=" * 60)
    
    # Create logger
    logger = ConversationLogger(agent_name="demo_agent")
    print(f"\n✅ Logger initialized")
    print(f"   Session ID: {logger.session_id}")
    print(f"   Letta enabled: {logger.letta is not None}")
    print(f"   Log file: {logger.local_log_file}")
    
    # Log some interactions
    print("\n📝 Logging interactions...")
    logger.log_interaction(
        "Hello, can you help me with Python?",
        "Of course! I'd be happy to help you with Python. What do you need?"
    )
    print("   ✅ Interaction 1 logged")
    
    logger.log_interaction(
        "How do I read a file?",
        "You can use open() function. Here's an example:\nwith open('file.txt', 'r') as f:\n    content = f.read()"
    )
    print("   ✅ Interaction 2 logged")
    
    # Log a tool call
    logger.log_tool_call(
        "read_file",
        {"file_path": "/tmp/test.txt"},
        "File contents here...",
        success=True
    )
    print("   ✅ Tool call logged")
    
    # End session
    session_id = logger.end_session("Demo completed successfully")
    print(f"\n✅ Session ended: {session_id}")
    print(f"\n📁 Log saved to: {logger.local_log_file}")
    if logger.letta:
        print(f"🧠 Also saved to Letta archival memory")
    
    print("\n" + "=" * 60)

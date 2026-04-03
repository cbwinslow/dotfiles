#!/usr/bin/env python3
"""Simple Letta Conversation Logger - Stores in Letta, not local files"""
import sys
from datetime import datetime
from typing import Optional, Dict, List

sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')
from letta_integration import LettaIntegration


class SimpleConversationLogger:
    """Simple conversation logger using Letta memory"""
    
    def __init__(self, agent_name: str, tool: str = "unknown"):
        self.agent_name = agent_name
        self.tool = tool
        self.letta = LettaIntegration(agent_name=agent_name)
        self.session_id = None
        
    def start_conversation(self, metadata: Optional[Dict] = None) -> str:
        """Start session - creates conversation memory block"""
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        
        # Get or create agent
        agent_id = self.letta.get_or_create_agent()
        if not agent_id:
            return None
        
        # Store session info in memory block
        content = f"[{self.tool}] Session started: {self.session_id}"
        if metadata:
            content += f" | {metadata}"
        
        # Update agent's memory with session start
        self.letta.update_memory_block(
            label="conversation_session",
            value=content
        )
        
        return self.session_id
    
    def log_interaction(self, user_input: str, agent_response: str, context: Optional[Dict] = None) -> bool:
        """Log interaction to agent memory block"""
        if not self.session_id:
            self.start_conversation()
        
        # Format interaction
        content = f"""[{self.tool}] {datetime.utcnow().isoformat()}
SESSION: {self.session_id}
USER: {user_input}
AGENT: {agent_response}"""
        if context:
            content += f"\nCONTEXT: {context}"
        
        # Get current conversation log and append
        try:
            block = self.letta.get_memory_block("conversation_log")
            if block and hasattr(block, 'value'):
                current = block.value
                new_value = current + "\n\n" + content
            else:
                new_value = content
            
            # Update the conversation log block
            result = self.letta.update_memory_block(
                label="conversation_log",
                value=new_value[-5000:]  # Keep last 5000 chars
            )
            return result
        except Exception as e:
            print(f"[Logger] Error: {e}")
            return False
    
    def end_conversation(self, summary: Optional[str] = None) -> bool:
        """End session - save summary to memory block"""
        if not self.session_id:
            return False
        
        content = f"[{self.tool}] Session ended: {self.session_id}"
        if summary:
            content += f" | {summary}"
        
        try:
            self.letta.update_memory_block(
                label="conversation_session",
                value=content
            )
            self.session_id = None
            return True
        except:
            return False
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """Search conversations in memory blocks"""
        try:
            block = self.letta.get_memory_block("conversation_log")
            if block and hasattr(block, 'value'):
                # Simple text search
                log_content = block.value
                if query.lower() in log_content.lower():
                    return [{"content": log_content, "query": query}]
            return []
        except:
            return []


def log_conversation(agent_name: str, tool: str, user_input: str, agent_response: str) -> bool:
    """One-shot logging"""
    logger = SimpleConversationLogger(agent_name=agent_name, tool=tool)
    logger.start_conversation()
    return logger.log_interaction(user_input, agent_response)


def search_all_conversations(query: str, agent_name: str = "search") -> List[Dict]:
    """Search across all agents"""
    logger = SimpleConversationLogger(agent_name=agent_name, tool="search")
    return logger.search_conversations(query)


if __name__ == "__main__":
    print("Testing SimpleConversationLogger...")
    logger = SimpleConversationLogger(agent_name="test", tool="test")
    sid = logger.start_conversation()
    print(f"Session: {sid[:20]}...")
    logger.log_interaction("Hello", "Hi there!")
    print("Logged interaction")
    results = logger.search_conversations("Hello")
    print(f"Found {len(results)} results")
    logger.end_conversation("Test complete")
    print("Done!")

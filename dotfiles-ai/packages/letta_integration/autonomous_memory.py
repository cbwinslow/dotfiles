"""
Autonomous Memory System for AI Agents
Provides automatic memory management using Letta as the backend.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Letta client
try:
    from letta_client import Letta
    LETTA_AVAILABLE = True
except ImportError:
    LETTA_AVAILABLE = False
    logger.warning("letta-client not installed. Memory features disabled.")


@dataclass
class MemoryConfig:
    """Configuration for autonomous memory system."""
    server_url: str = field(default_factory=lambda: os.getenv("LETTA_SERVER_URL", "http://localhost:8283"))
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("LETTA_API_KEY"))
    base_agent_id: Optional[str] = field(default_factory=lambda: os.getenv("LETTA_BASE_AGENT_ID"))
    auto_memory: bool = field(default_factory=lambda: os.getenv("LETTA_AUTO_MEMORY", "true").lower() == "true")
    memory_tags: List[str] = field(default_factory=lambda: os.getenv("LETTA_MEMORY_TAGS", "autonomous").split(","))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "server_url": self.server_url,
            "api_key": self.api_key,
            "base_agent_id": self.base_agent_id,
            "auto_memory": self.auto_memory,
            "memory_tags": self.memory_tags,
        }


class AutonomousMemoryManager:
    """
    Manages autonomous memory for AI agents using Letta.
    
    Features:
    - Automatic conversation logging
    - Memory block management (persona, human, projects, knowledge)
    - Archival memory search and storage
    - Cross-agent memory sharing
    - Pre/post task memory hooks
    """
    
    def __init__(self, agent_name: str, config: Optional[MemoryConfig] = None):
        self.agent_name = agent_name
        self.config = config or MemoryConfig()
        self.client = None
        self.agent_id = None
        self.conversation_id = None
        self._initialized = False
        
        if not LETTA_AVAILABLE:
            logger.warning(f"[{agent_name}] Letta client not available. Memory features disabled.")
            return
            
        if not self.config.auto_memory:
            logger.info(f"[{agent_name}] Auto-memory disabled via config.")
            return
            
        self._initialize()
    
    def _initialize(self):
        """Initialize connection to Letta server."""
        try:
            self.client = Letta(
                base_url=self.config.server_url,
                api_key=self.config.api_key
            )
            
            # Check server health
            health = self.client.health.check()
            if not health or not getattr(health, 'healthy', True):
                logger.warning(f"[{self.agent_name}] Letta server not healthy")
                return
                
            logger.info(f"[{self.agent_name}] Connected to Letta at {self.config.server_url}")
            
            # Get or create agent
            self.agent_id = self._get_or_create_agent()
            if self.agent_id:
                self._initialized = True
                logger.info(f"[{self.agent_name}] Memory manager initialized with agent {self.agent_id}")
                
        except Exception as e:
            logger.error(f"[{self.agent_name}] Failed to initialize memory manager: {e}")
    
    def _get_or_create_agent(self) -> Optional[str]:
        """Get existing agent or create new one."""
        try:
            # Try to find existing agent by name
            agents = self.client.agents.list()
            for agent in agents:
                if agent.name == self.agent_name:
                    logger.info(f"[{self.agent_name}] Found existing agent: {agent.id}")
                    return agent.id
            
            # Create new agent with memory blocks
            agent = self.client.agents.create(
                name=self.agent_name,
                memory_blocks=[
                    {
                        "label": "persona",
                        "value": f"I am an AI agent named {self.agent_name}. I maintain persistent memory across sessions."
                    },
                    {
                        "label": "human",
                        "value": "User preferences and context will be stored here."
                    },
                    {
                        "label": "projects",
                        "value": "Active projects: None"
                    },
                    {
                        "label": "autonomous_notes",
                        "value": "Autonomous memory notes will be stored here."
                    }
                ],
                tags=["autonomous", "ai-agent"] + self.config.memory_tags
            )
            
            logger.info(f"[{self.agent_name}] Created new agent: {agent.id}")
            return agent.id
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error creating agent: {e}")
            return None
    
    def start_session(self, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Start a new conversation session."""
        if not self._initialized or not self.client:
            return None
            
        try:
            meta = metadata or {}
            meta.update({
                "agent_name": self.agent_name,
                "session_start": datetime.now().isoformat(),
                "tags": self.config.memory_tags
            })
            
            conv = self.client.conversations.create(
                agent_id=self.agent_id,
                metadata=meta
            )
            self.conversation_id = conv.id
            logger.info(f"[{self.agent_name}] Started session: {conv.id}")
            return conv.id
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error starting session: {e}")
            return None
    
    def pre_task_hook(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Hook to call before executing a task.
        Retrieves relevant memories and returns them as context.
        """
        if not self._initialized:
            return ""
            
        try:
            # Ensure we have a conversation
            if not self.conversation_id:
                self.start_session()
                
            # Search archival memory for relevant context
            memories = self.search_memories(task_description, limit=5)
            
            # Get memory block values
            blocks = self.get_memory_blocks()
            
            # Compile context
            context_parts = []
            
            if memories:
                context_parts.append("## Relevant Past Memories:\n" + 
                                   "\n".join([f"- {m}" for m in memories]))
            
            if blocks.get("projects"):
                context_parts.append(f"## Active Projects:\n{blocks['projects']}")
                
            if blocks.get("human"):
                context_parts.append(f"## User Context:\n{blocks['human']}")
                
            compiled_context = "\n\n".join(context_parts)
            
            if compiled_context:
                logger.info(f"[{self.agent_name}] Retrieved {len(memories)} memories for task")
                
            return compiled_context
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error in pre_task_hook: {e}")
            return ""
    
    def post_task_hook(self, task_description: str, result: str, 
                       learned_facts: Optional[List[str]] = None):
        """
        Hook to call after executing a task.
        Stores memories and updates memory blocks.
        """
        if not self._initialized:
            return
            
        try:
            # Store task result in archival memory
            memory_text = f"Task: {task_description}\nResult: {result[:500]}"
            self.store_memory(memory_text, tags=["task", "autonomous"] + self.config.memory_tags)
            
            # Store learned facts
            if learned_facts:
                for fact in learned_facts:
                    self.store_memory(fact, tags=["fact", "learned"])
                    
            # Update conversation with summary
            if self.conversation_id and learned_facts:
                summary = f"Learned: {', '.join(learned_facts[:3])}"
                self._update_conversation_summary(summary)
                
            logger.info(f"[{self.agent_name}] Stored {len(learned_facts or [])} memories from task")
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error in post_task_hook: {e}")
    
    def store_memory(self, text: str, tags: Optional[List[str]] = None) -> bool:
        """Store text in archival memory."""
        if not self._initialized or not self.client:
            return False
            
        try:
            # Send as message to trigger archival storage
            # Letta automatically handles archival memory
            self.client.conversations.messages.create(
                conversation_id=self.conversation_id or self.start_session(),
                role="user",
                content=f"[MEMORY_STORE] {text}",
                tags=tags or ["autonomous"]
            )
            return True
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error storing memory: {e}")
            return False
    
    def search_memories(self, query: str, limit: int = 10) -> List[str]:
        """Search archival memory for relevant context."""
        if not self._initialized or not self.client:
            return []
            
        try:
            # Query via conversation - Letta handles retrieval
            response = self.client.conversations.messages.create(
                conversation_id=self.conversation_id or self.start_session(),
                role="user",
                content=f"[MEMORY_SEARCH] {query}"
            )
            
            # Extract memory references from response
            # This is simplified - actual implementation may vary based on Letta version
            return [response.message.content] if response else []
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error searching memories: {e}")
            return []
    
    def update_memory_block(self, label: str, value: str) -> bool:
        """Update a core memory block."""
        if not self._initialized or not self.client:
            return False
            
        try:
            # Update via agent memory tools
            self.client.agents.modify(
                agent_id=self.agent_id,
                memory_blocks=[{"label": label, "value": value}]
            )
            logger.info(f"[{self.agent_name}] Updated memory block: {label}")
            return True
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error updating memory block: {e}")
            return False
    
    def get_memory_blocks(self) -> Dict[str, str]:
        """Get all memory block values."""
        if not self._initialized or not self.client:
            return {}
            
        try:
            agent = self.client.agents.retrieve(self.agent_id)
            blocks = {}
            
            # Extract memory blocks from agent
            if hasattr(agent, 'memory_blocks'):
                for block in agent.memory_blocks:
                    blocks[block.label] = block.value
                    
            return blocks
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error getting memory blocks: {e}")
            return {}
    
    def _update_conversation_summary(self, summary: str):
        """Update conversation with summary."""
        try:
            self.client.conversations.modify(
                conversation_id=self.conversation_id,
                metadata={"summary": summary}
            )
        except Exception as e:
            logger.debug(f"[{self.agent_name}] Could not update conversation summary: {e}")
    
    def end_session(self, final_summary: Optional[str] = None):
        """End current session and store final summary."""
        if not self._initialized:
            return
            
        try:
            if final_summary and self.conversation_id:
                self.store_memory(final_summary, tags=["session_summary"])
                
            logger.info(f"[{self.agent_name}] Ended session: {self.conversation_id}")
            self.conversation_id = None
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error ending session: {e}")


class AutoMemoryDecorator:
    """Decorator for automatically adding memory to functions."""
    
    def __init__(self, agent_name: str, config: Optional[MemoryConfig] = None):
        self.memory = AutonomousMemoryManager(agent_name, config)
    
    def __call__(self, func: Callable) -> Callable:
        """Decorate a function with automatic memory."""
        
        def wrapper(*args, **kwargs):
            # Pre-task: get context
            task_desc = f"{func.__name__}({', '.join([str(a) for a in args])})"
            context = self.memory.pre_task_hook(task_desc)
            
            # Add context to kwargs if function accepts it
            if 'memory_context' in func.__code__.co_varnames:
                kwargs['memory_context'] = context
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Post-task: store learnings
            # Extract any returned facts
            learned = []
            if isinstance(result, dict) and 'facts' in result:
                learned = result['facts']
            
            self.memory.post_task_hook(task_desc, str(result), learned)
            
            return result
            
        return wrapper


# Convenience functions for quick usage

def create_memory_manager(agent_name: str) -> AutonomousMemoryManager:
    """Create a memory manager for an agent."""
    return AutonomousMemoryManager(agent_name)


def with_autonomous_memory(agent_name: str):
    """Decorator factory for adding memory to functions."""
    return AutoMemoryDecorator(agent_name)


# Auto-initialization for terminal agents
def auto_init_memory() -> Optional[AutonomousMemoryManager]:
    """
    Automatically initialize memory for current terminal agent.
    Detects agent from environment variables.
    """
    agent_name = os.getenv("AI_AGENT_NAME")
    
    if not agent_name:
        # Try to detect from terminal
        term = os.getenv("TERM_PROGRAM", "")
        if "code" in term.lower():
            agent_name = "vscode"
        elif os.getenv("WINDSURF_AGENT"):
            agent_name = "windsurf"
        else:
            agent_name = "terminal"
    
    if os.getenv("LETTA_AUTO_MEMORY", "true").lower() == "true":
        return create_memory_manager(agent_name)
    
    return None


# Global memory manager (initialized on first use)
_global_memory: Optional[AutonomousMemoryManager] = None

def get_memory() -> Optional[AutonomousMemoryManager]:
    """Get global memory manager."""
    global _global_memory
    if _global_memory is None:
        _global_memory = auto_init_memory()
    return _global_memory

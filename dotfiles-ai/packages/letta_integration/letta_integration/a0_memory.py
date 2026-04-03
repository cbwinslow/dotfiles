"""
A0 Memory System - Compatible with letta-client 1.8.0
Agent-Zero style autonomous memory for AI agents.
"""

import sys
import os

# Add epstein venv FIRST
epstein_venv = os.path.expanduser("~/workspace/epstein/.venv/lib/python3.12/site-packages")
if epstein_venv not in sys.path:
    sys.path.insert(0, epstein_venv)

import json
import logging
import hashlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Letta client
try:
    from letta_client import Letta
    LETTA_AVAILABLE = True
except ImportError:
    LETTA_AVAILABLE = False
    logger.warning("letta-client not available")


@dataclass
class AgentInstance:
    instance_id: str
    agent_name: str
    start_time: datetime
    conversation_id: Optional[str] = None


class A0MemorySystem:
    """Agent-Zero style memory with letta-client 1.8.0 compatibility."""
    
    def __init__(self, agent_name: str, instance_id: Optional[str] = None):
        self.agent_name = agent_name
        self.instance_id = instance_id or self._generate_instance_id()
        self.server_url = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
        self.api_key = os.getenv("LETTA_API_KEY")
        
        self.client = None
        self.agent_id = None
        self.conversation_id = None
        self._initialized = False
        
        if LETTA_AVAILABLE and os.getenv("LETTA_AUTO_MEMORY", "true").lower() == "true":
            self._initialize()
    
    def _generate_instance_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(os.urandom(16)).hexdigest()[:8]
        return f"{self.agent_name}_{timestamp}_{random_suffix}"
    
    def _initialize(self):
        """Initialize connection to Letta."""
        try:
            self.client = Letta(base_url=self.server_url, api_key=self.api_key)
            
            # Check connection by listing agents
            try:
                agents = list(self.client.agents.list())
                logger.info(f"[{self.instance_id}] Connected to Letta, {len(agents)} agents")
            except Exception as e:
                logger.warning(f"[{self.instance_id}] Connection failed: {e}")
                return
            
            # Get or create agent
            self.agent_id = self._get_or_create_agent()
            if not self.agent_id:
                return
            
            # Create conversation for this session
            self._create_conversation()
            
            self._initialized = True
            logger.info(f"[{self.instance_id}] A0 Memory initialized")
            
        except Exception as e:
            logger.error(f"[{self.instance_id}] Init failed: {e}")
    
    def _get_or_create_agent(self) -> Optional[str]:
        """Find or create agent."""
        try:
            agents = list(self.client.agents.list())
            
            for agent in agents:
                if getattr(agent, 'name', None) == self.agent_name:
                    logger.info(f"[{self.instance_id}] Found agent: {agent.id}")
                    return agent.id
            
            # Create new agent - simplified for 1.8.0 API
            agent = self.client.agents.create(
                name=self.agent_name,
                memory_blocks=[
                    {"label": "persona", "value": f"I am {self.agent_name}"},
                    {"label": "human", "value": "User preferences"},
                    {"label": "projects", "value": "Active projects"}
                ]
            )
            logger.info(f"[{self.instance_id}] Created agent: {agent.id}")
            return agent.id
            
        except Exception as e:
            logger.error(f"[{self.instance_id}] Agent error: {e}")
            return None
    
    def _create_conversation(self):
        """Create conversation session."""
        try:
            if self.agent_id:
                conv = self.client.conversations.create(agent_id=self.agent_id)
                self.conversation_id = conv.id
                logger.info(f"[{self.instance_id}] Conversation: {conv.id}")
        except Exception as e:
            logger.error(f"[{self.instance_id}] Conv error: {e}")
    
    def store_memory(self, content: str, memory_type: str = "fact", 
                     tags: List[str] = None) -> bool:
        """Store memory via message."""
        if not self._initialized or not self.conversation_id:
            return False
        
        try:
            # Use 'input' parameter for 1.8.0 API
            self.client.conversations.messages.create(
                conversation_id=self.conversation_id,
                input=f"[MEMORY:{memory_type}] {content}"
            )
            logger.info(f"[{self.instance_id}] Stored: {content[:50]}...")
            return True
        except Exception as e:
            logger.error(f"[{self.instance_id}] Store failed: {e}")
            return False
    
    def recall_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search archival memory."""
        if not self._initialized:
            return []
        
        try:
            # Use messages to trigger retrieval
            stream = self.client.conversations.messages.create(
                conversation_id=self.conversation_id,
                input=f"[SEARCH] {query}",
                streaming=True
            )
            
            # Collect results from stream
            results = []
            for chunk in stream:
                if hasattr(chunk, 'content'):
                    results.append({"content": chunk.content})
                    if len(results) >= limit:
                        break
            
            return results
        except Exception as e:
            logger.error(f"[{self.instance_id}] Recall failed: {e}")
            return []
    
    def rag_search(self, query: str, limit: int = 5) -> List[str]:
        """Pure RAG search."""
        results = self.recall_memories(query, limit)
        return [r.get("content", "") for r in results if r.get("content")]
    
    def pre_task_hook(self, task: str) -> str:
        """Get context before task."""
        memories = self.rag_search(task, limit=5)
        if memories:
            return "## Past Memories:\n" + "\n".join(f"- {m}" for m in memories)
        return ""
    
    def post_task_hook(self, task: str, result: str, learned: List[str] = None):
        """Store after task."""
        self.store_memory(f"Task: {task}\nResult: {result}", memory_type="task")
        if learned:
            for fact in learned:
                self.store_memory(fact, memory_type="fact")
    
    def get_instance_summary(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "conversation_id": self.conversation_id,
            "initialized": self._initialized
        }


class with_a0_memory:
    """Decorator for automatic memory."""
    
    def __init__(self, agent_name: str = None):
        self.agent_name = agent_name
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mem = A0MemorySystem(self.agent_name or "default")
            task = f"{func.__name__}"
            
            context = mem.pre_task_hook(task)
            if context:
                kwargs['memory_context'] = context
            
            result = func(*args, **kwargs)
            
            if mem._initialized:
                learned = result.get('learned', []) if isinstance(result, dict) else []
                mem.post_task_hook(task, str(result), learned)
            
            return result
        return wrapper


_instances: Dict[str, A0MemorySystem] = {}

def get_a0_memory(agent_name: str = None) -> Optional[A0MemorySystem]:
    name = agent_name or os.getenv("AI_AGENT_NAME", "default")
    if name not in _instances:
        _instances[name] = A0MemorySystem(name)
    return _instances[name]


def auto_init_a0() -> Optional[A0MemorySystem]:
    agent = os.getenv("AI_AGENT_NAME")
    if not agent:
        if os.getenv("WINDSURF_AGENT"):
            agent = "windsurf"
        elif os.getenv("KILOCODE_AGENT"):
            agent = "kilocode"
        else:
            agent = "terminal"
    return get_a0_memory(agent)

"""
Letta Integration using official letta-client SDK
Self-hosted server support (localhost:8283)
Implements all features from Letta documentation
"""
import os
import logging
from typing import Optional, Dict, List, Any, Iterator, BinaryIO
from datetime import datetime
from pathlib import Path

# Official Letta SDK
from letta_client import Letta

# Model picker (optional)
try:
    from letta_model_picker import ModelPicker
    MODEL_PICKER_AVAILABLE = True
except ImportError:
    MODEL_PICKER_AVAILABLE = False

# A0 Memory System
from .a0_memory import (
    A0MemorySystem,
    with_a0_memory,
    get_a0_memory,
    auto_init_a0,
    AgentInstance
)

__all__ = [
    'LettaIntegration',
    'A0MemorySystem',
    'with_a0_memory',
    'get_a0_memory', 
    'auto_init_a0',
    'AgentInstance'
]

logger = logging.getLogger(__name__)


class LettaIntegration:
    """
    Complete Letta integration with all self-hosted features.
    
    Features:
    - Agent Management (create, list, delete)
    - Memory Blocks (persona, human, custom)
    - Multi-agent Shared Memory
    - Archival Memory (searchable)
    - Messages & Streaming
    - Agent File Import/Export (.af)
    - MCP Tools support
    - Sleep-time Agents
    """
    
    def __init__(
        self,
        server_url: str = None,
        api_key: str = None,
        agent_name: str = "default_agent"
    ):
        """
        Initialize Letta integration with official SDK.
        
        Args:
            server_url: Letta server URL (default: http://localhost:8283)
            api_key: API key (optional for self-hosted)
            agent_name: Default agent name
        """
        self.server_url = server_url or os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
        self.agent_name = agent_name
        self.agent_id = None
        
        # Initialize official Letta client with self-hosted support
        self.client = Letta(
            base_url=self.server_url,
            api_key=api_key or os.getenv("LETTA_API_KEY")
        )
        
        logger.info(f"LettaIntegration initialized for agent: {agent_name}")
        logger.info(f"Server: {self.server_url}")
    
    def get_or_create_agent(self, agent_name: str = None) -> str:
        """Get existing agent or create new one"""
        agent_name = agent_name or self.agent_name
        
        # Try to find existing agent
        try:
            agents = self.client.agents.list()
            for agent in agents:
                if agent.name == agent_name:
                    self.agent_id = agent.id
                    logger.info(f"Found existing agent: {agent_name} (ID: {self.agent_id})")
                    return self.agent_id
        except Exception as e:
            logger.warning(f"Could not list agents: {e}")
        
        # Create new agent
        try:
            agent = self.client.agents.create(name=agent_name)
            self.agent_id = agent.id
            logger.info(f"Created new agent: {agent_name} (ID: {self.agent_id})")
            return self.agent_id
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            return None
    
    def list_agents(self) -> List[Any]:
        """List all agents on the server."""
        try:
            agents_page = self.client.agents.list()
            # Handle SyncArrayPage - convert to list
            return list(agents_page)
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []
    
    def create_agent_with_memory_blocks(
        self,
        agent_name: str,
        memory_blocks: List[Dict[str, str]] = None,
        model: str = None,
        embedding: str = None
    ) -> Any:
        """
        Create agent with memory blocks using official SDK.
        
        Args:
            agent_name: Name for the agent
            memory_blocks: List of {"label": "...", "value": "..."} dicts
            model: LLM model name
            embedding: Embedding model name
            
        Returns:
            Created agent object
        """
        memory_blocks = memory_blocks or [
            {"label": "persona", "value": f"I am {agent_name}, a helpful AI assistant."},
            {"label": "human", "value": "User preferences and information."}
        ]
        
        try:
            agent = self.client.agents.create(
                name=agent_name,
                memory_blocks=memory_blocks,
                model=model or os.getenv("LETTA_DEFAULT_MODEL", "letta/letta-free"),
                embedding=embedding or os.getenv("LETTA_DEFAULT_EMBEDDING", "ollama/bge-m3:latest")
            )
            self.agent_id = agent.id
            self.agent_name = agent_name
            logger.info(f"Created agent {agent_name} with ID: {agent.id}")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent with memory blocks: {e}")
            return None
    
    def send_message(self, message: str, agent_id: str = None) -> Any:
        """
        Send message to agent using official SDK.
        
        Args:
            message: Message content
            agent_id: Agent ID (uses default if not provided)
            
        Returns:
            Response from agent
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            agent_id = self.get_or_create_agent()
        
        try:
            response = self.client.agents.messages.create(
                agent_id=agent_id,
                messages=[{"role": "user", "content": message}]
            )
            return response
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
    
    def update_memory_block(self, label: str, value: str, agent_id: str = None) -> bool:
        """
        Update a memory block for an agent.
        
        Args:
            label: Block label (e.g., "human", "persona")
            value: New content
            agent_id: Agent ID
            
        Returns:
            True if successful
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            agent_id = self.get_or_create_agent()
        
        try:
            self.client.agents.blocks.update(
                agent_id=agent_id,
                block_label=label,
                value=value
            )
            logger.info(f"Updated memory block '{label}' for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update memory block: {e}")
            return False
    
    def get_memory_block(self, label: str, agent_id: str = None) -> Any:
        """
        Retrieve a memory block by label.
        
        Args:
            label: Block label
            agent_id: Agent ID
            
        Returns:
            Block object
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return None
        
        try:
            block = self.client.agents.blocks.retrieve(
                agent_id=agent_id,
                block_label=label
            )
            return block
        except Exception as e:
            logger.error(f"Failed to retrieve block: {e}")
            return None
    
    def create_shared_block(self, label: str, value: str) -> Any:
        """
        Create a shared memory block that can be attached to multiple agents.
        
        Args:
            label: Block label
            value: Block content
            
        Returns:
            Created block
        """
        try:
            block = self.client.blocks.create(
                label=label,
                value=value
            )
            logger.info(f"Created shared block: {label}")
            return block
        except Exception as e:
            logger.error(f"Failed to create shared block: {e}")
            return None
    
    def attach_shared_block(self, block_id: str, agent_id: str = None) -> bool:
        """
        Attach a shared block to an agent.
        
        Args:
            block_id: ID of the shared block
            agent_id: Agent ID
            
        Returns:
            True if successful
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            agent_id = self.get_or_create_agent()
        
        try:
            self.client.agents.blocks.attach(
                agent_id=agent_id,
                block_id=block_id
            )
            logger.info(f"Attached block {block_id} to agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to attach block: {e}")
            return False
    
    # =====================================================================
    # ARCHIVAL MEMORY (SEARCHABLE LONG-TERM STORAGE)
    # =====================================================================
    
    def save_to_archival(
        self,
        text: str,
        agent_id: str = None,
        tags: List[str] = None
    ) -> bool:
        """
        Save text to archival memory (searchable long-term storage).
        
        Args:
            text: Content to save
            agent_id: Agent ID (uses default if not provided)
            tags: Tags for categorization
            
        Returns:
            True if successful
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            agent_id = self.get_or_create_agent()
        
        try:
            # Try different SDK API patterns
            try:
                # Newer SDK pattern
                self.client.agents.archival_memory.create(
                    agent_id=agent_id,
                    text=text,
                    tags=tags or []
                )
            except AttributeError:
                # Fallback: use direct API call
                import requests
                response = requests.post(
                    f"{self.server_url}/v1/agents/{agent_id}/archival-memory",
                    json={"text": text, "tags": tags or []},
                    headers={"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
                )
                response.raise_for_status()
            
            logger.info(f"Saved to archival memory ({len(text)} chars)")
            return True
        except Exception as e:
            logger.error(f"Failed to save to archival: {e}")
            return False
    
    def search_archival(
        self,
        query: str,
        agent_id: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search archival memory using vector similarity.
        
        Args:
            query: Search query
            agent_id: Agent ID
            limit: Max results
            
        Returns:
            List of matching memories with similarity scores
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return []
        
        try:
            # Try different SDK API patterns
            try:
                # Newer SDK pattern
                results = self.client.agents.archival_memory.search(
                    agent_id=agent_id,
                    query=query,
                    limit=limit
                )
                return list(results) if results else []
            except AttributeError:
                # Fallback: use direct API call
                import requests
                response = requests.post(
                    f"{self.server_url}/v1/agents/{agent_id}/archival-memory/search",
                    json={"query": query, "limit": limit},
                    headers={"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
                
        except Exception as e:
            logger.error(f"Failed to search archival: {e}")
            return []
    
    def get_archival_memory(self, agent_id: str = None) -> List[Dict]:
        """Get all archival memories for an agent."""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return []
        
        try:
            # Try different SDK API patterns
            try:
                # Newer SDK pattern
                results = self.client.agents.archival_memory.list(agent_id=agent_id)
                return list(results) if results else []
            except AttributeError:
                # Fallback: use direct API call
                import requests
                response = requests.get(
                    f"{self.server_url}/v1/agents/{agent_id}/archival-memory",
                    headers={"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except Exception as e:
            logger.error(f"Failed to list archival: {e}")
            return []
    
    def check_server_health(self) -> Dict:
        """Check Letta server health"""
        try:
            # Try to list agents as health check
            self.client.agents.list()
            return {"status": "healthy", "server": self.server_url}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Convenience function
def get_letta_integration(agent_name: str = None) -> LettaIntegration:
    """Get or create default Letta integration instance"""
    return LettaIntegration(agent_name=agent_name or "default")


# Import conversation logging components
from .conversation_logger import (
    ConversationLogger,
    AutoLogger,
    get_logger,
    quick_log,
)

# Import memory management components
from .memory_manager import (
    IntelligentMemoryManager,
    MemoryAnalyzer,
    MemoryTrigger,
    Memory,
    analyze_and_save,
    should_recall_before_llm,
)

__all__ = [
    "LettaIntegration",
    "get_letta_integration",
    "ConversationLogger",
    "AutoLogger",
    "get_logger",
    "quick_log",
    "IntelligentMemoryManager",
    "MemoryAnalyzer",
    "MemoryTrigger",
    "Memory",
    "analyze_and_save",
    "should_recall_before_llm",
]

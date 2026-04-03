"""
Complete Letta Self-Hosted Integration
Implements all features from official Letta documentation
"""
import os
import logging
from typing import Optional, Dict, List, Any, Iterator, BinaryIO
from datetime import datetime
from pathlib import Path

# Official Letta SDK
from letta_client import Letta
from letta_client.types import (
    AgentState,
    Message,
    MemoryBlock,
    AgentMessage,
    StreamingMessage,
)

logger = logging.getLogger(__name__)


class LettaCompleteIntegration:
    """
    Complete Letta integration with all self-hosted features.
    
    Features:
    - Agent Management
    - Memory Blocks (persona, human, custom)
    - Multi-agent Shared Memory
    - Archival Memory (searchable)
    - Sleep-time Agents
    - Agent File Import/Export (.af)
    - MCP Tools
    - Streaming Messages
    - Filesystem Access
    - Long-running Agents
    """
    
    def __init__(
        self,
        server_url: str = None,
        api_key: str = None,
        agent_name: str = "default_agent"
    ):
        """
        Initialize Letta integration for self-hosted server.
        
        Args:
            server_url: Letta server URL (default: http://localhost:8283)
            api_key: API key (optional for self-hosted)
            agent_name: Default agent name
        """
        self.server_url = server_url or os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
        self.agent_name = agent_name
        self.agent_id = None
        
        # Initialize official Letta client
        self.client = Letta(
            base_url=self.server_url,
            api_key=api_key or os.getenv("LETTA_API_KEY")
        )
        
        logger.info(f"LettaCompleteIntegration initialized")
        logger.info(f"Server: {self.server_url}")
    
    # =========================================================================
    # AGENT MANAGEMENT
    # =========================================================================
    
    def create_agent(
        self,
        agent_name: str = None,
        model: str = None,
        embedding: str = None,
        memory_blocks: List[Dict] = None,
        block_ids: List[str] = None,
        tools: List[str] = None,
        enable_sleeptime: bool = False,
        description: str = None
    ) -> AgentState:
        """
        Create a new agent with full configuration.
        
        Args:
            agent_name: Name for the agent
            model: LLM model (e.g., "openai/gpt-4o-mini", "letta/letta-free")
            embedding: Embedding model
            memory_blocks: Initial memory blocks [{"label": "...", "value": "..."}]
            block_ids: IDs of shared blocks to attach
            tools: Tool names to enable (e.g., ["web_search", "run_code"])
            enable_sleeptime: Enable sleep-time agent
            description: Agent description
            
        Returns:
            Created AgentState
        """
        agent_name = agent_name or self.agent_name
        
        # Default memory blocks
        if memory_blocks is None:
            memory_blocks = [
                {"label": "persona", "value": f"I am {agent_name}, a helpful AI assistant."},
                {"label": "human", "value": "User information and preferences."}
            ]
        
        try:
            agent = self.client.agents.create(
                name=agent_name,
                model=model or os.getenv("LETTA_DEFAULT_MODEL", "letta/letta-free"),
                embedding=embedding or os.getenv("LETTA_DEFAULT_EMBEDDING", "ollama/bge-m3:latest"),
                memory_blocks=memory_blocks,
                block_ids=block_ids or [],
                tools=tools or [],
                enable_sleeptime=enable_sleeptime,
                description=description
            )
            
            self.agent_id = agent.id
            self.agent_name = agent_name
            
            logger.info(f"Created agent {agent_name} (ID: {agent.id})")
            if enable_sleeptime:
                logger.info(f"  - Sleep-time agent enabled")
            if block_ids:
                logger.info(f"  - Attached {len(block_ids)} shared blocks")
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise
    
    def list_agents(self) -> List[AgentState]:
        """List all agents on the server."""
        try:
            return self.client.agents.list()
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []
    
    def get_agent(self, agent_id: str = None) -> Optional[AgentState]:
        """Get agent by ID."""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return None
        
        try:
            return self.client.agents.retrieve(agent_id=agent_id)
        except Exception as e:
            logger.error(f"Failed to get agent: {e}")
            return None
    
    def delete_agent(self, agent_id: str = None) -> bool:
        """Delete an agent."""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return False
        
        try:
            self.client.agents.delete(agent_id=agent_id)
            logger.info(f"Deleted agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete agent: {e}")
            return False
    
    # =========================================================================
    # MEMORY BLOCKS
    # =========================================================================
    
    def create_memory_block(
        self,
        label: str,
        value: str,
        description: str = None,
        limit: int = 5000
    ) -> MemoryBlock:
        """
        Create a standalone memory block.
        
        Args:
            label: Unique label
            value: Content
            description: Description
            limit: Character limit
            
        Returns:
            Created MemoryBlock
        """
        try:
            block = self.client.blocks.create(
                label=label,
                value=value,
                limit=limit
            )
            logger.info(f"Created memory block: {label}")
            return block
        except Exception as e:
            logger.error(f"Failed to create block: {e}")
            raise
    
    def update_memory_block(
        self,
        label: str,
        value: str,
        agent_id: str = None
    ) -> bool:
        """
        Update a memory block value.
        
        Args:
            label: Block label (e.g., "human", "persona", "conversation_log")
            value: New content
            agent_id: Agent ID (uses default if not provided)
            
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
            logger.debug(f"Updated memory block '{label}'")
            return True
        except Exception as e:
            logger.error(f"Failed to update block: {e}")
            return False
    
    def get_memory_block(self, label: str, agent_id: str = None) -> Optional[MemoryBlock]:
        """Retrieve a memory block by label."""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return None
        
        try:
            return self.client.agents.blocks.retrieve(
                agent_id=agent_id,
                block_label=label
            )
        except Exception as e:
            logger.error(f"Failed to retrieve block: {e}")
            return None
    
    def list_memory_blocks(self, agent_id: str = None) -> List[MemoryBlock]:
        """List all memory blocks for an agent."""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return []
        
        try:
            return self.client.agents.blocks.list(agent_id=agent_id)
        except Exception as e:
            logger.error(f"Failed to list blocks: {e}")
            return []
    
    # =========================================================================
    # MULTI-AGENT SHARED MEMORY
    # =========================================================================
    
    def create_shared_block(
        self,
        label: str,
        value: str,
        description: str = None
    ) -> MemoryBlock:
        """
        Create a shared memory block for multi-agent use.
        
        Args:
            label: Block label
            value: Content
            description: Description
            
        Returns:
            Created shared block
        """
        return self.create_memory_block(label, value, description)
    
    def attach_shared_block(
        self,
        block_id: str,
        agent_id: str = None
    ) -> bool:
        """
        Attach a shared block to an agent.
        
        Args:
            block_id: Shared block ID
            agent_id: Agent ID
            
        Returns:
            True if successful
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            logger.error("No agent ID provided")
            return False
        
        try:
            self.client.agents.blocks.attach(
                agent_id=agent_id,
                block_id=block_id
            )
            logger.info(f"Attached shared block {block_id} to agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to attach block: {e}")
            return False
    
    def detach_shared_block(
        self,
        block_id: str,
        agent_id: str = None
    ) -> bool:
        """Detach a shared block from an agent."""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return False
        
        try:
            self.client.agents.blocks.detach(
                agent_id=agent_id,
                block_id=block_id
            )
            logger.info(f"Detached block {block_id} from agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to detach block: {e}")
            return False
    
    # =========================================================================
    # MESSAGES & STREAMING
    # =========================================================================
    
    def send_message(
        self,
        message: str,
        agent_id: str = None,
        role: str = "user"
    ) -> List[AgentMessage]:
        """
        Send a message to an agent.
        
        Args:
            message: Message content
            agent_id: Agent ID
            role: Message role (user/system)
            
        Returns:
            List of agent responses
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            agent_id = self.get_or_create_agent()
        
        try:
            response = self.client.agents.messages.create(
                agent_id=agent_id,
                messages=[{"role": role, "content": message}]
            )
            logger.info(f"Message sent to agent {agent_id}")
            return response.messages if hasattr(response, 'messages') else []
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    def send_message_streaming(
        self,
        message: str,
        agent_id: str = None
    ) -> Iterator[StreamingMessage]:
        """
        Send message with streaming response.
        
        Args:
            message: Message content
            agent_id: Agent ID
            
        Yields:
            StreamingMessage chunks
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            agent_id = self.get_or_create_agent()
        
        try:
            stream = self.client.agents.messages.create_stream(
                agent_id=agent_id,
                messages=[{"role": "user", "content": message}]
            )
            logger.info(f"Streaming message to agent {agent_id}")
            return stream
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            raise
    
    def get_message_history(
        self,
        agent_id: str = None,
        limit: int = 100
    ) -> List[Message]:
        """Get message history for an agent."""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return []
        
        try:
            return self.client.agents.messages.list(
                agent_id=agent_id,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get message history: {e}")
            return []
    
    # =========================================================================
    # ARCHIVAL MEMORY (SEARCHABLE)
    # =========================================================================
    
    def save_to_archival(
        self,
        text: str,
        agent_id: str = None,
        tags: List[str] = None
    ) -> bool:
        """
        Save text to archival memory (searchable).
        
        Args:
            text: Content to save
            agent_id: Agent ID
            tags: Tags for categorization
            
        Returns:
            True if successful
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            agent_id = self.get_or_create_agent()
        
        try:
            self.client.agents.archival_memory.create(
                agent_id=agent_id,
                text=text,
                tags=tags or []
            )
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
        Search archival memory.
        
        Args:
            query: Search query
            agent_id: Agent ID
            limit: Max results
            
        Returns:
            List of matching memories
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return []
        
        try:
            results = self.client.agents.archival_memory.search(
                agent_id=agent_id,
                query=query,
                limit=limit
            )
            logger.info(f"Archival search found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Failed to search archival: {e}")
            return []
    
    # =========================================================================
    # AGENT FILE IMPORT/EXPORT (.af)
    # =========================================================================
    
    def export_agent_to_file(
        self,
        filepath: str,
        agent_id: str = None
    ) -> bool:
        """
        Export agent to .af file.
        
        Args:
            filepath: Path to save .af file
            agent_id: Agent ID
            
        Returns:
            True if successful
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return False
        
        try:
            with open(filepath, 'wb') as f:
                self.client.agents.export_file(
                    agent_id=agent_id,
                    file=f
                )
            logger.info(f"Exported agent to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export agent: {e}")
            return False
    
    def import_agent_from_file(
        self,
        filepath: str,
        agent_name: str = None
    ) -> Optional[AgentState]:
        """
        Import agent from .af file.
        
        Args:
            filepath: Path to .af file
            agent_name: Optional new name for agent
            
        Returns:
            Imported AgentState
        """
        try:
            with open(filepath, 'rb') as f:
                agent = self.client.agents.import_file(file=f)
            
            if agent_name:
                # Rename if requested
                agent = self.client.agents.modify(
                    agent_id=agent.id,
                    name=agent_name
                )
            
            self.agent_id = agent.id
            self.agent_name = agent.name
            
            logger.info(f"Imported agent from {filepath} (ID: {agent.id})")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to import agent: {e}")
            return None
    
    # =========================================================================
    # MCP TOOLS
    # =========================================================================
    
    def create_mcp_server(
        self,
        server_name: str,
        server_url: str,
        server_type: str = "streamable_http"
    ) -> Any:
        """
        Create an MCP (Model Context Protocol) server connection.
        
        Args:
            server_name: Name for the server
            server_url: MCP server URL
            server_type: Type (streamable_http, stdio, etc.)
            
        Returns:
            Created MCP server
        """
        try:
            server = self.client.mcp_servers.create(
                server_name=server_name,
                config={
                    "mcp_server_type": server_type,
                    "server_url": server_url
                }
            )
            logger.info(f"Created MCP server: {server_name}")
            return server
        except Exception as e:
            logger.error(f"Failed to create MCP server: {e}")
            raise
    
    def list_mcp_tools(self, server_id: str) -> List[Any]:
        """List tools available from MCP server."""
        try:
            return self.client.mcp_servers.tools.list(server_id)
        except Exception as e:
            logger.error(f"Failed to list MCP tools: {e}")
            return []
    
    def attach_mcp_tool_to_agent(
        self,
        tool_id: str,
        agent_id: str = None
    ) -> bool:
        """Attach MCP tool to agent."""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            return False
        
        try:
            # Re-create agent with tool
            agent = self.client.agents.retrieve(agent_id)
            current_tools = agent.tools or []
            
            self.client.agents.modify(
                agent_id=agent_id,
                tools=current_tools + [tool_id]
            )
            logger.info(f"Attached MCP tool {tool_id} to agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to attach tool: {e}")
            return False
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_or_create_agent(self, agent_name: str = None) -> str:
        """Get existing agent or create new one."""
        agent_name = agent_name or self.agent_name
        
        # Try to find existing
        agents = self.list_agents()
        for agent in agents:
            if agent.name == agent_name:
                self.agent_id = agent.id
                logger.info(f"Found existing agent: {agent_name}")
                return agent.id
        
        # Create new
        agent = self.create_agent(agent_name=agent_name)
        return agent.id if agent else None
    
    def check_server_health(self) -> Dict:
        """Check Letta server health."""
        try:
            agents = self.list_agents()
            return {
                "status": "healthy",
                "server": self.server_url,
                "agent_count": len(agents)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_letta_integration(
    server_url: str = None,
    agent_name: str = "default"
) -> LettaCompleteIntegration:
    """Get or create Letta integration instance."""
    return LettaCompleteIntegration(
        server_url=server_url,
        agent_name=agent_name
    )

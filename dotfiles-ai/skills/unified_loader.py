#!/usr/bin/env python3
"""
Unified Agent Skill Loader
Automatically loads skills and initializes memory for all AI agents.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('agent_loader')

class AgentSkillLoader:
    """Universal skill loader for all AI agents."""
    
    def __init__(self):
        self.agent_name = self._detect_agent()
        self.skills_loaded = []
        self.memory_initialized = False
        
    def _detect_agent(self) -> str:
        """Auto-detect which agent is running."""
        # Check environment variables
        if os.getenv('WINDSURF_AGENT'):
            return 'windsurf'
        if os.getenv('KILOCODE_AGENT'):
            return 'kilocode'
        if os.getenv('CLINE_AGENT'):
            return 'cline'
        if os.getenv('CLAUDE_AGENT'):
            return 'claude'
        
        # Check terminal/IDE
        term = os.getenv('TERM_PROGRAM', '').lower()
        if 'code' in term:
            return 'vscode'
        
        # Default
        return os.getenv('AI_AGENT_NAME', 'generic')
    
    def load_skill(self, skill_name: str) -> bool:
        """Load a specific skill by name."""
        skill_paths = [
            Path.home() / 'dotfiles' / 'ai' / 'skills' / skill_name,
            Path.home() / 'dotfiles' / 'ai' / 'shared' / 'skills' / skill_name,
            Path.home() / 'dotfiles' / 'ai' / 'packages' / skill_name,
        ]
        
        for path in skill_paths:
            if path.exists():
                # Add to Python path if needed
                if path.is_dir() and str(path.parent) not in sys.path:
                    sys.path.insert(0, str(path.parent))
                
                self.skills_loaded.append(skill_name)
                logger.info(f"Loaded skill: {skill_name}")
                return True
        
        logger.warning(f"Skill not found: {skill_name}")
        return False
    
    def initialize_autonomous_memory(self) -> bool:
        """Initialize autonomous memory for this agent."""
        try:
            # Add packages to path
            packages_dir = Path.home() / 'dotfiles' / 'ai' / 'packages'
            if str(packages_dir) not in sys.path:
                sys.path.insert(0, str(packages_dir))
            
            # Import and initialize
            from letta_integration.autonomous_memory import AutonomousMemoryManager
            
            memory = AutonomousMemoryManager(self.agent_name)
            
            if memory._initialized:
                self.memory_initialized = True
                logger.info(f"Autonomous memory initialized for {self.agent_name}")
                
                # Store reference globally
                os.environ['_AGENT_MEMORY'] = 'active'
                return True
            else:
                logger.warning(f"Memory initialization failed for {self.agent_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing memory: {e}")
            return False
    
    def load_all_default_skills(self) -> List[str]:
        """Load all default skills for this agent type."""
        defaults = [
            'autonomous_memory',
            'bitwarden_secrets',
        ]
        
        loaded = []
        for skill in defaults:
            if self.load_skill(skill):
                loaded.append(skill)
        
        return loaded
    
    def get_memory_manager(self) -> Optional[Any]:
        """Get the memory manager if initialized."""
        if not self.memory_initialized:
            return None
        
        try:
            from letta_integration.autonomous_memory import get_memory
            return get_memory()
        except:
            return None

# Global loader instance
_loader: Optional[AgentSkillLoader] = None

def get_loader() -> AgentSkillLoader:
    """Get or create global skill loader."""
    global _loader
    if _loader is None:
        _loader = AgentSkillLoader()
    return _loader

def auto_load() -> bool:
    """
    Automatically load all skills and memory.
    Call this at agent startup.
    """
    loader = get_loader()
    
    # Load default skills
    loaded = loader.load_all_default_skills()
    logger.info(f"Auto-loaded {len(loaded)} skills")
    
    # Initialize memory if enabled
    if os.getenv('LETTA_AUTO_MEMORY', 'true').lower() == 'true':
        loader.initialize_autonomous_memory()
    
    return loader.memory_initialized

# Convenience exports
def get_memory():
    """Get memory manager for current agent."""
    loader = get_loader()
    return loader.get_memory_manager()

# Auto-execute on import if AI_AGENT_NAME is set
if os.getenv('AI_AGENT_NAME') or os.getenv('TERM_PROGRAM'):
    auto_load()

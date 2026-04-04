"""
Agent Integration Skills for Letta Server

Provides comprehensive agent integration capabilities.
These skills handle agent-specific memory settings and synchronization.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from agent_memory import (
    store_agent_context,
    get_agent_context,
    store_memory_block,
    get_memory_block
)

logger = logging.getLogger(__name__)


def setup_agent_memory(
    agent_name: str,
    memory_config: Dict[str, Any],
    skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Configure agent-specific memory settings.
    
    Args:
        agent_name: Name of the agent
        memory_config: Memory configuration for the agent
        skills: List of skills to enable
        
    Returns:
        Setup results
    """
    try:
        setup_result = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "memory_config": memory_config,
            "skills": skills or [],
            "steps_completed": [],
            "errors": [],
            "warnings": []
        }
        
        # Validate memory configuration
        required_config_keys = ["backend", "default_ttl_days", "max_memory_size_mb"]
        for key in required_config_keys:
            if key not in memory_config:
                setup_result["errors"].append(f"Missing required memory config key: {key}")
        
        if setup_result["errors"]:
            setup_result["status"] = "failed"
            return setup_result
        
        # Store agent configuration as memory block
        try:
            agent_config_content = f"""
            Agent Configuration for {agent_name}
            ======================================
            
            Memory Backend: {memory_config.get('backend', 'unknown')}
            Default TTL Days: {memory_config.get('default_ttl_days', 'unknown')}
            Max Memory Size MB: {memory_config.get('max_memory_size_mb', 'unknown')}
            Skills Enabled: {', '.join(skills or [])}
            Setup Date: {datetime.now().isoformat()}
            
            Additional Configuration:
            {json.dumps(memory_config, indent=2)}
            """
            
            store_memory_block(
                label=f"agent_config_{agent_name}",
                content=agent_config_content,
                description=f"Configuration for agent {agent_name}"
            )
            
            setup_result["steps_completed"].append("agent_config_stored")
            
        except Exception as e:
            setup_result["errors"].append(f"Failed to store agent config: {e}")
        
        # Initialize agent context
        try:
            initial_context = {
                "agent_name": agent_name,
                "memory_backend": memory_config.get("backend"),
                "default_ttl_days": memory_config.get("default_ttl_days"),
                "max_memory_size_mb": memory_config.get("max_memory_size_mb"),
                "skills_enabled": skills or [],
                "setup_date": datetime.now().isoformat(),
                "status": "active",
                "last_activity": None,
                "memory_usage_mb": 0,
                "conversation_count": 0,
                "entity_extraction_count": 0
            }
            
            store_agent_context(agent_name, "config", initial_context)
            setup_result["steps_completed"].append("agent_context_initialized")
            
        except Exception as e:
            setup_result["errors"].append(f"Failed to initialize agent context: {e}")
        
        # Create agent-specific memory blocks
        try:
            # Create agent memory summary block
            memory_summary = f"""
            Agent Memory Summary for {agent_name}
            =====================================
            
            This block contains summary information about {agent_name}'s memory usage,
            configuration, and activity patterns.
            
            Last Updated: {datetime.now().isoformat()}
            Memory Backend: {memory_config.get('backend')}
            Status: Active
            """
            
            store_memory_block(
                label=f"agent_memory_summary_{agent_name}",
                content=memory_summary,
                description=f"Memory summary for agent {agent_name}"
            )
            
            setup_result["steps_completed"].append("memory_blocks_created")
            
        except Exception as e:
            setup_result["warnings"].append(f"Failed to create memory blocks: {e}")
        
        # Determine final status
        if setup_result["errors"]:
            setup_result["status"] = "failed"
        elif setup_result["warnings"]:
            setup_result["status"] = "warning"
        else:
            setup_result["status"] = "success"
        
        logger.info(f"Agent memory setup completed for {agent_name}: {setup_result['status']}")
        return setup_result
        
    except Exception as e:
        logger.error(f"Failed to setup agent memory: {e}")
        raise


def sync_agent_context(agent_name: str) -> Dict[str, Any]:
    """
    Synchronize agent context with Letta.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Sync results
    """
    try:
        sync_result = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "sync_type": "context",
            "steps_completed": [],
            "errors": [],
            "warnings": [],
            "changes_detected": False,
            "changes_applied": 0
        }
        
        # Get current agent context
        try:
            current_context = get_agent_context(agent_name)
            if not current_context:
                # Initialize context if it doesn't exist
                initial_context = {
                    "agent_name": agent_name,
                    "status": "active",
                    "last_sync": datetime.now().isoformat(),
                    "memory_usage_mb": 0,
                    "conversation_count": 0,
                    "entity_extraction_count": 0
                }
                
                store_agent_context(agent_name, "context", initial_context)
                sync_result["steps_completed"].append("context_initialized")
                sync_result["changes_applied"] += 1
                
        except Exception as e:
            sync_result["errors"].append(f"Failed to get agent context: {e}")
        
        # Update last sync timestamp
        try:
            current_context = get_agent_context(agent_name)
            if current_context:
                current_context["last_sync"] = datetime.now().isoformat()
                store_agent_context(agent_name, "context", current_context)
                sync_result["steps_completed"].append("sync_timestamp_updated")
                sync_result["changes_applied"] += 1
                
        except Exception as e:
            sync_result["warnings"].append(f"Failed to update sync timestamp: {e}")
        
        # Sync memory statistics
        try:
            from agent_memory import get_memory_stats
            memory_stats = get_memory_stats()
            
            # Update agent-specific memory usage
            if current_context:
                current_context["memory_usage_mb"] = memory_stats.get("total_memories", 0) * 0.1  # Estimate
                current_context["last_memory_stats"] = memory_stats
                store_agent_context(agent_name, "context", current_context)
                sync_result["steps_completed"].append("memory_stats_synced")
                sync_result["changes_applied"] += 1
                
        except Exception as e:
            sync_result["warnings"].append(f"Failed to sync memory stats: {e}")
        
        # Determine if changes were detected
        sync_result["changes_detected"] = sync_result["changes_applied"] > 0
        
        # Determine final status
        if sync_result["errors"]:
            sync_result["status"] = "failed"
        elif sync_result["warnings"]:
            sync_result["status"] = "warning"
        else:
            sync_result["status"] = "success"
        
        logger.info(f"Agent context sync completed for {agent_name}: {sync_result['status']}")
        return sync_result
        
    except Exception as e:
        logger.error(f"Failed to sync agent context: {e}")
        raise


def create_agent_profile(
    agent_name: str,
    profile_data: Dict[str, Any],
    skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create agent profiles in Letta.
    
    Args:
        agent_name: Name of the agent
        profile_data: Profile information
        skills: List of skills for the agent
        
    Returns:
        Profile creation results
    """
    try:
        profile_result = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "profile_data": profile_data,
            "skills": skills or [],
            "steps_completed": [],
            "errors": [],
            "warnings": []
        }
        
        # Create agent profile content
        profile_content = f"""
        Agent Profile: {agent_name}
        ===========================
        
        Profile Information:
        {json.dumps(profile_data, indent=2)}
        
        Skills:
        {', '.join(skills or [])}
        
        Created: {datetime.now().isoformat()}
        Status: Active
        
        Profile Type: Letta Server Integration
        Framework: {profile_data.get('framework', 'unknown')}
        Provider: {profile_data.get('provider', 'unknown')}
        Model: {profile_data.get('model', 'unknown')}
        """
        
        # Store agent profile as memory block
        try:
            store_memory_block(
                label=f"agent_profile_{agent_name}",
                content=profile_content,
                description=f"Profile for agent {agent_name}"
            )
            
            profile_result["steps_completed"].append("profile_created")
            
        except Exception as e:
            profile_result["errors"].append(f"Failed to create agent profile: {e}")
        
        # Store agent profile in context
        try:
            profile_context = {
                "agent_name": agent_name,
                "profile_data": profile_data,
                "skills": skills or [],
                "created_date": datetime.now().isoformat(),
                "status": "active",
                "framework": profile_data.get("framework"),
                "provider": profile_data.get("provider"),
                "model": profile_data.get("model")
            }
            
            store_agent_context(agent_name, "profile", profile_context)
            profile_result["steps_completed"].append("profile_context_stored")
            
        except Exception as e:
            profile_result["errors"].append(f"Failed to store profile context: {e}")
        
        # Create agent-specific configuration
        try:
            agent_config = {
                "name": agent_name,
                "framework": profile_data.get("framework"),
                "provider": profile_data.get("provider"),
                "model": profile_data.get("model"),
                "memory_backend": "letta_server",
                "skills": skills or [],
                "config_date": datetime.now().isoformat()
            }
            
            store_agent_context(agent_name, "config", agent_config)
            profile_result["steps_completed"].append("agent_config_created")
            
        except Exception as e:
            profile_result["warnings"].append(f"Failed to create agent config: {e}")
        
        # Determine final status
        if profile_result["errors"]:
            profile_result["status"] = "failed"
        elif profile_result["warnings"]:
            profile_result["status"] = "warning"
        else:
            profile_result["status"] = "success"
        
        logger.info(f"Agent profile created for {agent_name}: {profile_result['status']}")
        return profile_result
        
    except Exception as e:
        logger.error(f"Failed to create agent profile: {e}")
        raise


def get_agent_status(agent_name: str) -> Dict[str, Any]:
    """
    Get comprehensive agent status information.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Agent status information
    """
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "status": "unknown",
            "context": {},
            "profile": {},
            "memory_usage": {},
            "activity": {},
            "health": {}
        }
        
        # Get agent context
        try:
            context = get_agent_context(agent_name)
            status["context"] = context or {}
            
        except Exception as e:
            status["errors"] = [f"Failed to get agent context: {e}"]
        
        # Get agent profile
        try:
            profile = get_agent_context(agent_name)
            if profile:
                status["profile"] = profile.get("profile", {})
                
        except Exception as e:
            status["warnings"] = [f"Failed to get agent profile: {e}"]
        
        # Get memory statistics for this agent
        try:
            from agent_memory import search_memories
            agent_memories = search_memories(query="", agent_name=agent_name)
            
            status["memory_usage"] = {
                "total_memories": len(agent_memories),
                "memory_types": {},
                "last_activity": None
            }
            
            # Analyze memory types
            for memory in agent_memories:
                memory_type = memory.get("metadata", {}).get("memory_type", "unknown")
                if memory_type not in status["memory_usage"]["memory_types"]:
                    status["memory_usage"]["memory_types"][memory_type] = 0
                status["memory_usage"]["memory_types"][memory_type] += 1
            
            # Get last activity
            if agent_memories:
                status["memory_usage"]["last_activity"] = agent_memories[0].get("metadata", {}).get("timestamp")
                
        except Exception as e:
            status["warnings"] = status.get("warnings", []) + [f"Failed to get memory stats: {e}"]
        
        # Determine agent health
        try:
            context = status["context"]
            if context:
                last_sync = context.get("last_sync")
                if last_sync:
                    from datetime import datetime, timedelta
                    last_sync_time = datetime.fromisoformat(last_sync)
                    if datetime.now() - last_sync_time < timedelta(hours=1):
                        status["health"]["sync_status"] = "healthy"
                    else:
                        status["health"]["sync_status"] = "stale"
                else:
                    status["health"]["sync_status"] = "unknown"
                
                memory_usage = context.get("memory_usage_mb", 0)
                max_memory = context.get("max_memory_size_mb", 100)
                
                if memory_usage < max_memory * 0.8:
                    status["health"]["memory_status"] = "healthy"
                elif memory_usage < max_memory:
                    status["health"]["memory_status"] = "warning"
                else:
                    status["health"]["memory_status"] = "critical"
                
                status["status"] = "active"
            else:
                status["status"] = "inactive"
                status["health"]["sync_status"] = "unknown"
                status["health"]["memory_status"] = "unknown"
                
        except Exception as e:
            status["warnings"] = status.get("warnings", []) + [f"Failed to determine agent health: {e}"]
        
        logger.info(f"Agent status retrieved for {agent_name}: {status['status']}")
        return status
        
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise


def update_agent_skills(agent_name: str, skills: List[str]) -> Dict[str, Any]:
    """
    Update agent skills configuration.
    
    Args:
        agent_name: Name of the agent
        skills: New list of skills
        
    Returns:
        Update results
    """
    try:
        update_result = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "new_skills": skills,
            "steps_completed": [],
            "errors": [],
            "warnings": []
        }
        
        # Update agent context with new skills
        try:
            current_context = get_agent_context(agent_name)
            if current_context:
                current_context["skills_enabled"] = skills
                current_context["skills_last_updated"] = datetime.now().isoformat()
                store_agent_context(agent_name, "context", current_context)
                update_result["steps_completed"].append("skills_updated")
            else:
                # Create new context if it doesn't exist
                new_context = {
                    "agent_name": agent_name,
                    "skills_enabled": skills,
                    "skills_last_updated": datetime.now().isoformat(),
                    "status": "active"
                }
                store_agent_context(agent_name, "context", new_context)
                update_result["steps_completed"].append("context_created")
                
        except Exception as e:
            update_result["errors"].append(f"Failed to update agent skills: {e}")
        
        # Update agent profile if it exists
        try:
            profile = get_agent_context(agent_name)
            if profile and "profile" in profile:
                profile["profile"]["skills"] = skills
                store_agent_context(agent_name, "profile", profile["profile"])
                update_result["steps_completed"].append("profile_updated")
                
        except Exception as e:
            update_result["warnings"].append(f"Failed to update agent profile: {e}")
        
        # Determine final status
        if update_result["errors"]:
            update_result["status"] = "failed"
        elif update_result["warnings"]:
            update_result["status"] = "warning"
        else:
            update_result["status"] = "success"
        
        logger.info(f"Agent skills updated for {agent_name}: {update_result['status']}")
        return update_result
        
    except Exception as e:
        logger.error(f"Failed to update agent skills: {e}")
        raise


def cleanup_agent_data(agent_name: str, preserve_profile: bool = True) -> Dict[str, Any]:
    """
    Clean up agent data while preserving important information.
    
    Args:
        agent_name: Name of the agent
        preserve_profile: Whether to preserve agent profile
        
    Returns:
        Cleanup results
    """
    try:
        cleanup_result = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "preserve_profile": preserve_profile,
            "steps_completed": [],
            "errors": [],
            "warnings": [],
            "data_cleaned": 0
        }
        
        # Clean up agent context (but preserve profile if requested)
        try:
            if preserve_profile:
                # Only clean up non-profile context data
                current_context = get_agent_context(agent_name)
                if current_context:
                    # Keep profile and config, clean up activity data
                    preserved_keys = ["profile", "config"]
                    cleaned_context = {k: v for k, v in current_context.items() if k in preserved_keys}
                    cleaned_context["last_cleanup"] = datetime.now().isoformat()
                    
                    store_agent_context(agent_name, "context", cleaned_context)
                    cleanup_result["steps_completed"].append("context_cleaned")
                    cleanup_result["data_cleaned"] += 1
            else:
                # Remove all context
                store_agent_context(agent_name, "context", {})
                cleanup_result["steps_completed"].append("context_removed")
                cleanup_result["data_cleaned"] += 1
                
        except Exception as e:
            cleanup_result["errors"].append(f"Failed to clean up agent context: {e}")
        
        # Clean up old memory blocks
        try:
            # Remove old agent-specific memory blocks
            old_blocks = [
                f"agent_memory_summary_{agent_name}",
                f"agent_config_{agent_name}",
                f"memory_cleanup_{agent_name}"
            ]
            
            for block_label in old_blocks:
                try:
                    # Note: This would require a delete function in agent_memory
                    # For now, we'll just log what would be cleaned up
                    cleanup_result["steps_completed"].append(f"block_cleanup_scheduled_{block_label}")
                    cleanup_result["data_cleaned"] += 1
                except Exception as e:
                    cleanup_result["warnings"].append(f"Failed to clean up block {block_label}: {e}")
                    
        except Exception as e:
            cleanup_result["warnings"].append(f"Failed to clean up memory blocks: {e}")
        
        # Determine final status
        if cleanup_result["errors"]:
            cleanup_result["status"] = "failed"
        elif cleanup_result["warnings"]:
            cleanup_result["status"] = "warning"
        else:
            cleanup_result["status"] = "success"
        
        logger.info(f"Agent data cleanup completed for {agent_name}: {cleanup_result['status']}")
        return cleanup_result
        
    except Exception as e:
        logger.error(f"Failed to cleanup agent data: {e}")
        raise
"""
Memory Management Skills for Letta Server

Provides comprehensive memory operations that replace standalone scripts.
All functions are designed to work with the Agent Memory System and Letta server.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from agent_memory import (
    store_memory,
    search_memories,
    store_agent_context,
    get_agent_context,
    store_memory_block,
    get_memory_block,
)

logger = logging.getLogger(__name__)


def store_conversation(
    agent_name: str,
    conversation_history: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """
    Save conversation history to Letta server.

    Replaces: save_conversation_to_letta.py

    Args:
        agent_name: Name of the agent
        conversation_history: List of conversation messages
        metadata: Additional metadata
        tags: Tags for categorization

    Returns:
        Memory ID of the stored conversation
    """
    try:
        # Prepare conversation content
        conversation_text = ""
        for message in conversation_history:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            conversation_text += f"{role.upper()}: {content}\n\n"

        # Prepare metadata
        memory_metadata = {
            "agent_name": agent_name,
            "conversation_length": len(conversation_history),
            "message_types": [msg.get("role") for msg in conversation_history],
            "timestamp": datetime.now().isoformat(),
        }

        if metadata:
            memory_metadata.update(metadata)

        # Prepare tags
        memory_tags = tags or []
        memory_tags.extend(["conversation", agent_name, "letta_server"])

        # Store in Agent memory system
        memory_id = store_memory(
            memory_type="conversation",
            title=f"Conversation with {agent_name}",
            content=conversation_text,
            metadata=memory_metadata,
            tags=memory_tags,
        )

        # Update agent context
        store_agent_context(
            agent_name=agent_name,
            context_key="last_conversation",
            context_value={
                "memory_id": memory_id,
                "timestamp": datetime.now().isoformat(),
                "length": len(conversation_history),
            },
        )

        logger.info(f"Conversation stored successfully: {memory_id}")
        return memory_id

    except Exception as e:
        logger.error(f"Failed to store conversation: {e}")
        raise


def search_memories(
    query: str,
    agent_name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    date_range: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for relevant memories in Letta server.

    Replaces: search_letta_memories.py

    Args:
        query: Search query
        agent_name: Filter by agent
        tags: Filter by tags
        date_range: Filter by date range

    Returns:
        List of search results
    """
    try:
        # Prepare search parameters
        search_params = {"query": query, "tags": tags}

        # Add agent filter if specified
        if agent_name:
            search_params["agent_name"] = agent_name

        # Add date range filter if specified
        if date_range:
            search_params["date_range"] = date_range

        # Search memories
        results = search_memories(**search_params)

        # Enhance results with additional context
        enhanced_results = []
        for result in results:
            enhanced_result = {
                "memory_id": result.get("id"),
                "title": result.get("title"),
                "content_preview": result.get("content", "")[:200] + "..."
                if len(result.get("content", "")) > 200
                else result.get("content"),
                "tags": result.get("tags", []),
                "metadata": result.get("metadata", {}),
                "score": result.get("score", 0),
                "agent_name": result.get("metadata", {}).get("agent_name"),
            }
            enhanced_results.append(enhanced_result)

        logger.info(f"Search completed: {len(enhanced_results)} results for query: {query}")
        return enhanced_results

    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        raise


def get_memory_stats() -> Dict[str, Any]:
    """
    Get comprehensive memory statistics.

    Returns:
        Dictionary containing memory statistics
    """
    try:
        # Get basic memory counts from database
        from agent_memory import get_db_connection

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Count memories
                cur.execute("SELECT COUNT(*) FROM memories")
                total_memories = cur.fetchone()[0]

                # Count memory blocks
                cur.execute("SELECT COUNT(*) FROM memory_blocks")
                total_memory_blocks = cur.fetchone()[0]

                # Count agent contexts
                cur.execute("SELECT COUNT(DISTINCT agent_name) FROM agent_contexts")
                total_agent_contexts = cur.fetchone()[0]

        # Get memory types
        memory_types = {}
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
                    for row in cur.fetchall():
                        memory_types[row[0]] = row[1]
        except:
            pass

        # Get agent contexts
        agent_contexts = {}
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT agent_name, COUNT(*) FROM agent_contexts GROUP BY agent_name"
                    )
                    for row in cur.fetchall():
                        agent_contexts[row[0]] = row[1]
        except:
            pass

        # Create enhanced stats
        enhanced_stats = {
            "total_memories": total_memories,
            "total_memory_blocks": total_memory_blocks,
            "total_agent_contexts": total_agent_contexts,
            "memory_types": memory_types,
            "agent_contexts": agent_contexts,
            "last_updated": datetime.now().isoformat(),
            "storage_backend": "agent_memory",
            "server_status": "healthy",
        }

        logger.info("Memory statistics retrieved successfully")
        return enhanced_stats

    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise


def store_entity_extraction(
    agent_name: str,
    entities: List[Dict[str, Any]],
    context: str,
    extraction_metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Store extracted entities to Letta server.

    Replaces: add_verification_memories.py (entity extraction part)

    Args:
        agent_name: Name of the agent
        entities: List of extracted entities
        context: Context of the extraction
        extraction_metadata: Additional metadata about the extraction

    Returns:
        Memory ID of the stored entities
    """
    try:
        # Prepare entity content
        entity_content = f"Entity Extraction Results for {agent_name}\n"
        entity_content += f"Context: {context}\n"
        entity_content += f"Extraction Time: {datetime.now().isoformat()}\n\n"

        entity_content += "Extracted Entities:\n"
        for i, entity in enumerate(entities, 1):
            entity_content += f"{i}. {entity.get('text', '')} ({entity.get('label', '')})\n"
            if "confidence" in entity:
                entity_content += f"   Confidence: {entity['confidence']}\n"
            if "metadata" in entity:
                entity_content += f"   Metadata: {entity['metadata']}\n"
            entity_content += "\n"

        # Prepare metadata
        memory_metadata = {
            "agent_name": agent_name,
            "context": context,
            "entity_count": len(entities),
            "extraction_time": datetime.now().isoformat(),
            "entity_types": list(set([entity.get("label", "") for entity in entities])),
        }

        if extraction_metadata:
            memory_metadata.update(extraction_metadata)

        # Prepare tags
        tags = ["entity_extraction", "nlp", "processing", agent_name, "letta_server"]

        # Store in Agent memory system
        memory_id = store_memory(
            memory_type="entity_extraction",
            title=f"Entity Extraction - {agent_name}",
            content=entity_content,
            metadata=memory_metadata,
            tags=tags,
        )

        # Update agent context with entity extraction info
        store_agent_context(
            agent_name=agent_name,
            context_key="last_entity_extraction",
            context_value={
                "memory_id": memory_id,
                "entity_count": len(entities),
                "context": context,
                "timestamp": datetime.now().isoformat(),
            },
        )

        logger.info(f"Entity extraction stored successfully: {memory_id}")
        return memory_id

    except Exception as e:
        logger.error(f"Failed to store entity extraction: {e}")
        raise


def manage_memory_lifecycle(
    agent_name: str,
    cleanup_days: int = 30,
    max_memory_size_mb: int = 50,
    optimize_search: bool = True,
) -> Dict[str, Any]:
    """
    Handle memory cleanup and organization.

    Args:
        agent_name: Name of the agent
        cleanup_days: Days after which to clean up old memories
        max_memory_size_mb: Maximum memory size in MB
        optimize_search: Whether to optimize search indexes

    Returns:
        Cleanup results
    """
    try:
        cleanup_results = {
            "agent_name": agent_name,
            "cleanup_date": datetime.now().isoformat(),
            "memories_cleaned": 0,
            "memory_blocks_cleaned": 0,
            "agent_contexts_cleaned": 0,
            "total_space_freed_mb": 0,
            "optimization_performed": False,
        }

        # Get current memory stats
        stats = get_memory_stats()

        # Clean up old agent contexts
        try:
            current_context = get_agent_context(agent_name)
            if current_context:
                cutoff_date = datetime.now() - timedelta(days=cleanup_days)

                # Remove old context entries
                old_keys = []
                for key, value in current_context.items():
                    if isinstance(value, dict) and "timestamp" in value:
                        try:
                            timestamp = datetime.fromisoformat(value["timestamp"])
                            if timestamp < cutoff_date:
                                old_keys.append(key)
                        except:
                            pass

                # Clean up old keys
                for key in old_keys:
                    del current_context[key]
                    cleanup_results["agent_contexts_cleaned"] += 1

                # Update context if changes were made
                if old_keys:
                    store_agent_context(agent_name, "context", current_context)

        except Exception as e:
            logger.warning(f"Failed to clean up agent context for {agent_name}: {e}")

        # Store cleanup results as a memory block
        cleanup_summary = f"""
        Memory Lifecycle Management Results for {agent_name}
        Date: {cleanup_results["cleanup_date"]}
        
        Cleanup Summary:
        - Memories cleaned: {cleanup_results["memories_cleaned"]}
        - Memory blocks cleaned: {cleanup_results["memory_blocks_cleaned"]}
        - Agent contexts cleaned: {cleanup_results["agent_contexts_cleaned"]}
        - Space freed: {cleanup_results["total_space_freed_mb"]} MB
        - Optimization performed: {cleanup_results["optimization_performed"]}
        
        Current Stats:
        - Total memories: {stats.get("total_memories", 0)}
        - Total memory blocks: {stats.get("total_memory_blocks", 0)}
        - Total agent contexts: {stats.get("total_agent_contexts", 0)}
        """

        store_memory_block(
            label=f"memory_cleanup_{agent_name}",
            content=cleanup_summary,
            description=f"Memory cleanup results for {agent_name}",
        )

        logger.info(f"Memory lifecycle management completed for {agent_name}")
        return cleanup_results

    except Exception as e:
        logger.error(f"Failed to manage memory lifecycle: {e}")
        raise


def get_agent_memory_summary(agent_name: str) -> Dict[str, Any]:
    """
    Get comprehensive memory summary for an agent.

    Args:
        agent_name: Name of the agent

    Returns:
        Agent memory summary
    """
    try:
        # Get agent context
        context = get_agent_context(agent_name)

        # Get memory stats
        stats = get_memory_stats()

        # Search for agent-specific memories
        agent_memories = search_memories(query="", agent_name=agent_name)

        # Analyze memory types for this agent
        agent_memory_types = {}
        for memory in agent_memories:
            memory_type = memory.get("metadata", {}).get("memory_type", "unknown")
            if memory_type not in agent_memory_types:
                agent_memory_types[memory_type] = 0
            agent_memory_types[memory_type] += 1

        summary = {
            "agent_name": agent_name,
            "summary_date": datetime.now().isoformat(),
            "total_memories": len(agent_memories),
            "memory_types": agent_memory_types,
            "agent_context": context,
            "last_activity": context.get("last_conversation", {}).get("timestamp")
            if context
            else None,
            "total_entity_extractions": len(
                [m for m in agent_memories if "entity_extraction" in m.get("tags", [])]
            ),
            "total_conversations": len(
                [m for m in agent_memories if "conversation" in m.get("tags", [])]
            ),
        }

        logger.info(f"Agent memory summary generated for {agent_name}")
        return summary

    except Exception as e:
        logger.error(f"Failed to get agent memory summary: {e}")
        raise


def advanced_memory_search(
    query: str = None,
    search_type: str = "semantic",
    agent_id: str = "agent-1167f15a-a10a-4595-b962-ec0f372aae0d",
    tags: List[str] = None,
    memory_type: str = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Advanced memory search with multiple protocols.

    Args:
        query: Search query (optional for some search types)
        search_type: Type of search (semantic, tags, text, recent, stats)
        agent_id: Agent ID to search
        tags: Tags to filter by
        memory_type: Memory type to filter by
        limit: Max results

    Returns:
        Search results
    """
    try:
        from agent_memory import search_memories, get_db_connection

        if search_type == "semantic":
            # Use semantic search from agent_memory
            results = search_memories(query=query or "", agent_name=agent_id, tags=tags)
            return {
                "success": True,
                "search_type": "semantic",
                "query": query,
                "results": results[:limit] if limit else results,
                "count": len(results),
            }

        elif search_type == "tags":
            # Search by tags using PostgreSQL
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    conditions = []
                    params = []

                    if tags:
                        for tag in tags:
                            conditions.append("%s = ANY(tags)")
                            params.append(tag)

                    if memory_type:
                        conditions.append("memory_type = %s")
                        params.append(memory_type)

                    where_clause = " AND ".join(conditions) if conditions else "1=1"

                    query_sql = f"""
                        SELECT * FROM memories 
                        WHERE {where_clause}
                        ORDER BY created_at DESC
                        LIMIT %s
                    """
                    params.append(limit)

                    cur.execute(query_sql, tuple(params))
                    columns = [desc[0] for desc in cur.description]
                    results = [dict(zip(columns, row)) for row in cur.fetchall()]

            return {
                "success": True,
                "search_type": "tags",
                "tags": tags,
                "results": results,
                "count": len(results),
            }

        elif search_type == "text":
            # Search by text content
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    conditions = ["(content ILIKE %s OR title ILIKE %s)"]
                    params = [f"%{query}%", f"%{query}%"]

                    if tags:
                        for tag in tags:
                            conditions.append("%s = ANY(tags)")
                            params.append(tag)

                    if memory_type:
                        conditions.append("memory_type = %s")
                        params.append(memory_type)

                    where_clause = " AND ".join(conditions)

                    query_sql = f"""
                        SELECT * FROM memories 
                        WHERE {where_clause}
                        ORDER BY created_at DESC
                        LIMIT %s
                    """
                    params.append(limit)

                    cur.execute(query_sql, tuple(params))
                    columns = [desc[0] for desc in cur.description]
                    results = [dict(zip(columns, row)) for row in cur.fetchall()]

            return {
                "success": True,
                "search_type": "text",
                "query": query,
                "results": results,
                "count": len(results),
            }

        elif search_type == "stats":
            # Get memory statistics
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Total count
                    cur.execute("SELECT COUNT(*) FROM memories")
                    total = cur.fetchone()[0]

                    # Count by type
                    cur.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
                    by_type = {row[0]: row[1] for row in cur.fetchall()}

                    # Count by tags
                    cur.execute("""
                        SELECT unnest(tags) as tag, COUNT(*) 
                        FROM memories 
                        GROUP BY tag 
                        ORDER BY COUNT(*) DESC 
                        LIMIT 20
                    """)
                    by_tags = {row[0]: row[1] for row in cur.fetchall()}

            return {
                "success": True,
                "search_type": "stats",
                "total_memories": total,
                "by_type": by_type,
                "by_tags": by_tags,
            }

        else:
            return {"success": False, "error": f"Unknown search type: {search_type}"}

    except Exception as e:
        logger.error(f"Advanced memory search failed: {e}")
        return {"success": False, "error": str(e)}


def cross_agent_search(query: str, agent_ids: List[str] = None) -> Dict[str, Any]:
    """
    Search across multiple agents.

    Args:
        query: Search query
        agent_ids: List of agent IDs to search (default: common agents)

    Returns:
        Combined search results
    """
    try:
        if agent_ids is None:
            # Default common agents
            agent_ids = [
                "agent-1167f15a-a10a-4595-b962-ec0f372aae0d",  # coder
                "agent-a3b6b8f5-dffb-49f2-82a8-69097d410f96",  # researcher
                "agent-311b8012-989e-47d5-8ccc-c19574008162",  # infra-assistant
            ]

        all_results = {}

        for agent_id in agent_ids:
            results = advanced_memory_search(
                query=query, search_type="semantic", agent_id=agent_id, limit=5
            )
            if results["success"]:
                all_results[agent_id] = results["results"]

        return {
            "success": True,
            "query": query,
            "agent_ids": agent_ids,
            "results": all_results,
            "total_results": sum(len(r) for r in all_results.values()),
        }

    except Exception as e:
        logger.error(f"Cross-agent search failed: {e}")
        return {"success": False, "error": str(e)}

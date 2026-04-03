"""
Memory Sync Skill Implementation

Provides synchronization capabilities between PostgreSQL database and Letta server.
This skill replaces standalone sync scripts with reusable, integrated functions.
"""

import json
import hashlib
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemorySync:
    """Memory synchronization between PostgreSQL and Letta server."""

    def __init__(self):
        self.agent_ids = {
            "coder": "agent-1167f15a-a10a-4595-b962-ec0f372aae0d",
            "researcher": "agent-a3b6b8f5-dffb-49f2-82a8-69097d410f96",
            "infra-assistant": "agent-311b8012-989e-47d5-8ccc-c19574008162",
            "ops-monitor": "agent-7290d241-dbac-4dd5-b969-d601e8caac6d",
        }

    def _get_agent_id(self, agent_name: str) -> str:
        """Get agent ID from name or return if already an ID."""
        if agent_name.startswith("agent-"):
            return agent_name
        return self.agent_ids.get(agent_name, self.agent_ids["coder"])

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash of content for deduplication."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def sync_postgres_to_letta(
        self,
        agent_id: str,
        memory_types: List[str] = None,
        limit: int = 100,
        dry_run: bool = False,
        incremental: bool = False,
        last_sync_timestamp: str = None,
    ) -> Dict[str, Any]:
        """
        Sync memories from PostgreSQL to Letta server.

        Args:
            agent_id: Target agent ID in Letta
            memory_types: Memory types to sync (default: all)
            limit: Max memories to sync
            dry_run: Preview sync without executing
            incremental: Sync only new/updated memories
            last_sync_timestamp: Timestamp for incremental sync

        Returns:
            Sync results
        """
        try:
            from cli_operations import run_sql_query, store_letta_memory

            # Build query conditions
            conditions = []
            params = []

            if memory_types:
                type_conditions = []
                for mem_type in memory_types:
                    type_conditions.append("memory_type = %s")
                    params.append(mem_type)
                conditions.append(f"({' OR '.join(type_conditions)})")

            if incremental and last_sync_timestamp:
                conditions.append("created_at > %s")
                params.append(last_sync_timestamp)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Fetch memories from PostgreSQL
            query = f"""
                SELECT * FROM letta_memories 
                WHERE {where_clause}
                ORDER BY created_at DESC 
                LIMIT %s
            """
            params.append(limit)

            result = run_sql_query(query, tuple(params))

            if not result["success"]:
                return result

            memories = result["data"]

            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "memories_found": len(memories),
                    "memories": memories[:10],  # Preview first 10
                    "message": f"Would sync {len(memories)} memories",
                }

            # Sync each memory to Letta
            sync_results = []
            for memory in memories:
                # Prepare content
                content = memory.get("content", "")
                title = memory.get("title", "")
                tags = memory.get("tags", [])

                # Combine title and content
                full_content = f"{title}\n\n{content}" if title else content

                # Store in Letta
                letta_result = store_letta_memory(agent_id=agent_id, text=full_content, tags=tags)

                sync_results.append(
                    {
                        "memory_id": memory.get("id"),
                        "title": title,
                        "synced": letta_result["success"],
                        "error": letta_result.get("error"),
                    }
                )

            # Calculate statistics
            successful = sum(1 for r in sync_results if r["synced"])
            failed = len(sync_results) - successful

            return {
                "success": True,
                "agent_id": agent_id,
                "total_memories": len(memories),
                "synced": successful,
                "failed": failed,
                "results": sync_results,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"success": False, "error": str(e)}

    def sync_letta_to_postgres(
        self, agent_id: str, memory_types: List[str] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Sync memories from Letta server to PostgreSQL.

        Args:
            agent_id: Source agent ID in Letta
            memory_types: Memory types to sync (default: all)
            limit: Max memories to sync

        Returns:
            Sync results
        """
        try:
            from cli_operations import search_letta_memories, run_sql_query

            # Fetch memories from Letta
            letta_result = search_letta_memories(agent_id, "", limit)

            if not letta_result["success"]:
                return letta_result

            memories = letta_result["data"]

            # Sync each memory to PostgreSQL
            sync_results = []
            for memory in memories:
                # Prepare content
                content = memory.get("text", "")
                tags = memory.get("tags", [])

                # Check if memory already exists
                check_query = """
                    SELECT id FROM letta_memories 
                    WHERE content = %s AND %s = ANY(tags)
                """
                check_result = run_sql_query(check_query, (content, agent_id), fetch=True)

                if check_result["success"] and check_result["data"]:
                    # Memory already exists
                    sync_results.append(
                        {"memory_id": memory.get("id"), "synced": False, "reason": "already_exists"}
                    )
                    continue

                # Insert into PostgreSQL
                insert_query = """
                    INSERT INTO letta_memories (memory_type, title, content, tags)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """
                insert_result = run_sql_query(
                    insert_query,
                    ("letta_import", f"Letta memory {memory.get('id')}", content, tags),
                    fetch=True,
                )

                sync_results.append(
                    {
                        "memory_id": memory.get("id"),
                        "synced": insert_result["success"],
                        "postgres_id": insert_result["data"][0]["id"]
                        if insert_result["success"]
                        else None,
                        "error": insert_result.get("error"),
                    }
                )

            # Calculate statistics
            successful = sum(1 for r in sync_results if r["synced"])
            skipped = sum(1 for r in sync_results if r.get("reason") == "already_exists")
            failed = len(sync_results) - successful - skipped

            return {
                "success": True,
                "agent_id": agent_id,
                "total_memories": len(memories),
                "synced": successful,
                "skipped": skipped,
                "failed": failed,
                "results": sync_results,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"success": False, "error": str(e)}

    def backup_agent_data(self, agent_id: str, backup_name: str = None) -> Dict[str, Any]:
        """
        Backup Letta agent data to PostgreSQL.

        Args:
            agent_id: Agent ID to backup
            backup_name: Backup name (default: timestamp-based)

        Returns:
            Backup results
        """
        try:
            from cli_operations import run_sql_query, run_letta_command

            # Get agent data from Letta
            letta_result = run_letta_command(["agent", agent_id])

            if not letta_result["success"]:
                return letta_result

            agent_data = letta_result["data"]

            # Create backup name if not provided
            if not backup_name:
                backup_name = f"backup_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Store backup in PostgreSQL
            query = """
                INSERT INTO agent_backups (agent_id, backup_name, backup_data, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """

            result = run_sql_query(
                query, (agent_id, backup_name, json.dumps(agent_data), datetime.now()), fetch=True
            )

            if result["success"]:
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "backup_name": backup_name,
                    "backup_id": result["data"][0]["id"],
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {"success": False, "error": str(e)}

    def deduplicate_memories(
        self, agent_id: str = None, memory_type: str = None, strategy: str = "content"
    ) -> Dict[str, Any]:
        """
        Remove duplicate memories across storage backends.

        Args:
            agent_id: Filter by agent
            memory_type: Filter by memory type
            strategy: Deduplication strategy (hash, content, semantic)

        Returns:
            Deduplication results
        """
        try:
            from cli_operations import run_sql_query

            # Build query conditions
            conditions = []
            params = []

            if agent_id:
                conditions.append("tags @> %s")
                params.append([agent_id])

            if memory_type:
                conditions.append("memory_type = %s")
                params.append(memory_type)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Fetch memories to deduplicate
            query = f"""
                SELECT id, content, title, created_at
                FROM letta_memories 
                WHERE {where_clause}
                ORDER BY created_at DESC
            """

            result = run_sql_query(query, tuple(params))

            if not result["success"]:
                return result

            memories = result["data"]

            # Find duplicates based on strategy
            duplicates = []
            seen_hashes = {}

            for memory in memories:
                content = memory.get("content", "")

                if strategy == "hash":
                    content_hash = self._calculate_content_hash(content)

                    if content_hash in seen_hashes:
                        # Found duplicate
                        duplicates.append(
                            {
                                "duplicate_id": memory.get("id"),
                                "original_id": seen_hashes[content_hash],
                                "reason": "content_hash_match",
                            }
                        )
                    else:
                        seen_hashes[content_hash] = memory.get("id")

            # Remove duplicates
            removed_count = 0
            for dup in duplicates:
                delete_query = "DELETE FROM letta_memories WHERE id = %s"
                delete_result = run_sql_query(delete_query, (dup["duplicate_id"],), fetch=False)

                if delete_result["success"]:
                    removed_count += 1
                    dup["removed"] = True
                else:
                    dup["removed"] = False
                    dup["error"] = delete_result.get("error")

            return {
                "success": True,
                "total_memories": len(memories),
                "duplicates_found": len(duplicates),
                "duplicates_removed": removed_count,
                "duplicates": duplicates,
                "strategy": strategy,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Deduplication failed: {e}")
            return {"success": False, "error": str(e)}


# Create a global instance
memory_sync = MemorySync()


# Export functions for use in skills
def sync_postgres_to_letta(
    agent_id: str, memory_types: List[str] = None, limit: int = 100, dry_run: bool = False
) -> Dict[str, Any]:
    """Sync memories from PostgreSQL to Letta server."""
    return memory_sync.sync_postgres_to_letta(agent_id, memory_types, limit, dry_run)


def sync_letta_to_postgres(
    agent_id: str, memory_types: List[str] = None, limit: int = 100
) -> Dict[str, Any]:
    """Sync memories from Letta server to PostgreSQL."""
    return memory_sync.sync_letta_to_postgres(agent_id, memory_types, limit)


def backup_agent_data(agent_id: str, backup_name: str = None) -> Dict[str, Any]:
    """Backup Letta agent data to PostgreSQL."""
    return memory_sync.backup_agent_data(agent_id, backup_name)


def deduplicate_memories(
    agent_id: str = None, memory_type: str = None, strategy: str = "content"
) -> Dict[str, Any]:
    """Remove duplicate memories across storage backends."""
    return memory_sync.deduplicate_memories(agent_id, memory_type, strategy)

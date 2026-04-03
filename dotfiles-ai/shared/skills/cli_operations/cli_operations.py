"""
CLI Operations Skill Implementation

Provides command-line interface operations for Letta server and other tools.
This skill wraps CLI commands into reusable functions for AI agents.
"""

import json
import logging
import subprocess
import sys
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class CLIOperations:
    """Command-line interface operations for Letta and other tools."""

    def __init__(self, letta_path: str = "/home/cbwinslow/bin/letta"):
        self.letta_path = letta_path

    def run_letta_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """
        Run a Letta CLI command and return the result.

        Args:
            command: List of command arguments (e.g., ["archival-search", "agent-id", "query"])
            timeout: Command timeout in seconds

        Returns:
            Dict with success status, data, and raw output
        """
        try:
            # Build the full command
            full_command = [self.letta_path] + command

            result = subprocess.run(full_command, capture_output=True, text=True, timeout=timeout)

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "command": " ".join(full_command),
                    "raw": result.stdout,
                }

            # Try to parse as JSON, otherwise return raw text
            try:
                data = json.loads(result.stdout)
                return {"success": True, "data": data, "raw": result.stdout}
            except json.JSONDecodeError:
                return {"success": True, "data": result.stdout, "raw": result.stdout}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out", "command": " ".join(command)}
        except Exception as e:
            return {"success": False, "error": str(e), "command": " ".join(command)}

    def search_letta_memories(self, agent_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search memories using Letta CLI.

        Args:
            agent_id: Agent ID to search
            query: Search query
            limit: Max results

        Returns:
            Dict with search results
        """
        command = ["archival-search", agent_id, query]
        return self.run_letta_command(command)

    def store_letta_memory(
        self, agent_id: str, text: str, tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Store a memory using Letta CLI.

        Args:
            agent_id: Agent ID to store to
            text: Memory text
            tags: Tags for categorization

        Returns:
            Dict with success status
        """
        tags_str = ",".join(tags) if tags else ""
        command = ["archival-insert", agent_id, text, tags_str]
        return self.run_letta_command(command)

    def list_letta_agents(self) -> Dict[str, Any]:
        """
        List all agents in Letta server.

        Returns:
            Dict with list of agents
        """
        command = ["agents"]
        return self.run_letta_command(command)

    def check_letta_health(self) -> Dict[str, Any]:
        """
        Check Letta server health status.

        Returns:
            Dict with health status
        """
        command = ["health"]
        return self.run_letta_command(command)

    def backup_letta_agent(self, agent_id: str, output_file: str) -> Dict[str, Any]:
        """
        Backup an agent's data to JSON file.

        Args:
            agent_id: Agent ID to backup
            output_file: Output file path

        Returns:
            Dict with success status
        """
        try:
            # First get the agent data
            result = self.run_letta_command(["agent", agent_id])

            if not result["success"]:
                return result

            # Write to file
            with open(output_file, "w") as f:
                json.dump(result["data"], f, indent=2)

            return {
                "success": True,
                "message": f"Agent backup saved to {output_file}",
                "agent_id": agent_id,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_sql_query(
        self,
        query: str,
        params: tuple = None,
        fetch: bool = True,
        database: str = "letta",
        host: str = "localhost",
        port: int = 5432,
        user: str = "cbwinslow",
        password: str = "123qweasd",
    ) -> Dict[str, Any]:
        """
        Run a SQL query against PostgreSQL database.

        Args:
            query: SQL query to execute
            params: Query parameters
            fetch: Whether to fetch results
            database: Database name
            host: Database host
            port: Database port
            user: Database user
            password: Database password

        Returns:
            Query results or success status
        """
        try:
            conn = psycopg2.connect(
                host=host, port=port, database=database, user=user, password=password
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)

                if fetch and cur.description:  # Has results
                    results = cur.fetchall()
                    conn.close()
                    return {
                        "success": True,
                        "data": [dict(row) for row in results],
                        "row_count": len(results),
                    }
                else:
                    conn.commit()
                    conn.close()
                    return {
                        "success": True,
                        "message": "Query executed successfully",
                        "rows_affected": cur.rowcount,
                    }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_postgres_memories(
        self,
        search_text: str = None,
        memory_type: str = None,
        tags: List[str] = None,
        limit: int = 50,
        database: str = "letta",
    ) -> Dict[str, Any]:
        """
        Search memories in PostgreSQL database.

        Args:
            search_text: Text to search for
            memory_type: Filter by memory type
            tags: Filter by tags
            limit: Max results
            database: Database name

        Returns:
            List of memory objects
        """
        try:
            conditions = []
            params = []

            if search_text:
                conditions.append("(content ILIKE %s OR title ILIKE %s)")
                params.extend([f"%{search_text}%", f"%{search_text}%"])

            if memory_type:
                conditions.append("memory_type = %s")
                params.append(memory_type)

            if tags:
                # Check if any of the tags match
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append("%s = ANY(tags)")
                    params.append(tag)
                conditions.append(f"({' OR '.join(tag_conditions)})")

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            query = f"""
                SELECT * FROM letta_memories 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s
            """
            params.append(limit)

            return self.run_sql_query(query, tuple(params), database=database)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_memory_stats(self, database: str = "letta") -> Dict[str, Any]:
        """
        Get memory statistics from PostgreSQL.

        Args:
            database: Database name

        Returns:
            Dict with memory statistics
        """
        try:
            # Get total count
            count_result = self.run_sql_query(
                "SELECT COUNT(*) as total FROM letta_memories", database=database
            )

            if not count_result["success"]:
                return count_result

            total = count_result["data"][0]["total"]

            # Get counts by type
            type_result = self.run_sql_query(
                """SELECT memory_type, COUNT(*) as count 
                   FROM letta_memories 
                   GROUP BY memory_type 
                   ORDER BY count DESC""",
                database=database,
            )

            # Get recent memories
            recent_result = self.run_sql_query(
                """SELECT * FROM letta_memories 
                   ORDER BY created_at DESC 
                   LIMIT 5""",
                database=database,
            )

            return {
                "success": True,
                "data": {
                    "total_memories": total,
                    "by_type": type_result["data"] if type_result["success"] else [],
                    "recent_memories": recent_result["data"] if recent_result["success"] else [],
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


# Create a global instance
cli = CLIOperations()


# Export functions for use in skills
def run_letta_command(command: List[str], timeout: int = 30) -> Dict[str, Any]:
    """Run a Letta CLI command."""
    return cli.run_letta_command(command, timeout)


def search_letta_memories(agent_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
    """Search memories using Letta CLI."""
    return cli.search_letta_memories(agent_id, query, limit)


def store_letta_memory(agent_id: str, text: str, tags: List[str] = None) -> Dict[str, Any]:
    """Store a memory using Letta CLI."""
    return cli.store_letta_memory(agent_id, text, tags)


def list_letta_agents() -> Dict[str, Any]:
    """List all agents in Letta server."""
    return cli.list_letta_agents()


def check_letta_health() -> Dict[str, Any]:
    """Check Letta server health status."""
    return cli.check_letta_health()


def run_sql_query(
    query: str, params: tuple = None, fetch: bool = True, database: str = "letta"
) -> Dict[str, Any]:
    """Run a SQL query against PostgreSQL database."""
    return cli.run_sql_query(query, params, fetch, database)


def search_postgres_memories(
    search_text: str = None, memory_type: str = None, tags: List[str] = None, limit: int = 50
) -> Dict[str, Any]:
    """Search memories in PostgreSQL database."""
    return cli.search_postgres_memories(search_text, memory_type, tags, limit)


def get_memory_stats() -> Dict[str, Any]:
    """Get memory statistics from PostgreSQL."""
    return cli.get_memory_stats()

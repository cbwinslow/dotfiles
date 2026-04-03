import os
import subprocess
from typing import Any, Dict, List, Optional

LETTA_URL = os.getenv("LETTA_URL", "http://localhost:8283")
LETTA_SERVER_PASSWORD = os.getenv("LETTA_SERVER_PASSWORD", "123qweasd")

def _run_letta_command(command: str, *args: str) -> Dict[str, Any]:
    """Run a Letta CLI command and return the parsed JSON response."""
    try:
        full_command = ["letta", command] + list(args)
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True
        )
        return {"success": True, "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr.strip() if e.stderr else str(e)}

def store_agent_context(agent_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Store agent context in Letta."""
    try:
        # Convert context to string representation
        context_str = str(context)
        result = _run_letta_command("memory-update", agent_id, "agent-context", context_str)
        if result["success"]:
            return {"success": True, "message": "Agent context stored successfully"}
        return {"success": False, "error": result["error"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def store_memory_block(label: str, value: str) -> Dict[str, Any]:
    """Store reusable memory block."""
    try:
        result = _run_letta_command("block", "create", label, value)
        if result["success"]:
            return {"success": True, "message": "Memory block created successfully"}
        return {"success": False, "error": result["error"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def archival_insert(agent_id: str, text: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Store archival memory."""
    try:
        tag_str = ",".join(tags) if tags else ""
        result = _run_letta_command("archival-insert", agent_id, text, tag_str)
        if result["success"]:
            return {"success": True, "message": "Archival memory stored successfully"}
        return {"success": False, "error": result["error"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def archival_search(agent_id: str, query: str) -> Dict[str, Any]:
    """Search archival memories."""
    try:
        result = _run_letta_command("archival-search", agent_id, query)
        if result["success"]:
            return {"success": True, "results": result["output"]}
        return {"success": False, "error": result["error"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_agent_memory(agent_id: str) -> Dict[str, Any]:
    """Get agent memory blocks."""
    try:
        result = _run_letta_command("memory", agent_id)
        if result["success"]:
            return {"success": True, "memory": result["output"]}
        return {"success": False, "error": result["error"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_memory_blocks() -> Dict[str, Any]:
    """List all memory blocks."""
    try:
        result = _run_letta_command("block", "list")
        if result["success"]:
            return {"success": True, "blocks": result["output"]}
        return {"success": False, "error": result["error"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_agents() -> Dict[str, Any]:
    """List all agents."""
    try:
        result = _run_letta_command("agents")
        if result["success"]:
            return {"success": True, "agents": result["output"]}
        return {"success": False, "error": result["error"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

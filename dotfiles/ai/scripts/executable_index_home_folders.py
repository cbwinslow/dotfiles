#!/usr/bin/env python3
"""
Comprehensive Home Folder Indexer for CBW RAG
Indexes all AI agent configs, dotfiles, .config, and workspace projects
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment
os.environ.update(os.environ)
os.environ['CBW_RAG_DATABASE'] = os.getenv('CBW_RAG_DATABASE', 'postgresql://cbwinslow:123qweasd@localhost:5432/cbw_rag')

DB_URL = os.environ['CBW_RAG_DATABASE']
INDEXER = Path.home() / "projects/ai/rag_system/cbw_indexer.py"

# AI Agent Config Folders to index
AI_AGENT_FOLDERS = [
    ".agent",
    ".cline",
    ".codeium",
    ".codex",
    ".copilot",
    ".crewai",
    ".crush",
    ".cursor",
    ".gemini",
    ".ghcp-appmod",
    ".kilocode",
    ".letta",
    ".mcp",
    ".opencode",
    ".openclaw",
    ".rest-client",
    ".sonarlint",
    ".windsurf",
    ".epstein_memory",
]

# .config subdirectories to index (exclude node_modules, cache, etc.)
CONFIG_FOLDERS = [
    "ai",
    "ai-agents",
    "bat",
    "bitwarden-ai",
    "chezmoi",
    "coderabbit",
    "configstore",
    "fish",
    "gemini",
    "gh",
    "git",
    "go",
    "kilo",
    "lvim",
    "mcp",
    "opencode",
    "openclaw",
    "shell",
    "tcd",
    "uv",
    "vscode-sqltools",
]

# Individual dotfiles to index
DOTFILES = [
    ".bashrc",
    ".bash_aliases",
    ".bash_functions",
    ".bash_profile",
    ".bash_logout",
    ".zshrc",
    ".zshenv",
    ".zshrc.local",
    ".profile",
    ".gitconfig",
    ".gitignore",
    ".tmux.conf",
    ".vimrc",
    ".inputrc",
    ".wgetrc",
    ".curlrc",
    ".psqlrc",
    ".env.ai",
]

# Workspace projects to index
WORKSPACE_FOLDERS = [
    "epstein",
    "qry.sh",
    "stem",
    "templates",
]

# Other important folders
OTHER_FOLDERS = [
    ".dbtools",
    ".docker",
    ".dotnet",
    ".gitlab",
]


def index_path(path: str, workers: int = 4) -> Dict[str, Any]:
    """Index a single path using cbw_indexer."""
    if not os.path.exists(path):
        return {"path": path, "status": "skipped", "reason": "does_not_exist"}
    
    cmd = [
        sys.executable, str(INDEXER),
        path,
        "--db", DB_URL,
        "--use-ollama",
        "--ollama-url", "http://localhost:11434",
        "--ollama-model", "nomic-embed-text",
        "--workers", str(workers),
        "--batch-size", "32",
        "--quiet"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return {"path": path, "status": "success"}
        else:
            # Check if it's a transaction error - might be from concurrent access
            if "transaction" in result.stderr.lower():
                return {"path": path, "status": "retry", "error": result.stderr[:200]}
            return {"path": path, "status": "error", "error": result.stderr[:200]}
    except subprocess.TimeoutExpired:
        return {"path": path, "status": "timeout"}
    except Exception as e:
        return {"path": path, "status": "error", "error": str(e)}


def index_all():
    """Index all configured folders."""
    home = Path.home()
    all_paths = []
    
    print("=" * 70)
    print("COMPREHENSIVE HOME FOLDER INDEXER")
    print("=" * 70)
    
    # Collect AI agent folders
    print("\n[Collecting paths...]")
    for folder in AI_AGENT_FOLDERS:
        path = home / folder
        if path.exists():
            all_paths.append(("ai-agent", folder, str(path)))
    
    # Collect .config folders
    for folder in CONFIG_FOLDERS:
        path = home / ".config" / folder
        if path.exists():
            all_paths.append(("config", folder, str(path)))
    
    # Collect dotfiles
    for dotfile in DOTFILES:
        path = home / dotfile
        if path.exists():
            all_paths.append(("dotfile", dotfile, str(path)))
    
    # Collect workspace folders
    for folder in WORKSPACE_FOLDERS:
        path = home / "workspace" / folder
        if path.exists():
            all_paths.append(("workspace", folder, str(path)))
    
    # Collect other folders
    for folder in OTHER_FOLDERS:
        path = home / folder
        if path.exists():
            all_paths.append(("other", folder, str(path)))
    
    print(f"Found {len(all_paths)} paths to index")
    
    # Index everything (serially to avoid DB conflicts)
    results = []
    success_count = 0
    error_count = 0
    
    print("\n[Indexing...]")
    for category, name, path in all_paths:
        print(f"  [{category:12}] {name:30} ...", end=" ", flush=True)
        result = index_path(path, workers=2)
        results.append(result)
        
        if result["status"] == "success":
            success_count += 1
            print("✓")
        elif result["status"] == "retry":
            # Retry once
            print("retry...", end=" ", flush=True)
            import time
            time.sleep(2)
            result = index_path(path, workers=1)
            if result["status"] == "success":
                success_count += 1
                print("✓")
            else:
                error_count += 1
                print(f"✗ ({result.get('error', 'unknown')[:50]})")
        else:
            error_count += 1
            print(f"✗ ({result.get('error', 'unknown')[:50]})")
    
    # Summary
    print("\n" + "=" * 70)
    print("INDEXING SUMMARY")
    print("=" * 70)
    print(f"  Total paths:     {len(all_paths)}")
    print(f"  Successful:      {success_count}")
    print(f"  Errors:          {error_count}")
    
    # Show errors
    if error_count > 0:
        print("\n  Errors:")
        for r in results:
            if r["status"] == "error":
                print(f"    - {r['path']}: {r.get('error', 'unknown')[:60]}")
    
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Comprehensive Home Folder Indexer")
    parser.add_argument("--list", action="store_true", help="List paths that would be indexed")
    parser.add_argument("--category", type=str, help="Index only specific category (ai-agent, config, dotfile, workspace, other)")
    args = parser.parse_args()
    
    if args.list:
        home = Path.home()
        print("Paths that would be indexed:")
        for folder in AI_AGENT_FOLDERS:
            path = home / folder
            status = "✓" if path.exists() else "✗"
            print(f"  [{status}] ai-agent: {folder}")
        for folder in CONFIG_FOLDERS:
            path = home / ".config" / folder
            status = "✓" if path.exists() else "✗"
            print(f"  [{status}] config: .config/{folder}")
        return
    
    # Run indexing
    index_all()
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()

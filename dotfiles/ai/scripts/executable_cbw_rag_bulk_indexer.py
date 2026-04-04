#!/usr/bin/env python3
"""
CBW RAG Bulk Indexer - Index all important folders
Indexes dotfiles, configs, projects with parallel processing
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Paths to index
INDEX_TARGETS = {
    # Core dotfiles repo
    "dotfiles_ai": "/home/cbwinslow/dotfiles/ai",
    "dotfiles_shell": "/home/cbwinslow/dotfiles/shell", 
    "dotfiles_git": "/home/cbwinslow/dotfiles/git",
    "dotfiles_ssh": "/home/cbwinslow/dotfiles/ssh",
    "dotfiles_editor": "/home/cbwinslow/dotfiles/editor",
    
    # Actual dotfiles (hidden configs)
    "home_config": "/home/cbwinslow/.config",
    "home_local": "/home/cbwinslow/.local",
    
    # Individual dotfiles (handled specially)
    # "bash_rc": "~/.bashrc", etc.
    
    # Projects
    "workspace_epstein": "/home/cbwinslow/workspace/epstein",
    "projects_ai": "/home/cbwinslow/projects/ai",
    "projects_apps": "/home/cbwinslow/projects/apps",
}

# Individual dotfiles to index
DOTFILES_TO_INDEX = [
    "/home/cbwinslow/.bashrc",
    "/home/cbwinslow/.bash_aliases",
    "/home/cbwinslow/.bash_functions",
    "/home/cbwinslow/.bash_secrets",
    "/home/cbwinslow/.bash_profile",
    "/home/cbwinslow/.bash_logout",
    "/home/cbwinslow/.zshrc",
    "/home/cbwinslow/.zshenv",
    "/home/cbwinslow/.zshrc.local",
    "/home/cbwinslow/.profile",
    "/home/cbwinslow/.gitconfig",
    "/home/cbwinslow/.tmux.conf",
    "/home/cbwinslow/.vimrc",
    "/home/cbwinslow/.inputrc",
    "/home/cbwinslow/.wgetrc",
    "/home/cbwinslow/.curlrc",
    "/home/cbwinslow/.psqlrc",
]

# Skip patterns
SKIP_PATTERNS = [
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "*.so",
    "*.dll",
    "*.dylib",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
    ".tox",
    ".coverage",
    "htmlcov",
    ".env",
    ".env.*",
    "*.min.js",
    "*.min.css",
    ".next",
    ".nuxt",
    "target",  # rust
    "Cargo.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
    "Gemfile.lock",
    "composer.lock",
]


def index_directory(path: str, workers: int = 4, force: bool = False) -> Dict[str, Any]:
    """Index a single directory using cbw_indexer."""
    if not os.path.exists(path):
        return {"path": path, "status": "skipped", "reason": "does_not_exist"}
    
    indexer_path = "/home/cbwinslow/projects/ai/rag_system/cbw_indexer.py"
    
    cmd = [
        sys.executable, indexer_path,
        path,
        "--workers", str(workers),
        "--batch-size", "32"
    ]
    
    if force:
        cmd.append("--force")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            # Parse stats from output
            stats = {"path": path, "status": "success", "output": result.stdout}
            return stats
        else:
            return {"path": path, "status": "error", "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"path": path, "status": "timeout"}
    except Exception as e:
        return {"path": path, "status": "error", "error": str(e)}


def index_all_targets(parallel: bool = True, max_workers: int = 3) -> List[Dict]:
    """Index all configured targets."""
    results = []
    
    print("=" * 60)
    print("CBW RAG BULK INDEXER")
    print("=" * 60)
    
    # Index directories
    print("\n[1/3] Indexing directories...")
    dirs_to_index = [(name, path) for name, path in INDEX_TARGETS.items() 
                     if os.path.exists(path)]
    
    if parallel and len(dirs_to_index) > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(index_directory, path, 4, False): (name, path) 
                for name, path in dirs_to_index
            }
            
            for future in as_completed(futures):
                name, path = futures[future]
                try:
                    result = future.result()
                    results.append({**result, "name": name})
                    status_icon = "✓" if result["status"] == "success" else "✗"
                    print(f"  {status_icon} {name}: {result['status']}")
                except Exception as e:
                    results.append({"name": name, "path": path, "status": "error", "error": str(e)})
                    print(f"  ✗ {name}: error - {e}")
    else:
        for name, path in dirs_to_index:
            print(f"  Indexing {name}...")
            result = index_directory(path, 4, False)
            results.append({**result, "name": name})
            status_icon = "✓" if result["status"] == "success" else "✗"
            print(f"  {status_icon} {name}: {result['status']}")
    
    # Index individual dotfiles
    print("\n[2/3] Indexing individual dotfiles...")
    dotfile_results = index_dotfiles(DOTFILES_TO_INDEX)
    results.extend(dotfile_results)
    print(f"  Indexed {len([r for r in dotfile_results if r['status'] == 'success'])} dotfiles")
    
    # Summary
    print("\n[3/3] Indexing Summary")
    print("-" * 40)
    success = len([r for r in results if r["status"] == "success"])
    failed = len([r for r in results if r["status"] == "error"])
    skipped = len([r for r in results if r["status"] == "skipped"])
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    
    return results


def index_dotfiles(file_list: List[str]) -> List[Dict]:
    """Index individual dotfiles as a special collection."""
    results = []
    
    # Add dotfiles to a temp directory structure for indexing
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory(prefix="dotfiles_") as tmpdir:
        dotfiles_dir = os.path.join(tmpdir, "home_dotfiles")
        os.makedirs(dotfiles_dir, exist_ok=True)
        
        for src_path in file_list:
            if os.path.exists(src_path):
                filename = os.path.basename(src_path)
                # Prefix with dot if not present to preserve identity
                if not filename.startswith("."):
                    filename = f"dot_{filename}"
                dst_path = os.path.join(dotfiles_dir, filename)
                try:
                    shutil.copy2(src_path, dst_path)
                except Exception as e:
                    results.append({"path": src_path, "status": "error", "error": str(e)})
        
        # Index the temp directory
        result = index_directory(dotfiles_dir, workers=2, force=False)
        
        # Update paths in results to reflect original locations
        for item in results:
            if item.get("status") == "success":
                item["original_path"] = item.get("path")
    
    return results


def get_index_stats() -> Dict[str, Any]:
    """Get current indexing statistics from database."""
    try:
        import psycopg2
        db_url = os.getenv("CBW_RAG_DATABASE", 
                          "postgresql://cbwinslow:123qweasd@localhost:5432/cbw_rag")
        
        conn = psycopg2.connect(db_url)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_system_stats()")
            stats = {row[0]: row[1] for row in cur.fetchall()}
            
            cur.execute("SELECT * FROM v_file_stats_by_extension LIMIT 10")
            extensions = [{"ext": r[0], "count": r[1], "size": r[2]} for r in cur.fetchall()]
            
            return {
                "system": stats,
                "top_extensions": extensions
            }
    except Exception as e:
        return {"error": str(e)}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CBW RAG Bulk Indexer")
    parser.add_argument("--force", action="store_true", help="Force reindex")
    parser.add_argument("--workers", type=int, default=3, help="Parallel workers")
    parser.add_argument("--stats", action="store_true", help="Show stats only")
    parser.add_argument("--target", type=str, help="Specific target to index")
    
    args = parser.parse_args()
    
    if args.stats:
        stats = get_index_stats()
        print("\n=== CBW RAG Database Statistics ===")
        if "system" in stats:
            for name, value in stats["system"].items():
                print(f"  {name}: {value}")
        if "top_extensions" in stats:
            print("\nTop File Types:")
            for ext in stats["top_extensions"][:5]:
                print(f"  {ext['ext']}: {ext['count']} files")
        return
    
    if args.target:
        if args.target in INDEX_TARGETS:
            path = INDEX_TARGETS[args.target]
            result = index_directory(path, workers=4, force=args.force)
            print(f"\nResult: {result['status']}")
            if result.get('output'):
                print(result['output'])
        else:
            print(f"Unknown target: {args.target}")
            print(f"Available: {list(INDEX_TARGETS.keys())}")
        return
    
    # Index everything
    results = index_all_targets(parallel=True, max_workers=args.workers)
    
    # Show final stats
    print("\n")
    stats = get_index_stats()
    if "system" in stats:
        print("=== Final Database State ===")
        for name, value in stats["system"].items():
            print(f"  {name}: {value}")


if __name__ == "__main__":
    main()

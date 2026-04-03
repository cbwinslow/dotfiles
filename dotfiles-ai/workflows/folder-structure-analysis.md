# Workflow: Folder Structure Analysis

Analyze folder contents using CBW RAG saved queries.

## Overview

Use the RAG database to understand folder structures, find files by type, and analyze codebase organization.

## Quick Commands

```bash
# Get system stats
rag-index-cmd stats

# View all database functions
rag-index-cmd functions

# View all database views
rag-index-cmd views

# Search for files
rag-index-cmd search "middleware pattern"

# Find duplicates
rag-index-cmd duplicates

# Recently modified files
rag-index-cmd recent 7
```

## Python API Usage

### System Overview

```python
from unified_memory import (
    get_system_stats,
    get_file_stats_by_extension,
    get_dotfiles_summary
)

# Overall database stats
stats = get_system_stats()
print(f"Total files: {stats['total_files']}")
print(f"Total chunks: {stats['total_chunks']}")
print(f"Unique extensions: {stats['unique_extensions']}")

# File type breakdown
ext_stats = get_file_stats_by_extension()
for ext in ext_stats[:10]:
    print(f"{ext['file_extension']}: {ext['file_count']} files")

# Dotfiles summary
dotfiles = get_dotfiles_summary()
print(f"Dotfiles indexed: {dotfiles['total_dotfiles']}")
```

### Folder Analysis

```python
from unified_memory import (
    analyze_folder_structure,
    find_files_in_tree,
    get_directory_summary
)

# Analyze a specific folder
analysis = analyze_folder_structure("/home/cbwinslow/dotfiles/ai")
print(f"Files: {analysis['total_files']}")
print(f"Size: {analysis['total_size_bytes']} bytes")
print(f"Extensions: {analysis['by_extension']}")
print(f"Subdirs: {analysis['subdirectories']}")

# Find files in tree
files = find_files_in_tree("/home/cbwinslow/dotfiles", "*.py", max_depth=5)
for f in files:
    print(f"{f['file_path']} ({f['file_size_bytes']} bytes)")

# Get directory summary
summary = get_directory_summary("/home/cbwinslow/dotfiles/ai")
for item in summary:
    print(f"{item['item_type']}: {item['item_name']} ({item['item_count']} items)")
```

### File Type Queries

```python
from unified_memory import (
    get_python_files,
    get_config_files,
    get_shell_files,
    get_doc_files
)

# Get specific file types
python_files = get_python_files(limit=20)
config_files = get_config_files(limit=20)
shell_files = get_shell_files(limit=20)
doc_files = get_doc_files(limit=20)

# Print summary
print(f"Python files: {len(python_files)}")
print(f"Config files: {len(config_files)}")
print(f"Shell scripts: {len(shell_files)}")
print(f"Documentation: {len(doc_files)}")
```

### Content Search

```python
from unified_memory import (
    search_files_content,
    find_similar_code,
    quick_search
)

# Search file content
results = search_files_content("database connection", file_extensions=['.py'], max_results=5)
for r in results:
    print(f"{r['file_path']}:{r['line_start']}")
    print(f"  {r['chunk_text'][:100]}...")

# Find similar code patterns
code_matches = find_similar_code("def authenticate", language="python", max_results=5)

# Quick search (searches all file types)
quick_results = quick_search("docker compose")
```

### Maintenance Queries

```python
from unified_memory import (
    get_recent_files,
    get_large_files,
    get_duplicate_files,
    find_recently_modified
)

# Recently modified
recent = get_recent_files(limit=20)

# Large files (>1MB)
large = get_large_files(min_size_bytes=1048576)

# Find duplicates
dups = get_duplicate_files()
for dup in dups[:5]:
    print(f"Hash: {dup['content_hash'][:16]}...")
    print(f"  Count: {dup['duplicate_count']}")
    print(f"  Files: {dup['all_paths'][:3]}")

# Modified in last N days
modified = find_recently_modified(days=3)
```

## Database Views Reference

| View | Description |
|------|-------------|
| `v_active_files` | All non-deleted files with metadata |
| `v_file_stats_by_extension` | File counts grouped by extension |
| `v_recent_files` | Recently modified files |
| `v_large_files` | Files >1MB with size info |
| `v_duplicate_groups` | Groups of duplicate files |
| `v_directory_stats` | Stats per directory |
| `v_file_chunks_full` | All chunks with file info |
| `v_python_files` | Python files only |
| `v_config_files` | Config files (.yaml, .json, etc.) |
| `v_shell_files` | Shell scripts |
| `v_doc_files` | Documentation files |

## SQL Functions Reference

| Function | Description |
|----------|-------------|
| `search_files_content(term, extensions, limit)` | Search content with filters |
| `find_files_in_tree(root, pattern, depth)` | Find files under path |
| `find_similar_code(pattern, language, limit)` | Find code patterns |
| `get_directory_summary(path)` | Get directory contents |
| `find_recently_modified(since)` | Find recently changed files |
| `get_system_stats()` | Overall statistics |

## Common Patterns

### Pattern: Find All Python in Project
```python
from unified_memory import find_files_in_tree

python_files = find_files_in_tree(
    "/home/cbwinslow/dotfiles",
    "*.py",
    max_depth=10
)
print(f"Found {len(python_files)} Python files")
```

### Pattern: Find Config Patterns
```python
from unified_memory import search_files_content

# Find all YAML configs with "service"
service_configs = search_files_content(
    "service:",
    file_extensions=['.yaml', '.yml'],
    max_results=20
)
```

### Pattern: Analyze Directory Growth
```python
from unified_memory import get_directory_stats

# Compare file counts across directories
dir_stats = get_directory_stats()
for d in dir_stats[:10]:
    print(f"{d['directory_path']}: {d['file_count']} files")
```

### Pattern: Find Unindexed Areas
```python
from unified_memory.queries import _get_db

# Check what directories are NOT indexed
check_dirs = [
    "/home/cbwinslow/.config",
    "/home/cbwinslow/.local",
    "/home/cbwinslow/workspace",
]

conn = _get_db()
with conn.cursor() as cur:
    for d in check_dirs:
        cur.execute("SELECT COUNT(*) FROM files WHERE file_path LIKE %s", (d + '/%',))
        count = cur.fetchone()[0]
        status = "✓" if count > 0 else "✗"
        print(f"{status} {d}: {count} files")
```

## Indexing New Areas

```bash
# Index a new directory
python3 ~/projects/ai/rag_system/cbw_indexer.py \
    /path/to/new/directory \
    --db "$CBW_RAG_DATABASE" \
    --use-ollama \
    --workers 6

# Force reindex (updates existing files)
python3 ~/projects/ai/rag_system/cbw_indexer.py \
    /path/to/directory \
    --db "$CBW_RAG_DATABASE" \
    --use-ollama \
    --workers 6
```

## SQL Query Examples

```sql
-- Find all files in dotfiles repo
SELECT file_path, file_name, file_extension
FROM v_active_files
WHERE file_path LIKE '%dotfiles%'
ORDER BY file_path;

-- Find recently added files
SELECT file_path, indexed_at
FROM v_active_files
WHERE indexed_at > NOW() - INTERVAL '1 day'
ORDER BY indexed_at DESC;

-- Find files by content pattern
SELECT * FROM search_files_content('def main', ARRAY['.py'], 10);

-- Get directory tree
SELECT * FROM find_files_in_tree('/home/cbwinslow/dotfiles/ai', '%', 3);
```

## Integration with Agents

Add to agent config for folder analysis:

```yaml
skills:
  - unified_memory

tools:
  - unified_memory.analyze_folder_structure
  - unified_memory.search_files_content
  - unified_memory.find_similar_code
  - unified_memory.get_system_stats
```

## See Also

- `unified-memory-system.md` - Full memory system
- `rag-assisted-coding.md` - Coding with RAG
- `cbw_rag_saved_queries.sql` - Database schema

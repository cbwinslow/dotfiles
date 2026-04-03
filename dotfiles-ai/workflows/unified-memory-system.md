# Workflow: Unified Memory System

Complete workflow for using Letta A0 + CBW RAG together.

## Philosophy

The unified memory system creates a **seamless knowledge layer** across:
- **Agent Memory (Letta)**: Conversations, decisions, learned facts
- **File Memory (RAG)**: Code contents, patterns, documentation

Everything is automatically connected and searchable.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    UNIFIED MEMORY                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐        ┌──────────────┐                  │
│  │  Letta A0    │        │  CBW RAG     │                  │
│  │  Memory      │◄──────►│  File Index  │                  │
│  │              │        │              │                  │
│  │ • Agent conv │        │ • Code files │                  │
│  │ • Learnings  │        │ • Chunks     │                  │
│  │ • Facts      │        │ • Embeddings │                  │
│  │ • Tasks      │        │ • Duplicates │                  │
│  └──────────────┘        └──────────────┘                  │
│         │                        │                          │
│         └────────┬───────────────┘                          │
│                  ▼                                          │
│         ┌──────────────┐                                   │
│         │  PostgreSQL  │                                   │
│         │  + pgvector  │                                   │
│         └──────────────┘                                   │
└─────────────────────────────────────────────────────────────┘
```

## Auto-Behaviors

### 1. Instance Tracking
Every agent session gets a unique ID:
```
windsurf_20260329183045_a1b2c3d4
```
All memories are tagged with this instance.

### 2. Pre-Task Context
Before every task, automatically:
1. Search Letta for related past work
2. Search RAG for relevant code files
3. Combine into formatted context

### 3. Post-Task Storage
After every task, automatically:
1. Store task result in Letta
2. Store learned facts
3. Note files modified

### 4. Cross-Reference
When storing facts, also note related files:
```python
store_fact("Use pydantic v2 for validation")
# Also tags: files where pydantic is used
```

## Usage Patterns

### Pattern 1: Coding with Full Context

```python
from unified_memory import UnifiedMemorySkill

memory = UnifiedMemorySkill()

# Before coding - get everything
context = memory.before_task("Implement OAuth2 flow")
# Returns:
# - Past OAuth work from Letta
# - Existing auth code from RAG
# - Relevant middleware patterns

# Code with context in prompt...

# After coding - store everything
memory.after_task(
    "Implement OAuth2",
    "Added OAuth2 with PKCE",
    learned=[
        "PKCE is required for mobile apps",
        "State parameter prevents CSRF"
    ],
    files_modified=[
        "/app/auth/oauth.py",
        "/app/config/oauth.py"
    ]
)
```

### Pattern 2: Investigating Issues

```python
# Search across both systems
from unified_memory import search_code, search_files

# Find error handling in codebase
error_patterns = search_code("error handling", language="python")

# Find related past issues
memory = UnifiedMemorySkill()
context = memory.before_task("Debug authentication error")

# Combines:
# - Past auth issues from Letta
# - Auth-related code from RAG
```

### Pattern 3: Code Review

```python
# Check for duplicates before review
from unified_memory import find_duplicates

file_path = "/app/utils/helpers.py"
dups = find_duplicates(file_path)
if dups:
    print(f"Warning: {len(dups)} similar files exist")

# Get context for review
memory = UnifiedMemorySkill()
context = memory.before_task(f"Review {file_path}")
```

### Pattern 4: Knowledge Building

```python
# Store architectural decisions
from unified_memory import store_fact

store_fact("""
Architecture Decision: Use CQRS pattern for inventory service.
Rationale: Write-heavy operations need separate optimization.
Date: 2026-03-29
""")

# Later, when working on inventory:
context = before_task("Add inventory tracking")
# Will include the CQRS decision from memory
```

## Database Connections

### Letta (A0 Memory)
```yaml
Database: letta
Host: localhost:5432 (via 172.17.0.1 from Docker)
User: cbwinslow
Tables: agents, messages, memory_blocks, conversations
```

### CBW RAG
```yaml
Database: cbw_rag
Host: localhost:5432
User: cbwinslow
Tables: files, file_chunks, duplicate_files, code_fingerprints
Extensions: pgvector
```

## Query Examples

### Search Letta Memories
```sql
-- Find past tasks similar to current work
SELECT content, created_at 
FROM messages 
WHERE content ILIKE '%authentication%' 
ORDER BY created_at DESC;
```

### Search RAG Files
```sql
-- Semantic search on code
SELECT f.file_path, fc.chunk_text
FROM file_chunks fc
JOIN files f ON f.id = fc.file_id
WHERE fc.chunk_text ILIKE '%middleware%'
ORDER BY length(fc.chunk_text) DESC;
```

### Combined View
```sql
-- All knowledge about a topic
SELECT 'letta' as source, content as text, created_at
FROM messages
WHERE content ILIKE '%docker%'

UNION ALL

SELECT 'rag' as source, fc.chunk_text as text, f.indexed_at as created_at
FROM file_chunks fc
JOIN files f ON f.id = fc.file_id
WHERE fc.chunk_text ILIKE '%docker%';
```

## Configuration

### Environment Variables
```bash
# ~/.bash_secrets

# Letta (A0 Memory)
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_PG_URI="postgresql://cbwinslow:123qweasd@172.17.0.1:5432/letta"
export A0_AUTO_INIT="true"

# CBW RAG
export CBW_RAG_DATABASE="postgresql://cbwinslow:123qweasd@localhost:5432/cbw_rag"
export CBW_RAG_OLLAMA_URL="http://localhost:11434"
export CBW_RAG_EMBEDDING_MODEL="nomic-embed-text"
export UNIFIED_MEMORY_AUTO_INIT="true"
```

### Agent Config
```yaml
# base_agent.yaml additions
skills:
  - unified_memory
  
tools:
  - unified_memory.before_task
  - unified_memory.after_task
  - unified_memory.search_files
  - unified_memory.search_code
  - unified_memory.find_duplicates
  - unified_memory.store

mcp_servers:
  cbw_rag:
    command: python3
    args: ["~/dotfiles/ai/shared/mcp/rag_server.py"]
```

## Maintenance

### Reindex Files
```bash
# Add new directory to RAG
rag-index ~/new_project --workers 8

# Reindex with fresh embeddings
rag-index ~/project --workers 8 --force
```

### Check Stats
```bash
rag-stats
```

### Cleanup Duplicates
```python
from unified_memory import find_duplicates

# Find all duplicates
dups = find_duplicates("/path/to/check")
for dup in dups:
    print(f"Duplicate: {dup['file_path']}")
```

## Performance Tips

### Batch Operations
```python
# Index multiple directories at once
from cbw_indexer import Indexer

indexer = Indexer(db, embed_model)
stats = indexer.run_crawl(
    ["/path1", "/path2", "/path3"],
    parallel=True,
    max_workers=8
)
```

### Limit Context Size
```python
# Default limits prevent token overflow
context = before_task("Task")  # Auto-limits to top 3 files + 5 memories
```

### Use Language Filters
```python
# Faster than searching all files
results = search_code("pattern", language="python", limit=5)
```

## Troubleshooting

### Connection Issues
```bash
# Check Letta server
curl http://localhost:8283/v1/health

# Check Ollama
curl http://localhost:11434/api/tags

# Check PostgreSQL
psql $CBW_RAG_DATABASE -c "SELECT 1"
```

### Missing Embeddings
```bash
# Regenerate embeddings for a directory
rag-index ~/project --force
```

### Slow Queries
```bash
# Check database indexes
psql $CBW_RAG_DATABASE -c "\di"
```

## See Also

- Skill: `unified_memory` - Python implementation
- Skill: `a0_memory` - Letta-only interface
- Skill: `cbw_rag` - RAG-only interface
- Workflow: `rag-assisted-coding.md`
- Workflow: `a0-autonomous-memory.md`

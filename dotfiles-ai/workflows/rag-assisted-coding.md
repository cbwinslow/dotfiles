# Workflow: RAG-Assisted Coding

Use CBW RAG + Letta memory for context-aware coding.

## When to Use

- Starting work on an unfamiliar codebase
- Need to understand existing code patterns
- Looking for similar implementations
- Debugging issues with existing code

## Steps

### 1. Pre-Task Context Retrieval

```python
from unified_memory import before_task, search_code

# Automatically get context
context = before_task("Implement rate limiting middleware")

# Or manually search for patterns
similar = search_code("rate limiting", language="python", limit=3)
```

### 2. Understand Existing Patterns

```python
# Find authentication patterns in this codebase
auth_patterns = search_code("authentication decorator", language="python")

# Find error handling patterns  
error_patterns = search_code("try except logging", language="python")
```

### 3. Check for Duplicates

```python
from unified_memory import find_duplicates

# Before creating new file, check if similar exists
dups = find_duplicates("/app/middleware/new_auth.py")
if dups:
    print(f"Similar files exist: {[d['file_path'] for d in dups]}")
```

### 4. Code with Context

The `before_task()` output includes:
- Past decisions from Letta memory
- Relevant code files from RAG
- File structure and patterns

```
[AUTOMATICALLY RETRIEVED CONTEXT]

## Previous Memories (Agent Learnings)
- User prefers fastapi over flask for new APIs
- Always add type hints to public functions

## Relevant Code/Files (RAG)
### /app/middleware/auth.py:23
```python
def require_auth(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        ...
```

### /app/routes/api.py:45
```python
@app.middleware("http")
async def add_process_time_header(request, call_next):
    ...
```

[END CONTEXT]
```

### 5. Post-Task Documentation

```python
from unified_memory import after_task

after_task(
    "Implement rate limiting",
    result="Added Redis-based rate limiter",
    learned=[
        "Redis TTL is in seconds, not milliseconds",
        "FastAPI middleware order matters"
    ],
    files_modified=[
        "/app/middleware/rate_limit.py",
        "/app/config/redis.py"
    ]
)
```

## Best Practices

### Always Search First
```python
# Before implementing, check if it exists
results = search_files("rate limit")
if results:
    print("Rate limiting already implemented:")
    for r in results:
        print(f"  - {r['file_path']}")
```

### Language-Specific Searches
```python
# Find all middleware patterns by language
python_middleware = search_code("middleware", language="python", limit=5)
js_middleware = search_code("middleware", language="javascript", limit=5)
```

### Use Context Window Wisely
```python
# Get top 3 most relevant files only
context = before_task("Fix bug", use_rag=True)
# Context is pre-formatted and limited to avoid token overflow
```

### Store Learnings Immediately
```python
# While coding, store discoveries
from unified_memory import store_fact

store_fact("FastAPI BackgroundTasks use threadpool, not asyncio")
```

## Common Patterns

### Pattern: API Endpoint Creation
```python
# 1. Search existing endpoints
endpoints = search_code("@app.get", language="python")

# 2. Check authentication patterns
auth = search_code("require_auth", language="python")

# 3. Create with context
context = before_task("Create new user endpoint")

# 4. Implement following patterns
# ... coding ...

# 5. Document
after_task("Create user endpoint", "Done", files_modified=["/app/routes/users.py"])
```

### Pattern: Database Migration
```python
# 1. Find existing migrations
migrations = search_files("CREATE TABLE")

# 2. Check migration patterns
patterns = search_code("alembic migration", language="python")

# 3. Understand schema conventions
schema = search_code("Column\(" + """""" + """,", language="python")

# 4. Create migration with context
context = before_task("Add user preferences table")
```

### Pattern: Bug Fix
```python
# 1. Search for similar error handling
error_handling = search_code("try.*except.*Exception", language="python")

# 2. Find where error occurs
location = search_files("function_that_fails")

# 3. Check past fixes for similar issues
context = before_task("Fix timeout error in API calls")

# 4. Fix and document
after_task("Fix timeout", "Added retry logic", learned=["Requests timeout after 30s by default"])
```

## CLI Tools

Use shell commands for quick searches:

```bash
# Index new directory
rag-index ~/new_project --workers 4

# Search files
rag-search "middleware pattern"

# Find duplicates
rag-duplicates

# Show stats
rag-stats
```

## Integration

Add to agent config:

```yaml
skills:
  - unified_memory

workflows:
  - rag-assisted-coding

tools:
  - unified_memory.before_task
  - unified_memory.after_task
  - unified_memory.search_files
  - unified_memory.search_code
```

## See Also

- `unified-memory-system.md` - Full memory system workflow
- `a0-autonomous-memory.md` - Letta-only memory workflow
- Skill: `unified_memory` - Implementation

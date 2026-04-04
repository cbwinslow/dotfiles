---
name: cbw-rag
description: Search and retrieve files from the CBW RAG vector database. Use this skill to semantically search all indexed files on the server using natural language queries.
tools:
  bash: true
  read: true
---

# CBW RAG Search Skill

You have access to a RAG (Retrieval-Augmented Generation) database containing vectorized files from the server. Use this skill to search for relevant file content using natural language.

## Database

- **PostgreSQL 16** with **pgvector 0.8** extension
- **Database**: `cbw_rag` on localhost:5432
- **Embedding model**: `nomic-embed-text` (768 dimensions via Ollama)
- **Connection**: `postgresql://cbwinslow:123qweasd@localhost:5432/cbw_rag`

## How to Search

Run the search CLI tool:

```bash
# Vector similarity search (semantic)
rag-search "your natural language query"

# Full-text search (keyword)
rag-search "your query" --text-only

# Hybrid search (default - combines vector + text)
rag-search "your query" --hybrid

# Filter by file type
rag-search "python async functions" --type code
rag-search "configuration settings" --type config

# Limit results
rag-search "query" -n 5

# Show database stats
rag-search --stats
```

## How to Index Files

```bash
# Index a directory
rag-index /path/to/directory

# Dry run (preview)
rag-index /path --dry-run --verbose

# Skip unchanged files
rag-index /path --resume
```

## Database Schema

The `cbw_rag` database contains:

- **`files`** - File metadata (path, name, type, size, owner, permissions, git info, language detection, MIME type, timestamps, tags, JSONB extras)
- **`document_chunks`** - Text content split into chunks with line positions
- **`embeddings`** - 768-dim vectors from nomic-embed-text model with HNSW index
- **`embeddings_large`** - 4096-dim vectors from qwen3-embedding model
- **`v_searchable`** - View joining chunks with their embeddings and file metadata

## Direct SQL Access

For advanced queries, connect directly:

```bash
PGPASSWORD=123qweasd psql -h localhost -U cbwinslow -d cbw_rag
```

### Example SQL Queries

```sql
-- Find similar files to a text query (requires embedding)
SELECT source_path, file_name, file_category, detected_language
FROM files WHERE index_status = 'indexed'
ORDER BY file_modified_at DESC LIMIT 20;

-- Full-text search directly
SELECT f.source_path, dc.content, dc.start_line
FROM document_chunks dc
JOIN files f ON f.id = dc.file_id
WHERE to_tsvector('english', dc.content) @@ plainto_tsquery('english', 'your query')
LIMIT 10;

-- Files by category
SELECT file_category, COUNT(*) FROM files
WHERE index_status = 'indexed'
GROUP BY file_category;

-- Files by language
SELECT detected_language, COUNT(*) FROM files
WHERE index_status = 'indexed' AND detected_language IS NOT NULL
GROUP BY detected_language ORDER BY count DESC;
```

## Environment Variables

Set in `~/.bash_secrets`:
- `CBW_RAG_DATABASE` - PostgreSQL connection string
- `CBW_RAG_OLLAMA_URL` - Ollama API URL (default: http://localhost:11434)
- `CBW_RAG_EMBEDDING_MODEL` - Embedding model name (default: nomic-embed-text)

## Source Code

- Indexer: `/home/cbwinslow/infra/cbw_rag/indexer.py`
- Search: `/home/cbwinslow/infra/cbw_rag/search.py`
- Schema: `/home/cbwinslow/infra/cbw_rag/schema.sql`

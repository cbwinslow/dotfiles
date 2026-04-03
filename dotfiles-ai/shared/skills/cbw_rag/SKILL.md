# CBW RAG Skill
# Semantic search and file indexing for all AI agents
# Location: ~/dotfiles/ai/skills/cbw_rag/SKILL.md

name: cbw_rag
description: "CBW RAG system for semantic search, file deduplication, and code similarity"
version: 1.0.0

## Overview

This skill provides RAG (Retrieval-Augmented Generation) capabilities for all AI agents:
- Semantic search across all indexed files
- Find duplicate files for cleanup
- Find similar code patterns
- Index new directories

All data is stored in PostgreSQL with pgvector for fast similarity search.
Secrets are loaded from ~/.bash_secrets.

## Operations

### `semantic_search`
Search for content using natural language queries.

**Parameters:**
- `query` (string): Natural language search query
- `limit` (int, optional): Max results (default: 10)
- `file_type` (string, optional): Filter by file extension

**Example:**
```python
results = cbw_rag.semantic_search("authentication middleware", limit=5)
```

### `find_duplicates`
Find duplicate files by hash or content similarity.

**Parameters:**
- `min_size` (int, optional): Minimum file size in bytes (default: 1024)
- `limit` (int, optional): Max duplicate groups (default: 100)

**Example:**
```python
duplicates = cbw_rag.find_duplicates(min_size=1024, limit=50)
```

### `similar_code`
Find similar code patterns across all indexed files.

**Parameters:**
- `code_snippet` (string): Code to find similar patterns for
- `language` (string, optional): Filter by programming language
- `threshold` (float, optional): Similarity threshold 0-1 (default: 0.8)
- `limit` (int, optional): Max results (default: 10)

**Example:**
```python
similar = cbw_rag.similar_code("def authenticate_user", language="python", limit=5)
```

### `index_files`
Index new directories into the RAG database.

**Parameters:**
- `paths` (list): Directory paths to index
- `recursive` (bool, optional): Index subdirectories (default: true)
- `workers` (int, optional): Parallel workers (default: 4)

**Example:**
```python
cbw_rag.index_files(["/home/cbwinslow/new_project"], recursive=True, workers=4)
```

## Configuration

The RAG system reads configuration from environment variables (set in ~/.bash_secrets):
- `CBW_RAG_DATABASE`: PostgreSQL connection string
- `CBW_RAG_OLLAMA_URL`: Ollama server URL (default: http://localhost:11434)
- `CBW_RAG_EMBEDDING_MODEL`: Embedding model name (default: nomic-embed-text)

## MCP Server

This skill is backed by an MCP server at:
`~/dotfiles/ai/shared/mcp/rag_server.py`

All AI tools (Windsurf, Cline, Claude Desktop, OpenCode, KiloCode, Gemini, Qwen) connect to this centralized server.

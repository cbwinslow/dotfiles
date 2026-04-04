---
name: rag-search
description: Search the CBW RAG vector database for files matching a natural language query
arguments:
  - name: query
    description: Natural language search query
    required: true
  - name: type
    description: "Filter by file category: code, document, config"
    required: false
  - name: limit
    description: Number of results to return (default: 10)
    required: false
---

Search the CBW RAG database using the `rag-search` CLI tool. The database contains vectorized files from the server with pgvector 0.8 and nomic-embed-text embeddings.

Run: `rag-search "{{query}}" {{#if type}}--type {{type}}{{/if}} {{#if limit}}-n {{limit}}{{/if}}`

If no results found, try `--text-only` for keyword search instead of vector similarity.

---
name: rag-index
description: Index files into the CBW RAG vector database
arguments:
  - name: path
    description: Directory path to index
    required: true
  - name: resume
    description: Skip files with unchanged content hash
    required: false
---

Index files from the specified directory into the CBW RAG database. Files are chunked, embedded via Ollama (nomic-embed-text), and stored in PostgreSQL with pgvector.

Run: `rag-index "{{path}}" {{#if resume}}--resume{{/if}} --verbose`

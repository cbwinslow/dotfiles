#!/bin/bash
# CBW RAG CLI Tools
# Source this file in your shell profile: source ~/dotfiles/ai/scripts/rag_cli.sh

# Load secrets
if [ -f ~/.bash_secrets ]; then
    source ~/.bash_secrets
fi

# RAG Index - Index files into the vector database
rag-index() {
    local target_path="${1:-.}"
    local workers="${2:-4}"
    
    if [ ! -d "$target_path" ] && [ ! -f "$target_path" ]; then
        echo "Error: Path not found: $target_path"
        echo "Usage: rag-index <path> [workers]"
        return 1
    fi
    
    echo "Indexing: $target_path (workers: $workers)"
    python3 /home/cbwinslow/projects/ai/rag_system/cbw_indexer.py \
        "$target_path" \
        --db "${CBW_RAG_DATABASE}" \
        --model "${CBW_RAG_EMBEDDING_MODEL:-nomic-embed-text}" \
        --workers "$workers" \
        --chunk-size 512
}

# RAG Search - Semantic search across indexed files
rag-search() {
    local query="$1"
    local limit="${2:-10}"
    local file_type="${3:-}"
    
    if [ -z "$query" ]; then
        echo "Usage: rag-search <query> [limit] [file_type]"
        echo "Examples:"
        echo "  rag-search 'authentication middleware' 5"
        echo "  rag-search 'database connection' 10 py"
        return 1
    fi
    
    # Use the MCP server or direct SQL query via search function
    source ~/.bash_secrets
    
    if [ -n "$file_type" ]; then
        psql "$CBW_RAG_DATABASE" -c "
            SELECT f.file_path, f.file_name, fc.chunk_text, 
                   1 - (fc.embedding <=> (SELECT embedding FROM file_chunks LIMIT 1)) as similarity
            FROM file_chunks fc
            JOIN files f ON fc.file_id = f.id
            WHERE f.file_extension = '.$file_type'
            ORDER BY fc.embedding <=> (SELECT embedding FROM file_chunks LIMIT 1)
            LIMIT $limit;
        " 2>/dev/null || echo "Error: Could not search. Is the database running?"
    else
        psql "$CBW_RAG_DATABASE" -c "
            SELECT * FROM search_similar_content(
                (SELECT embedding FROM file_chunks WHERE chunk_text ILIKE '%$query%' LIMIT 1),
                0.7,
                $limit
            );
        " 2>/dev/null || echo "Note: Using fallback search method"
        
        # Fallback: simple text search
        psql "$CBW_RAG_DATABASE" -c "
            SELECT f.file_path, f.file_name, LEFT(fc.chunk_text, 200) as preview
            FROM file_chunks fc
            JOIN files f ON fc.file_id = f.id
            WHERE fc.chunk_text ILIKE '%$query%'
            LIMIT $limit;
        "
    fi
}

# RAG Stats - Show database statistics
rag-stats() {
    source ~/.bash_secrets
    
    echo "=== CBW RAG Statistics ==="
    echo ""
    
    echo "Files indexed:"
    psql "$CBW_RAG_DATABASE" -c "SELECT COUNT(*) as files FROM files WHERE is_deleted = false;"
    
    echo ""
    echo "Total chunks:"
    psql "$CBW_RAG_DATABASE" -c "SELECT COUNT(*) as chunks FROM file_chunks;"
    
    echo ""
    echo "File types distribution:"
    psql "$CBW_RAG_DATABASE" -c "
        SELECT file_extension, COUNT(*) as count 
        FROM files 
        WHERE file_extension IS NOT NULL AND is_deleted = false
        GROUP BY file_extension 
        ORDER BY count DESC 
        LIMIT 10;
    "
    
    echo ""
    echo "Database size:"
    psql "$CBW_RAG_DATABASE" -c "
        SELECT pg_size_pretty(pg_database_size(current_database())) as db_size;
    "
}

# RAG Find Duplicates - Find duplicate files
rag-duplicates() {
    source ~/.bash_secrets
    
    psql "$CBW_RAG_DATABASE" -c "
        SELECT content_hash, COUNT(*) as duplicate_count, 
               STRING_AGG(file_path, ', ' ORDER BY file_path) as files
        FROM files
        WHERE is_deleted = false
        GROUP BY content_hash
        HAVING COUNT(*) > 1
        ORDER BY duplicate_count DESC
        LIMIT 20;
    "
}

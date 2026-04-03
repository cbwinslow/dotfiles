-- Saved queries for CBW RAG system
-- These views and functions provide clean interfaces for skills/workflows

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: All active files with metadata
CREATE OR REPLACE VIEW v_active_files AS
SELECT 
    id,
    file_path,
    file_name,
    file_extension,
    file_size_bytes,
    content_hash,
    indexed_at,
    modified_at,
    regexp_replace(file_path, '/[^/]+$', '') as directory_path
FROM files
WHERE is_deleted = FALSE
ORDER BY indexed_at DESC;

-- View: File count by extension
CREATE OR REPLACE VIEW v_file_stats_by_extension AS
SELECT 
    file_extension,
    COUNT(*) as file_count,
    SUM(file_size_bytes) as total_size_bytes,
    MIN(indexed_at) as first_indexed,
    MAX(indexed_at) as last_indexed
FROM files
WHERE is_deleted = FALSE
GROUP BY file_extension
ORDER BY file_count DESC;

-- View: Recent files
CREATE OR REPLACE VIEW v_recent_files AS
SELECT 
    file_path,
    file_name,
    file_extension,
    modified_at,
    indexed_at
FROM files
WHERE is_deleted = FALSE
ORDER BY modified_at DESC NULLS LAST
LIMIT 100;

-- View: Large files (>1MB)
CREATE OR REPLACE VIEW v_large_files AS
SELECT 
    file_path,
    file_name,
    file_extension,
    file_size_bytes,
    pg_size_pretty(file_size_bytes) as size_pretty
FROM files
WHERE is_deleted = FALSE 
AND file_size_bytes > 1048576
ORDER BY file_size_bytes DESC;

-- View: Duplicate file groups
CREATE OR REPLACE VIEW v_duplicate_groups AS
SELECT 
    f.content_hash,
    COUNT(*) as duplicate_count,
    MIN(f.file_path) as first_file,
    ARRAY_AGG(f.file_path) as all_paths
FROM files f
WHERE f.is_deleted = FALSE
AND EXISTS (
    SELECT 1 FROM files f2 
    WHERE f2.content_hash = f.content_hash 
    AND f2.id != f.id 
    AND f2.is_deleted = FALSE
)
GROUP BY f.content_hash
ORDER BY duplicate_count DESC;

-- View: Directory statistics
CREATE OR REPLACE VIEW v_directory_stats AS
SELECT 
    regexp_replace(file_path, '/[^/]+$', '') as directory_path,
    COUNT(*) as file_count,
    COUNT(DISTINCT file_extension) as unique_extensions,
    SUM(file_size_bytes) as total_size_bytes,
    MIN(indexed_at) as first_indexed,
    MAX(indexed_at) as last_indexed
FROM files
WHERE is_deleted = FALSE
GROUP BY regexp_replace(file_path, '/[^/]+$', '')
ORDER BY file_count DESC;

-- View: All chunks with file info
CREATE OR REPLACE VIEW v_file_chunks_full AS
SELECT 
    fc.id as chunk_id,
    fc.file_id,
    f.file_path,
    f.file_name,
    f.file_extension,
    fc.chunk_text,
    fc.line_start,
    fc.line_end,
    fc.chunk_index,
    LENGTH(fc.chunk_text) as chunk_length
FROM file_chunks fc
JOIN files f ON f.id = fc.file_id
WHERE f.is_deleted = FALSE;

-- View: Python files only
CREATE OR REPLACE VIEW v_python_files AS
SELECT * FROM files 
WHERE is_deleted = FALSE 
AND file_extension = '.py';

-- View: Config files (.yaml, .yml, .json, .toml, .ini)
CREATE OR REPLACE VIEW v_config_files AS
SELECT * FROM files 
WHERE is_deleted = FALSE 
AND file_extension IN ('.yaml', '.yml', '.json', '.toml', '.ini', '.conf', '.cfg');

-- View: Shell scripts
CREATE OR REPLACE VIEW v_shell_files AS
SELECT * FROM files 
WHERE is_deleted = FALSE 
AND file_extension IN ('.sh', '.bash', '.zsh', '.fish');

-- View: Documentation files
CREATE OR REPLACE VIEW v_doc_files AS
SELECT * FROM files 
WHERE is_deleted = FALSE 
AND file_extension IN ('.md', '.txt', '.rst', '.adoc');

-- ============================================================================
-- FUNCTIONS FOR SKILLS/WORKFLOWS
-- ============================================================================

-- Function: Search files by content
CREATE OR REPLACE FUNCTION search_files_content(
    search_term TEXT,
    file_extensions TEXT[] DEFAULT NULL,
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    file_path TEXT,
    file_name TEXT,
    file_extension TEXT,
    chunk_text TEXT,
    line_start INTEGER,
    line_end INTEGER,
    relevance INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.file_path,
        f.file_name,
        f.file_extension,
        fc.chunk_text,
        fc.line_start,
        fc.line_end,
        (LENGTH(fc.chunk_text) - LENGTH(REPLACE(LOWER(fc.chunk_text), LOWER(search_term), ''))) / LENGTH(search_term) as relevance
    FROM files f
    JOIN file_chunks fc ON f.id = fc.file_id
    WHERE f.is_deleted = FALSE
    AND fc.chunk_text ILIKE '%' || search_term || '%'
    AND (file_extensions IS NULL OR f.file_extension = ANY(file_extensions))
    ORDER BY relevance DESC, f.file_path
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function: Find files in directory tree
CREATE OR REPLACE FUNCTION find_files_in_tree(
    root_path TEXT,
    file_pattern TEXT DEFAULT '%',
    max_depth INTEGER DEFAULT 10
)
RETURNS TABLE (
    file_path TEXT,
    file_name TEXT,
    file_extension TEXT,
    file_size_bytes BIGINT,
    depth INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.file_path,
        f.file_name,
        f.file_extension,
        f.file_size_bytes,
        (LENGTH(f.file_path) - LENGTH(REPLACE(f.file_path, '/', ''))) as depth
    FROM files f
    WHERE f.is_deleted = FALSE
    AND f.file_path LIKE root_path || '%'
    AND f.file_name ILIKE file_pattern
    AND (LENGTH(f.file_path) - LENGTH(REPLACE(f.file_path, '/', ''))) <= max_depth
    ORDER BY f.file_path;
END;
$$ LANGUAGE plpgsql;

-- Function: Get file with context (neighboring files in same directory)
CREATE OR REPLACE FUNCTION get_file_with_context(
    target_file_path TEXT,
    context_radius INTEGER DEFAULT 3
)
RETURNS TABLE (
    file_path TEXT,
    file_name TEXT,
    distance INTEGER
) AS $$
DECLARE
    target_dir TEXT;
BEGIN
    target_dir := regexp_replace(target_file_path, '/[^/]+$', '');
    
    RETURN QUERY
    SELECT 
        f.file_path,
        f.file_name,
        ABS(row_number() OVER (ORDER BY f.file_name) - 
            (SELECT row_number() FROM (SELECT row_number() OVER (ORDER BY file_name), file_path FROM files WHERE directory_path = target_dir AND is_deleted = FALSE) sub WHERE file_path = target_file_path)
        )::INTEGER as distance
    FROM files f
    WHERE f.directory_path = target_dir
    AND f.is_deleted = FALSE
    ORDER BY f.file_name;
END;
$$ LANGUAGE plpgsql;

-- Function: Find similar code patterns
CREATE OR REPLACE FUNCTION find_similar_code(
    code_pattern TEXT,
    language TEXT DEFAULT NULL,
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    file_path TEXT,
    file_name TEXT,
    chunk_text TEXT,
    line_start INTEGER,
    similarity_score INTEGER
) AS $$
DECLARE
    lang_ext TEXT;
BEGIN
    lang_ext := CASE LOWER(language)
        WHEN 'python' THEN '.py'
        WHEN 'javascript' THEN '.js'
        WHEN 'typescript' THEN '.ts'
        WHEN 'java' THEN '.java'
        WHEN 'go' THEN '.go'
        WHEN 'rust' THEN '.rs'
        WHEN 'cpp' THEN '.cpp'
        WHEN 'c' THEN '.c'
        WHEN 'ruby' THEN '.rb'
        WHEN 'php' THEN '.php'
        WHEN 'shell' THEN '.sh'
        ELSE NULL
    END;
    
    RETURN QUERY
    SELECT 
        f.file_path,
        f.file_name,
        fc.chunk_text,
        fc.line_start,
        (LENGTH(fc.chunk_text) - LENGTH(REPLACE(LOWER(fc.chunk_text), LOWER(code_pattern), ''))) / LENGTH(code_pattern) as similarity_score
    FROM files f
    JOIN file_chunks fc ON f.id = fc.file_id
    WHERE f.is_deleted = FALSE
    AND fc.chunk_text ILIKE '%' || code_pattern || '%'
    AND (lang_ext IS NULL OR f.file_extension = lang_ext)
    ORDER BY similarity_score DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function: Get directory structure summary
CREATE OR REPLACE FUNCTION get_directory_summary(dir_path TEXT)
RETURNS TABLE (
    item_type TEXT,
    item_name TEXT,
    item_count BIGINT,
    total_size BIGINT
) AS $$
BEGIN
    -- Subdirectories
    RETURN QUERY
    SELECT 
        'directory'::TEXT as item_type,
        regexp_replace(file_path, '^.*/([^/]+)/[^/]+$', '\1') as item_name,
        COUNT(*)::BIGINT as item_count,
        SUM(file_size_bytes)::BIGINT as total_size
    FROM files
    WHERE is_deleted = FALSE
    AND file_path LIKE dir_path || '/%'
    AND file_path NOT LIKE dir_path || '/%/%'
    GROUP BY regexp_replace(file_path, '^.*/([^/]+)/[^/]+$', '\1')
    
    UNION ALL
    
    -- Files directly in this directory
    SELECT 
        'file'::TEXT as item_type,
        file_name as item_name,
        1::BIGINT as item_count,
        file_size_bytes as total_size
    FROM files
    WHERE is_deleted = FALSE
    AND regexp_replace(file_path, '/[^/]+$', '') = dir_path;
END;
$$ LANGUAGE plpgsql;

-- Function: Find files by modification time
CREATE OR REPLACE FUNCTION find_recently_modified(
    since_timestamp TIMESTAMP DEFAULT (NOW() - INTERVAL '7 days')
)
RETURNS TABLE (
    file_path TEXT,
    file_name TEXT,
    last_modified_at TIMESTAMP,
    file_size_bytes BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.file_path,
        f.file_name,
        f.modified_at,
        f.file_size_bytes
    FROM files f
    WHERE f.is_deleted = FALSE
    AND (f.modified_at >= since_timestamp OR f.indexed_at >= since_timestamp)
    ORDER BY COALESCE(f.modified_at, f.indexed_at) DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Full system stats
CREATE OR REPLACE FUNCTION get_system_stats()
RETURNS TABLE (
    stat_name TEXT,
    stat_value BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'total_files'::TEXT, COUNT(*)::BIGINT FROM files WHERE is_deleted = FALSE
    UNION ALL
    SELECT 'total_chunks', COUNT(*)::BIGINT FROM file_chunks
    UNION ALL
    SELECT 'total_bytes', COALESCE(SUM(file_size_bytes), 0)::BIGINT FROM files WHERE is_deleted = FALSE
    UNION ALL
    SELECT 'unique_extensions', COUNT(DISTINCT file_extension)::BIGINT FROM files WHERE is_deleted = FALSE
    UNION ALL
    SELECT 'duplicate_groups', COUNT(DISTINCT content_hash)::BIGINT FROM files 
        WHERE is_deleted = FALSE AND content_hash IN (
            SELECT content_hash FROM files WHERE is_deleted = FALSE GROUP BY content_hash HAVING COUNT(*) > 1
        )
    UNION ALL
    SELECT 'indexed_dirs', COUNT(DISTINCT regexp_replace(file_path, '/[^/]+$', ''))::BIGINT FROM files WHERE is_deleted = FALSE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_files_directory_path ON files((regexp_replace(file_path, '/[^/]+$', '')));
CREATE INDEX IF NOT EXISTS idx_files_last_modified ON files(modified_at);
CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON file_chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_chunks_line_start ON file_chunks(line_start);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON VIEW v_active_files IS 'All non-deleted files with metadata';
COMMENT ON VIEW v_file_stats_by_extension IS 'File statistics grouped by extension';
COMMENT ON VIEW v_duplicate_groups IS 'Groups of duplicate files by content hash';
COMMENT ON FUNCTION search_files_content IS 'Search file chunks for content matching search_term';
COMMENT ON FUNCTION find_files_in_tree IS 'Find files under a root path with optional pattern matching';
COMMENT ON FUNCTION get_directory_summary IS 'Get summary of directory contents';

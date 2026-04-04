#!/bin/bash

# Migration script for Letta data from epstein database to current Letta server

# Step 1: Export data from epstein database
echo "Exporting data from epstein database..."

# Export letta_memories
psql -d epstein -c "\COPY (SELECT id::text AS id, memory_type AS label, content AS value, title AS description, created_at, updated_at FROM letta_memories) TO '/tmp/letta_memories.csv' WITH CSV HEADER"

# Export letta_memory_blocks
psql -d epstein -c "\COPY (SELECT id::text AS id, label, content, description, created_at, updated_at FROM letta_memory_blocks) TO '/tmp/letta_memory_blocks.csv' WITH CSV HEADER"

# Export letta_agent_context
psql -d epstein -c "\COPY (SELECT id::text AS id, agent_name || '_' || context_key AS label, context_value AS value, 'Agent context' AS description, created_at, updated_at FROM letta_agent_context) TO '/tmp/letta_agent_context.csv' WITH CSV HEADER"

# Step 2: Copy CSV files to Letta container
echo "Copying CSV files to Letta container..."
docker cp /tmp/letta_memories.csv letta-server:/tmp/
docker cp /tmp/letta_memory_blocks.csv letta-server:/tmp/
docker cp /tmp/letta_agent_context.csv letta-server:/tmp/

# Step 3: Import data into Letta server's database with proper column mapping
echo "Importing data into Letta server's database..."

# Import letta_memories
docker exec letta-server psql -U letta -d letta -c "\COPY block (id, label, value, description, created_at, updated_at, organization_id, is_template, read_only, version, hidden) FROM '/tmp/letta_memories.csv' WITH CSV HEADER"

# Import letta_memory_blocks
docker exec letta-server psql -U letta -d letta -c "\COPY block (id, label, value, description, created_at, updated_at, organization_id, is_template, read_only, version, hidden) FROM '/tmp/letta_memory_blocks.csv' WITH CSV HEADER"

# Import letta_agent_context
docker exec letta-server psql -U letta -d letta -c "\COPY block (id, label, value, description, created_at, updated_at, organization_id, is_template, read_only, version, hidden) FROM '/tmp/letta_agent_context.csv' WITH CSV HEADER"

# Step 4: Clean up temporary files
echo "Cleaning up temporary files..."
rm -f /tmp/letta_memories.csv /tmp/letta_memory_blocks.csv /tmp/letta_agent_context.csv

echo "Migration completed successfully!"

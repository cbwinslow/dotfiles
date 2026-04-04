#!/bin/bash

# Migration script using Letta CLI tools

# Step 1: Create test agent
echo "Creating test agent..."
letta create "epstein-agent" "Epstein Files Analysis Agent" "I am an agent for processing Epstein files" "letta/letta-free"

# Get the agent ID
AGENT_ID=$(letta agents | grep -o 'agent-[0-9a-f\-]*' | head -1)
echo "Using agent ID: $AGENT_ID"

# Step 2: Export and migrate letta_memories
echo "Migrating letta_memories..."
psql -d epstein -c "\COPY (SELECT memory_type || ': ' || title || ' - ' || LEFT(content, 200) AS memory, 'epstein,memories' AS tags FROM letta_memories) TO '/tmp/letta_memories.csv' WITH CSV HEADER"

# Import memories
while IFS=, read -r memory tags; do
  if [ "$memory" != "memory" ]; then
    echo "Storing memory: $memory"
    letta archival-insert "$AGENT_ID" "$memory" "$tags"
  fi
done < /tmp/letta_memories.csv

# Step 3: Export and migrate letta_memory_blocks
echo "Migrating letta_memory_blocks..."
psql -d epstein -c "\COPY (SELECT label || ': ' || LEFT(content, 200) AS memory, 'epstein,blocks' AS tags FROM letta_memory_blocks) TO '/tmp/letta_memory_blocks.csv' WITH CSV HEADER"

# Import memory blocks
while IFS=, read -r memory tags; do
  if [ "$memory" != "memory" ]; then
    echo "Storing memory block: $memory"
    letta archival-insert "$AGENT_ID" "$memory" "$tags"
  fi
done < /tmp/letta_memory_blocks.csv

# Step 4: Export and migrate letta_agent_context
echo "Migrating letta_agent_context..."
psql -d epstein -c "\COPY (SELECT agent_name || '_' || context_key || ': ' || context_value AS memory, 'epstein,context' AS tags FROM letta_agent_context) TO '/tmp/letta_agent_context.csv' WITH CSV HEADER"

# Import agent context
while IFS=, read -r memory tags; do
  if [ "$memory" != "memory" ]; then
    echo "Storing agent context: $memory"
    letta archival-insert "$AGENT_ID" "$memory" "$tags"
  fi
done < /tmp/letta_agent_context.csv

echo "Migration completed successfully!"

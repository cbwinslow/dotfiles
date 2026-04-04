# Letta Troubleshooting Guide
# Common issues and their fixes.

## 1. "database 'letta' does not exist"

**Symptom**: Docker logs show `asyncpg.exceptions.InvalidCatalogNameError: database "letta" does not exist`

**Fix**:
```bash
psql -h localhost -U cbwinslow -d postgres -c "CREATE DATABASE letta;"
psql -h localhost -U cbwinslow -d letta -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -h localhost -U cbwinslow -d letta -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
docker restart letta-server
sleep 15
```

## 2. "type 'vector' does not exist"

**Symptom**: Docker logs show `pg8000.exceptions.DatabaseError: type "vector" does not exist`

**Fix**:
```bash
psql -h localhost -U cbwinslow -d letta -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker restart letta-server
```

## 3. "500 Internal Server Error" on API calls

**Symptom**: `letta agents` returns `Error: 500 {"detail":"An unknown error occurred"}`

**Diagnosis**:
```bash
# Check if migrations completed
docker logs --tail 30 letta-server 2>&1 | grep -i "migration\|error\|failed"

# Check health
curl -s http://localhost:8283/v1/health/
```

**Fix**: Usually the database needs to be created/migrated. See fix #1.

## 4. "Handle <model> not found"

**Symptom**: `Error: 404 {"detail":"NOT_FOUND: Handle openrouter/... not found"}`

**Fix**: The model you're trying to use isn't available. List available models:
```bash
~/bin/letta models
```
Use one of the listed models when creating agents.

## 5. No agents listed

**Symptom**: `~/bin/letta agents` returns `[]`

**Fix**: Create the kilocode agent:
```bash
source ~/.bash_secrets
~/bin/letta create "kilocode" \
  "I am the KiloCode AI agent managing the CBW server." \
  "The user is cbwinslow." \
  "letta/letta-free"
```

## 6. Docker container not running

**Symptom**: `docker ps` doesn't show `letta-server`

**Fix**:
```bash
cd ~/infra/letta
bash deploy_letta.sh
```

## 7. PostgreSQL connection refused from Docker

**Symptom**: Docker logs show connection refused to PostgreSQL

**Fix**: Ensure PostgreSQL allows connections from Docker bridge:
```bash
# Check pg_hba.conf
cat /etc/postgresql/16/main/pg_hba.conf | grep "0.0.0.0"

# If missing, add:
# host all all 172.17.0.0/16 md5
sudo systemctl restart postgresql
```

## 8. Letta CLI not found

**Symptom**: `~/bin/letta: No such file or directory`

**Fix**:
```bash
# Check if wrapper exists
cat ~/bin/letta
# Should contain: exec node ~/letta-cli/index.mjs "$@"

# Check if CLI exists
ls ~/letta-cli/index.mjs

# Check if dependencies installed
cd ~/letta-cli && npm ls @letta-ai/letta-client
```

## 9. Memory search returns no results

**Symptom**: `~/bin/letta archival-search <id> "query"` returns empty

**Diagnosis**: The agent might not have archival memories yet, or embedding model isn't available.

**Fix**:
```bash
# Check if Ollama is running with embeddings
curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin).get('models',[])]"

# Store a test memory
~/bin/letta archival-insert <agent-id> "test memory entry" "test"

# List all memories (without search)
~/bin/letta archival <agent-id>
```

## 10. Skill symlinks broken

**Symptom**: Skills not appearing in KiloCode

**Fix**:
```bash
# Check symlinks
ls -la ~/.config/kilo/skills/

# Re-create broken ones
for skill in letta_memory letta_workflows cross_agent_coordinator knowledge_base; do
  ln -sf ~/dotfiles/ai/shared/skills/$skill ~/.config/kilo/skills/$skill
done
```

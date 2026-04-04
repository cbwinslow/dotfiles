# Letta Server - Complete Setup Guide
# Rebuild everything from scratch on a new server or after a crash.

## Prerequisites

- Ubuntu 24.04
- Docker + Docker Compose
- PostgreSQL 16 + pgvector extension
- Ollama (for embeddings)
- Node.js (for CLI)

## Step 1: PostgreSQL Setup

```bash
# Create the letta database
psql -h localhost -U cbwinslow -d postgres -c "CREATE DATABASE letta;"

# Enable required extensions
psql -h localhost -U cbwinslow -d letta -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -h localhost -U cbwinslow -d letta -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

## Step 2: Docker Deployment

```bash
cd ~/infra/letta

# Verify .env.letta has correct values:
cat .env.letta
# Key vars:
#   LETTA_PG_URI=postgresql://cbwinslow:123qweasd@host.docker.internal:5432/letta
#   LETTA_SERVER_PASSWORD=123qweasd
#   OLLAMA_BASE_URL=http://host.docker.internal:11434/v1

# Deploy
bash deploy_letta.sh
```

### docker-compose.letta.yml (reference)

```yaml
version: '3.8'
services:
  letta:
    image: letta/letta:latest
    container_name: letta-server
    restart: unless-stopped
    ports:
      - "8283:8283"
    env_file:
      - .env.letta
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./data:/app/data
    networks:
      - letta-net
networks:
  letta-net:
    driver: bridge
```

### .env.letta (reference)

```env
LETTA_PG_URI=postgresql://cbwinslow:123qweasd@host.docker.internal:5432/letta
LETTA_SERVER_PASSWORD=123qweasd
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
```

## Step 3: Verify Server

```bash
# Wait for migrations (first boot takes ~30s)
sleep 15

# Check health
curl -s http://localhost:8283/v1/health/
# Expected: {"version":"0.16.6","status":"ok"}

# Check Docker logs for errors
docker logs --tail 20 letta-server
# Look for: "Database migration completed successfully."
#           "Starting Letta Server..."
```

## Step 4: Install Letta CLI

```bash
# The CLI is at ~/letta-cli/index.mjs
# Wrapper script at ~/bin/letta

# Verify
~/bin/letta health
# Expected: {"version":"0.16.6","status":"ok"}
```

## Step 5: Create Agents

```bash
source ~/.bash_secrets

# Create kilocode agent
~/bin/letta create "kilocode" \
  "I am the KiloCode AI agent managing the CBW server. I handle skills, dotfiles, Docker ops, GitHub interactions, memory systems, and server administration." \
  "The user is cbwinslow, sysadmin/developer managing a Dell R720 server running Ubuntu 24.04." \
  "letta/letta-free"

# Note the agent ID from output - update in skill docs if different from:
# agent-e5e8aab5-9e87-45c1-8025-700503b524c6
```

## Step 6: Create Memory Blocks

```bash
source ~/.bash_secrets
AGENT_ID="<agent-id-from-step-5>"

# Create blocks
BLOCK1=$(~/bin/letta block create "skills-config" "KiloCode skill discovery configured. Skills.paths in ~/.config/kilo/kilo.jsonc points to ~/dotfiles/ai/skills, ~/dotfiles/ai/shared/skills, ~/dotfiles/skills." 2>&1 | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

BLOCK2=$(~/bin/letta block create "server-info" "CBW Server: Dell R720, 128GB RAM, Ubuntu 24.04. PostgreSQL 16 + pgvector 0.8. Ollama at localhost:11434. Letta server Docker v0.16.6." 2>&1 | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

BLOCK3=$(~/bin/letta block create "environment" "User: cbwinslow. Secrets in ~/.bash_secrets. Dotfiles in ~/dotfiles/. AI agent ecosystem: kilocode, opencode, gemini, claude, cline, vscode, windsurf, openclaw." 2>&1 | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Attach to agent
~/bin/letta block attach "$BLOCK1" "$AGENT_ID"
~/bin/letta block attach "$BLOCK2" "$AGENT_ID"
~/bin/letta block attach "$BLOCK3" "$AGENT_ID"
```

## Step 7: Store Initial Memories

```bash
source ~/.bash_secrets
AGENT_ID="<agent-id>"

# Store setup memory
~/bin/letta archival-insert "$AGENT_ID" \
  "$(date +%Y-%m-%d): Letta server setup complete. PostgreSQL letta database created with pgvector and pg_trgm extensions. Docker container letta-server running v0.16.6 on port 8283. KiloCode agent created. Memory blocks: skills-config, server-info, environment." \
  "setup,letta,database,infra"
```

## Step 8: Install Skills and Workflows

Skills are in `~/dotfiles/ai/shared/skills/`. If dotfiles are restored from git, they're already in place.

Verify:
```bash
# Check skill SKILL.md files exist
ls ~/dotfiles/ai/shared/skills/*/SKILL.md

# Check workflow files exist
ls ~/dotfiles/ai/shared/workflows/*.md

# Check command files exist
ls ~/dotfiles/ai/shared/commands/*.md
ls ~/.config/kilo/command/*.md
```

## Step 9: Configure KiloCode

```bash
# Verify skills.paths in kilo.jsonc
cat ~/.config/kilo/kilo.jsonc | python3 -c "import sys,jsonc; print(json.load(sys.stdin).get('skills',{}).get('paths',[]))"

# Verify symlinks
ls -la ~/.config/kilo/skills/

# Verify slash commands
ls ~/.config/kilo/command/
```

## Step 10: Update AGENTS.md

Update `~/AGENTS.md` with the current agent ID if it changed.

## Model Configuration

Available models on the Letta server:
```
letta/letta-free          # Free tier (default)
ollama/llama3.1:8b        # Local Ollama
ollama/llama3.2:latest    # Local Ollama
ollama/qwen3-coder-next:latest  # Local Ollama
```

Embedding: nomic-embed-text via Ollama (768d)

## Backup

```bash
# Export all memories from an agent
source ~/.bash_secrets
AGENT_ID="<agent-id>"
~/bin/letta archival "$AGENT_ID" > ~/infra/letta/data/archival_backup_$(date +%Y%m%d).json

# Export all blocks
~/bin/letta block list > ~/infra/letta/data/blocks_backup_$(date +%Y%m%d).json

# PostgreSQL backup
pg_dump -h localhost -U cbwinslow letta > ~/infra/letta/data/letta_db_$(date +%Y%m%d).sql
```

## Restore

```bash
# Restore PostgreSQL
psql -h localhost -U cbwinslow letta < ~/infra/letta/data/letta_db_YYYYMMDD.sql

# Restart Letta to pick up restored data
docker restart letta-server
sleep 15

# Re-create agents if needed (agents are in the DB backup)
~/bin/letta agents
```

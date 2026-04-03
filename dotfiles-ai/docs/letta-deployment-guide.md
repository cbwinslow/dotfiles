# Letta Self-Hosted Deployment with Bare-Metal PostgreSQL 16

This guide deploys Letta with a **bare-metal PostgreSQL 16** database instead of the containerized version, enabling better performance and direct database management.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agents (Cline, KiloCode, etc.)        │
│                         ↓ HTTP API                          │
├─────────────────────────────────────────────────────────────┤
│  Letta Server (Docker)                                      │
│  - Ports: 8083 (HTTP), 8283 (API)                          │
│  - Environment: LETTA_PG_URI pointing to external PG       │
│                         ↓ PostgreSQL Protocol               │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL 16 (Bare Metal)                                 │
│  - Host: localhost:5432 (or your-db-host:5432)           │
│  - Extensions: pgvector (for embeddings)                    │
│  - Database: letta                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Bare-Metal PostgreSQL 16 Setup

### 1.1 Install PostgreSQL 16

**Ubuntu/Debian:**
```bash
# Add PostgreSQL APT repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Install PostgreSQL 16
sudo apt update
sudo apt install -y postgresql-16 postgresql-16-contrib postgresql-16-pgvector

# Start and enable service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**RHEL/CentOS/Rocky:**
```bash
# Add PostgreSQL YUM repository
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# Install PostgreSQL 16
sudo dnf install -y postgresql16-server postgresql16-contrib postgresql16-pgvector

# Initialize and start
sudo /usr/pgsql-16/bin/postgresql-16-setup initdb
sudo systemctl start postgresql-16
sudo systemctl enable postgresql-16
```

**Arch Linux:**
```bash
sudo pacman -S postgresql postgresql-pgvector

# Initialize database
sudo -u postgres initdb --locale en_US.UTF-8 -D /var/lib/postgres/data
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 1.2 Configure PostgreSQL for Letta

**Create dedicated user and database:**
```bash
sudo -u postgres psql << EOF
-- Create role with secure password (change 'your_secure_password'!)
CREATE ROLE letta WITH LOGIN PASSWORD 'your_secure_password';

-- Create database owned by letta
CREATE DATABASE letta OWNER letta;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE letta TO letta;

-- Connect to letta database and enable pgvector
\c letta
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify extensions
SELECT * FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');
EOF
```

**Verify installation:**
```bash
# Check PostgreSQL version
psql --version

# Verify pgvector is available
sudo -u postgres psql -d letta -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"

# Test connection
psql -h localhost -U letta -d letta -c "SELECT version();"
```

### 1.3 Configure Network Access

**Edit `pg_hba.conf`** to allow local connections:
```bash
# Find the config file location
sudo -u postgres psql -c "SHOW hba_file;"

# Edit (path varies by distro, example for Ubuntu)
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

**Add these lines (adjust for your security needs):**
```
# Letta local connections
local   letta   letta   scram-sha-256
host    letta   letta   127.0.0.1/32    scram-sha-256
host    letta   letta   ::1/128         scram-sha-256

# If Letta runs in Docker on same host, allow docker0 interface
host    letta   letta   172.17.0.0/16   scram-sha-256
```

**Edit `postgresql.conf` for performance:**
```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

**Recommended settings for Letta:**
```ini
# Memory settings (adjust based on your RAM)
shared_buffers = 2GB                  # 25% of RAM
effective_cache_size = 6GB            # 75% of RAM
work_mem = 64MB                       # Per-query memory
maintenance_work_mem = 512MB          # For index creation

# Connection settings
max_connections = 200

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB

# Letta-specific: Allow prepared transactions for embeddings
max_prepared_transactions = 100
```

**Restart PostgreSQL:**
```bash
sudo systemctl restart postgresql

# Verify it's running
sudo systemctl status postgresql
```

### 1.4 Create Connection URL

**Format:**
```
postgresql://letta:your_secure_password@localhost:5432/letta
```

**Test connection from shell:**
```bash
export LETTA_PG_URI="postgresql://letta:your_secure_password@localhost:5432/letta"
psql "${LETTA_PG_URI}" -c "SELECT current_database(), current_user;"
```

---

## Phase 2: Letta Server Deployment

### 2.1 Create Letta Deployment Directory

```bash
mkdir -p ~/letta-deployment
cd ~/letta-deployment
```

### 2.2 Create Docker Compose Configuration

Create `compose.yaml`:

```yaml
version: '3.8'

services:
  letta_server:
    image: letta/letta:latest
    container_name: letta-server
    hostname: letta-server
    restart: unless-stopped
    ports:
      - "8083:8083"    # Web UI / ADE
      - "8283:8283"    # API
    environment:
      # Core database connection
      - LETTA_PG_URI=${LETTA_PG_URI:-postgresql://letta:letta@host.docker.internal:5432/letta}
      
      # Enable memory features
      - LETTA_DEBUG=True
      - LETTA_MEMFS_SERVICE_URL=http://localhost/memfs
      - LETTA_MEMFS_LOCAL=1
      
      # Model provider API keys (set in .env or export before running)
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - GROQ_API_KEY=${GROQ_API_KEY:-}
      - GEMINI_API_KEY=${GEMINI_API_KEY:-}
      - AZURE_API_KEY=${AZURE_API_KEY:-}
      - AZURE_BASE_URL=${AZURE_BASE_URL:-}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://host.docker.internal:11434}
      
      # Optional: Observability
      - LETTA_OTEL_EXPORTER_OTLP_ENDPOINT=${LETTA_OTEL_EXPORTER_OTLP_ENDPOINT:-}
      
    volumes:
      # Persist Letta data (if not using external DB for everything)
      - letta_data:/var/lib/letta
      
    networks:
      - letta_network
      
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8283/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  letta_data:
    driver: local

networks:
  letta_network:
    driver: bridge
```

**Note:** For Linux, use `host.docker.internal` or your host's actual IP. You may need to add:
```yaml
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

Or use network mode host if appropriate:
```yaml
    network_mode: host  # Simpler but less isolated
```

### 2.3 Create Environment File

Create `.env`:

```bash
# Database connection (REQUIRED)
# Replace 'your_secure_password' with actual password
LETTA_PG_URI=postgresql://letta:your_secure_password@host.docker.internal:5432/letta

# Model Provider API Keys (at least one required for LLM functionality)
# Free tiers available for all of these:
OPENAI_API_KEY=                    # OpenAI API (gpt-4o-mini is cheap)
ANTHROPIC_API_KEY=                  # Claude API
GROQ_API_KEY=                       # Groq (fast, cheap)
GEMINI_API_KEY=                     # Google Gemini (free tier available)

# Local LLM (optional, for fully free setup)
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Optional: Azure OpenAI
AZURE_API_KEY=
AZURE_BASE_URL=

# Optional: Observability
LETTA_OTEL_EXPORTER_OTLP_ENDPOINT=
```

**Secure the .env file:**
```bash
chmod 600 .env
```

### 2.4 Start Letta Server

```bash
# Pull latest image
docker compose pull

# Start server
docker compose up -d

# Watch logs
docker logs -f letta-server
```

**Expected startup logs:**
```
Using database: postgresql://letta:***@host.docker.internal:5432/letta
Running database migrations...
Database migration complete.
[[ Letta server // v0.x.y ]]
Server running at http://0.0.0.0:8283
ADE available at http://0.0.0.0:8083
```

### 2.5 Verify Deployment

```bash
# Check server health
curl http://localhost:8283/v1/health

# Check database connection
docker exec letta-server psql "${LETTA_PG_URI}" -c "SELECT count(*) FROM information_schema.tables;"

# View server logs
docker logs letta-server --tail 100
```

---

## Phase 3: Autonomous Memory Integration

### 3.1 Create Base Memory Agent in ADE

1. Open ADE: http://localhost:8083
2. Click "Create Agent"
3. Configure:

**System Prompt:**
```
You are a memory-enabled AI assistant with persistent long-term memory.

CORE RESPONSIBILITIES:
1. Always search your memory before answering questions about past interactions
2. Store important facts, decisions, and context in your memory blocks
3. Maintain user preferences in the 'human' memory block
4. Keep your 'persona' block updated with your role and capabilities
5. Use archival memory for searchable long-term storage

MEMORY POLICY:
- Before responding, recall relevant context from core and archival memory
- After each interaction, summarize key points for long-term storage
- Tag memories with relevant categories (project names, topics, dates)
- Update memory blocks proactively when learning user preferences

You have access to memory tools:
- memory_insert: Add new information to memory blocks
- memory_replace: Update existing memory content
- memory_rethink: Revise and improve memory organization
- Archival memory: Searchable long-term storage via vector similarity
```

**Memory Blocks:**
```yaml
persona:
  value: "I am an autonomous AI assistant with persistent memory. I help users with coding, system administration, and research tasks. I always recall relevant context before answering and store important learnings for future use."
  limit: 2000

human:
  value: "User preferences and identity will be stored here. Initial state: New user, preferences unknown."
  limit: 2000

projects:
  value: "Active projects and their status. Format: ProjectName: Description - Status - Last Updated"
  limit: 3000

knowledge:
  value: "Domain knowledge accumulated from conversations. Organized by topic."
  limit: 4000
```

**Tags:**
- `autonomous-memory`
- `git-memory-enabled`
- `base-agent`

4. Save the agent ID (e.g., `agent-abc123`) - you'll need this for configuration

### 3.2 Letta Client SDK Installation

```bash
# Install official Letta client
pip install letta-client

# Verify installation
python3 -c "from letta_client import Letta; print('Letta client installed successfully')"
```

---

## Phase 4: AI Agent Integration

### 4.1 Environment Variables for Agents

Add to `~/.env.ai` (created earlier):

```bash
# Letta Server Configuration
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_PG_URI="postgresql://letta:your_secure_password@localhost:5432/letta"

# Base Memory Agent ID (from ADE creation)
export LETTA_BASE_AGENT_ID="agent-abc123"  # Replace with your agent ID

# Default memory settings
export LETTA_AUTO_MEMORY=true
export LETTA_MEMORY_TAGS="autonomous,coding,ops"
```

### 4.2 Auto-Loading Configuration

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Letta Memory Auto-Load for AI Agents
if [ -f ~/.env.ai ]; then
    source ~/.env.ai
fi

# Auto-initialize Letta for terminal AI agents
if [[ -n "$AI_AGENT_NAME" ]] || [[ -n "$TERM_PROGRAM" ]]; then
    # Check if Letta server is healthy
    if curl -s http://localhost:8283/v1/health > /dev/null 2>&1; then
        export LETTA_AVAILABLE=true
        
        # Auto-load Letta integration module
        if [ -d ~/dotfiles/ai/packages/letta_integration ]; then
            export PYTHONPATH="${HOME}/dotfiles/ai/packages:${PYTHONPATH}"
        fi
    fi
fi
```

---

## Phase 5: Database Maintenance

### 5.1 Backup Script

Create `~/letta-deployment/backup.sh`:

```bash
#!/bin/bash
set -e

BACKUP_DIR="${HOME}/letta-backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="letta"
DB_USER="letta"

mkdir -p "${BACKUP_DIR}"

# PostgreSQL dump
echo "Creating PostgreSQL backup..."
sudo -u postgres pg_dump -Fc "${DB_NAME}" > "${BACKUP_DIR}/letta_${DATE}.dump"

# Also create plain SQL backup for readability
echo "Creating SQL backup..."
sudo -u postgres pg_dump "${DB_NAME}" > "${BACKUP_DIR}/letta_${DATE}.sql"

# Letta agent exports (optional)
if command -v python3 &> /dev/null; then
    echo "Exporting agents..."
    python3 << 'EOF'
import os
from letta_client import Letta

client = Letta(base_url=os.getenv('LETTA_SERVER_URL', 'http://localhost:8283'))
agents = client.agents.list()

for agent in agents:
    print(f"Exporting {agent.name}...")
    # Agent export logic here
EOF
fi

# Compress and cleanup old backups
cd "${BACKUP_DIR}"
tar -czf "letta_backup_${DATE}.tar.gz" "letta_${DATE}".*
rm "letta_${DATE}.dump" "letta_${DATE}.sql"

# Keep only last 10 backups
ls -t letta_backup_*.tar.gz | tail -n +11 | xargs -r rm

echo "Backup complete: ${BACKUP_DIR}/letta_backup_${DATE}.tar.gz"
```

Make executable:
```bash
chmod +x ~/letta-deployment/backup.sh
```

### 5.2 Restore Script

Create `~/letta-deployment/restore.sh`:

```bash
#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.dump>"
    exit 1
fi

BACKUP_FILE="$1"
DB_NAME="letta"
DB_USER="letta"

echo "Restoring from ${BACKUP_FILE}..."

# Stop Letta server
cd ~/letta-deployment
docker compose stop letta_server

# Drop and recreate database
echo "Recreating database..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS ${DB_NAME};
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
\c ${DB_NAME}
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF

# Restore
echo "Restoring data..."
sudo -u postgres pg_restore -d "${DB_NAME}" "${BACKUP_FILE}" || true

# Restart Letta
docker compose start letta_server

echo "Restore complete. Letta server restarting..."
```

---

## Troubleshooting

### Database Connection Issues

**Problem:** Letta can't connect to PostgreSQL

**Check:**
```bash
# Test connection from host
psql "${LETTA_PG_URI}" -c "SELECT 1"

# Test from inside Docker container
docker exec letta-server apt-get update && docker exec letta-server apt-get install -y postgresql-client
docker exec letta-server psql "${LETTA_PG_URI}" -c "SELECT 1"

# Check if pgvector is enabled
psql "${LETTA_PG_URI}" -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

**Fix:**
```bash
# If using Docker Desktop on Mac/Windows, use host.docker.internal
# If using Linux Docker, you may need the host's IP:
HOST_IP=$(ip route | grep docker0 | awk '{print $9}')
export LETTA_PG_URI="postgresql://letta:your_secure_password@${HOST_IP}:5432/letta"
```

### Migration Failures

**Problem:** Alembic migrations fail

**Fix:**
```bash
# Reset database (WARNING: DESTROYS ALL DATA)
sudo -u postgres psql << EOF
DROP DATABASE letta;
CREATE DATABASE letta OWNER letta;
\c letta
CREATE EXTENSION IF NOT EXISTS vector;
EOF

# Restart Letta to re-run migrations
docker compose restart letta_server
```

### Performance Issues

**Check database:**
```bash
# Monitor connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check table sizes
sudo -u postgres psql -d letta -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

**Optimize:**
```bash
# Vacuum and analyze
sudo -u postgres psql -d letta -c "VACUUM ANALYZE;"

# Reindex
sudo -u postgres psql -d letta -c "REINDEX DATABASE letta;"
```

---

## Security Considerations

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use strong passwords** for database user
3. **Restrict pg_hba.conf** to necessary networks only
4. **Enable SSL** for production deployments
5. **Regular backups** - Automate with cron
6. **Monitor access logs** - Enable PostgreSQL logging

---

## Next Steps

1. ✅ Deploy PostgreSQL 16 with pgvector
2. ✅ Start Letta server with external database
3. ✅ Create base memory agent in ADE
4. ✅ Configure AI agents to use Letta
5. → Create autonomous memory skills (see letta-autonomous-memory.md)
6. → Implement auto-loading for all agents

See `LETTTA_AUTONOMOUS_MEMORY.md` for the complete autonomous memory integration guide.

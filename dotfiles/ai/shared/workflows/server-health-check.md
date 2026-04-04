---
name: server-health-check
description: "Comprehensive server health check workflow. Checks Docker, PostgreSQL, Ollama, Letta, and system resources. Stores results in Letta for trend tracking."
version: "1.0.0"
triggers: [manual, scheduled, incident]
agents: [all]
---

# Server Health Check Workflow

Comprehensive health check for all services on the CBW server.

## Steps

### 1. System Resources
```bash
uptime
free -h
df -h /
nvidia-smi 2>/dev/null || echo "No GPU"
```

### 2. Docker Status
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 3. PostgreSQL
```bash
psql -h localhost -U cbwinslow -d postgres -c "SELECT version();" 2>/dev/null
psql -h localhost -U cbwinslow -d cbw_rag -c "SELECT COUNT(*) as embeddings FROM page_embeddings WHERE embedding IS NOT NULL;" 2>/dev/null
```

### 4. Letta Server
```bash
source ~/.bash_secrets
~/bin/letta health
~/bin/letta agents
```

### 5. Ollama
```bash
curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; d=json.load(sys.stdin); [print(m['name']) for m in d.get('models',[])]" 2>/dev/null
```

### 6. Store Results
```bash
source ~/.bash_secrets
~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
  "HEALTH_CHECK: $(date +%Y-%m-%dT%H:%M) | SYSTEM: <uptime, memory, disk> | DOCKER: <container count> | POSTGRES: <status> | LETTA: <status> | OLLAMA: <status>" \
  "health-check,infra"
```

## What to Report

- Any container not running
- Disk usage > 80%
- Memory usage > 90%
- PostgreSQL connection failures
- Letta server unreachable
- Ollama not responding

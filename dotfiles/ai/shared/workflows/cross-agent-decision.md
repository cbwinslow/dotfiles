---
name: cross-agent-decision
description: "Record and share important decisions across all agents via Letta. Ensures consistent knowledge and prevents conflicting actions."
version: "1.0.0"
triggers: [decision_made, config_change]
agents: [all]
---

# Cross-Agent Decision Recording Workflow

When an important decision is made, record it in Letta so all agents can reference it.

## Decision Triggers

Record a decision when:
- Changing a system configuration
- Choosing between technical alternatives
- Establishing a new pattern or convention
- Making a security-related choice
- Deciding on tool/library adoption

## Steps

1. **Format the decision**:
   ```
   DECISION: <what was decided>
   RATIONALE: <why this choice>
   ALTERNATIVES: <what else was considered>
   IMPACT: <what this affects>
   REVERSIBLE: <yes/no>
   DECIDED_BY: <agent or user>
   ```

2. **Store in Letta**:
   ```bash
   source ~/.bash_secrets
   ~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
     "DECISION: <topic> | RATIONALE: <reason> | ALTERNATIVES: <options> | IMPACT: <scope> | TIME: $(date -Iseconds)" \
     "decision,<topic>,<category>"
   ```

3. **Store as knowledge** (if it should be a permanent reference):
   ```bash
   ~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
     "KB: decision | TOPIC: <topic> | DECISION: <what> | RATIONALE: <why> | TIME: $(date -Iseconds)" \
     "kb,decision,<topic>"
   ```

## Example

```bash
source ~/.bash_secrets

# Decision: Use Nginx over Caddy for reverse proxy
~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
  "DECISION: Use Nginx as reverse proxy for all services | RATIONALE: Already installed, more mature config ecosystem, better upstream module support | ALTERNATIVES: Caddy (simpler config but fewer features), Traefik (overkill for single server) | IMPACT: All HTTP services on port 80/443 | TIME: 2026-04-02T11:00:00-04:00" \
  "decision,nginx,proxy,infra"
```

## Searching Past Decisions

```bash
# All decisions
~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "DECISION:"

# Decisions about a specific topic
~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "DECISION: nginx"

# Decisions in a category
~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "decision infra"
```

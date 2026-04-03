---
name: letta-backup
description: Backup Letta agent data and memories
---

Backup all Letta agent data. Exports core memory blocks and archival memories.

Skill path: ~/dotfiles/ai/shared/skills/memory_sync/SKILL.md

Steps:
1. List all agents: `~/bin/letta agents`
2. For each agent, list archival: `~/bin/letta archival <agent-id>`
3. List all blocks: `~/bin/letta block list`
4. Store backup record: `~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "BACKUP: $(date +%Y-%m-%d) | AGENTS: <count> | MEMORIES: <count> | BLOCKS: <count>" "backup,letta"`

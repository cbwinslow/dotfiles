---
name: letta-memory
description: Search and manage Letta memory across all agents
arguments:
  - name: query
    description: Search query for memory
    required: true
---

Search Letta archival memory for prior context on this topic.

Skill path: ~/dotfiles/ai/shared/skills/letta_memory/SKILL.md

Steps:
1. Source secrets: `source ~/.bash_secrets`
2. Search: `~/bin/letta archival-search agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "{{query}}"`
3. If results found, incorporate into your response
4. After completing the current task, store a new memory: `~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 "<summary>" "tags"`

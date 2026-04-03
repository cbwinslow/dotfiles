---
name: skill-sync
description: "Sync skill registries and ensure all agents can discover available skills. Validates SKILL.md files and updates registries."
version: "1.0.0"
triggers: [skill_added, skill_modified, manual]
agents: [all]
---

# Skill Discovery and Sync Workflow

Ensures all agents can discover and use available skills by maintaining registries and validating SKILL.md files.

## Steps

1. **Scan for SKILL.md files**:
   ```bash
   find ~/dotfiles/ai/skills ~/dotfiles/ai/shared/skills ~/dotfiles/skills -name "SKILL.md" -type f
   ```

2. **Validate each SKILL.md** has required frontmatter:
   - `name` field
   - `description` field
   - Valid YAML between `---` markers

3. **Update registry.json** at `~/dotfiles/ai/skills/registry.json`

4. **Verify symlinks** in agent config dirs:
   ```bash
   ls -la ~/.config/kilo/skills/
   ls -la ~/.kilocode/skills 2>/dev/null
   ```

5. **Store sync result** in Letta:
   ```bash
   source ~/.bash_secrets
   ~/bin/letta archival-insert agent-e5e8aab5-9e87-45c1-8025-700503b524c6 \
     "SKILL_SYNC: $(date +%Y-%m-%d) | FOUND: N skills | REGISTRY_UPDATED: yes/no | ISSUES: <any>" \
     "skills,sync"
   ```

## Skill Locations

| Location | Purpose | Discovered By |
|----------|---------|--------------|
| `~/dotfiles/ai/skills/` | Primary skills | All agents |
| `~/dotfiles/ai/shared/skills/` | Shared skills | All agents |
| `~/dotfiles/skills/` | Additional skills | All agents |
| `~/.config/kilo/command/` | KiloCode slash commands | KiloCode only |
| `~/.config/kilo/skills/` | KiloCode skill symlinks | KiloCode only |

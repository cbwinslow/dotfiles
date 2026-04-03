# Skills Management

## Description
Manage and coordinate AI agent skills, capabilities, and skill registries.

## When to Use
- Adding new skills to registry
- Discovering available skills
- Coordinating skill usage
- Updating skill documentation

## Commands

### List Skills
```bash
# List all available skills
cbw-skills --list

# Get skill info
cbw-skills --info debug

# Check skill availability
cbw-skills --check letta_memory

# Get recommendations
cbw-skills --recommend coding
```

### Skill Structure

Each skill should have:
```
skills/
└── skill_name/
    ├── SKILL.md          # Skill documentation
    └── (optional files)   # Implementation files
```

### Adding New Skills

1. Create directory
```bash
mkdir ~/dotfiles/ai/skills/my_skill
```

2. Add SKILL.md
```markdown
# My Skill

## Description
What this skill does...

## When to Use
When to apply this skill...

## Commands
How to use this skill...

## Related Skills
- related_skill_1
- related_skill_2
```

3. Update registry
```bash
# Update skills/agents.md
python3 ~/dotfiles/ai/scripts/generate_agents_md.py skills/

# Update universal registry
# Edit docs/UNIVERSAL_SKILLS_REGISTRY.md
```

## Skill Categories

### Debug & Analysis
- debug, analyze, visualize
- python-refactor, reuse, tasks

### Memory
- letta_agents, letta_memory, letta_blocks
- letta_backup, a0_memory, autonomous_memory

### Operations
- docker-ops, github, infrastructure
- system-maintenance, shell

### Development
- coding, research, knowledge
- skills, conversation_logger

### Security
- bitwarden, bitwarden_secrets

## Skill Dependencies

Some skills depend on others:
- `letta_memory` → requires `letta_agents`
- `letta_blocks` → requires `letta_agents`
- `reuse` → uses `analyze`
- `visualize` → uses `analyze`

## Best Practices

1. **Document thoroughly** - Complete SKILL.md for each skill
2. **Include examples** - Show how to use the skill
3. **List dependencies** - Note required skills/tools
4. **Keep updated** - Update when functionality changes
5. **Test regularly** - Ensure skills still work

## Related Skills
- All skills in the registry
- cbw_skills.py - Skill discovery tool

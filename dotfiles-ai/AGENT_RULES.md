# AI Agent Guidelines & Rules

## Core Principles

### 1. Always Check Directory Context First
**BEFORE starting work, read the `agents.md` file in the current directory.**

```bash
# This should be your first action
cat agents.md
```

This tells you:
- What the directory is for
- What files are key
- Common tasks and conventions
- Related directories

### 2. Follow Existing Patterns
- Match the code style already in the directory
- Use the same error handling patterns
- Follow naming conventions
- Reuse existing functions/approaches

### 3. Update agents.md When Structure Changes
If you:
- Add a new key file → Update the Key Files section
- Create a new subdirectory → Document it
- Change the purpose → Update the description

## Directory-Specific Rules

### Scripts/ (`scripts/`, `bin/`)
- **Must** use `set -euo pipefail` for bash scripts
- **Must** be executable (`chmod +x`)
- **Should** include usage examples in comments
- **Should** validate with shellcheck (bash) or pylint (python)

### Skills/ (`skills/`)
- **Must** have a `SKILL.md` file
- **Must** follow the skill template format
- **Should** include example usage
- **Must** be registered in `skills.yaml` if applicable

### Agents/ (`agents/`)
- **Must** have valid YAML configuration
- **Must** reference existing skills
- **Should** use `unified_memory` skill for RAG
- **Must** validate with `cbw-validate <file>`

### Config/ (`config/`, `configs/`)
- **Must** validate syntax before committing
- **Should** document all options
- **Must** use consistent formatting (YAML/JSON)
- **Should** include example configs

### Docs/ (`docs/`, `documentation/`)
- **Must** stay synchronized with code
- **Should** use clear headings
- **Should** include code examples
- **Must** be in Markdown format

## Code Organization Rules

### File Naming
- **Scripts:** `descriptive_name.sh` or `descriptive_name.py`
- **Configs:** `purpose.yaml` or `purpose.json`
- **Documentation:** `DESCRIPTIVE_NAME.md` (upper for important docs)
- **Tests:** `test_*.py` or `*_test.sh`

### Code Structure
- One purpose per file
- Functions should be < 50 lines
- Scripts should be < 300 lines (split if larger)
- Use imports/modules for shared code

### Comments & Documentation
- **Files:** Header comment explaining purpose
- **Functions:** Docstring explaining inputs/outputs
- **Complex logic:** Inline comments explaining why
- **TODOs:** Mark with `# TODO: description`

## Reuse Patterns

### Before Writing New Code
1. Search existing patterns: `cbw-help "what you need"`
2. Check similar scripts in the same directory
3. Look at `agents.md` for related directories
4. Reuse existing functions/modules

### Common Reusable Patterns (from your indexed data)
- **Database:** `PGPASSWORD="$PG_PASS" psql -h "$PG_HOST" ...`
- **Error handling:** `set -euo pipefail` + `trap cleanup EXIT`
- **API calls:** `curl -s -H "Content-Type: application/json" ...`
- **Python CLI:** Use `argparse` with subparsers
- **Config loading:** Use `yaml.safe_load()` or `json.load()`

## Validation Checklist

Before marking work complete:

- [ ] `agents.md` read and understood
- [ ] Code follows directory patterns
- [ ] Error handling added
- [ ] Documentation updated
- [ ] `agents.md` updated if structure changed
- [ ] Config validated (`cbw-validate` if applicable)
- [ ] Similar code searched for reuse opportunities
- [ ] Script made executable (if applicable)

## Tool Usage

### Quick Commands
```bash
# Get help for a task
cbw-help "how do I backup postgres"

# Find code patterns
cbw-pattern

# Validate configs
cbw-validate

# Get command recommendations
cbw-recommend "database task"

# Generate documentation
cbw-doc script.sh

# Generate template
cbw-template --generate postgres-backup
```

### Python Integration
```python
from unified_memory import quick_search, find_similar_code

# Search for patterns
results = quick_search("database backup")

# Find similar code
similar = find_similar_code("error handling pattern")
```

## Communication Rules

### When Asking for Clarification
- Reference the `agents.md` section you're unsure about
- Suggest specific approaches based on indexed patterns
- Explain why existing patterns don't fit (if applicable)

### When Reporting Completion
- Summarize what was done
- List files created/modified
- Note any `agents.md` updates
- Include validation results

## Error Prevention

### Common Mistakes to Avoid
1. **Not reading `agents.md`** → Always read first
2. **Inventing new patterns** → Search existing ones first
3. **Hardcoding paths** → Use environment variables
4. **No error handling** → Always add `set -euo pipefail` or try/except
5. **Not validating** → Run validators before finishing
6. **Forgetting documentation** → Update docs with code changes

### When Something Doesn't Exist
If you need a pattern that doesn't exist in the indexed data:
1. Check if it should exist (is this a new type of task?)
2. Create it following general best practices
3. Document it well so it becomes a reusable pattern
4. Consider if it should be added to `agents.md` examples

## Priority Order

When working, follow this priority:

1. **Read** `agents.md`
2. **Search** existing patterns (`cbw-help`)
3. **Validate** approach against existing code
4. **Implement** following conventions
5. **Update** `agents.md` if needed
6. **Validate** the result

---

**Remember:** The goal is consistency and reuse. When in doubt, look at what's already there.

---
description: Refactor code using analysis-driven approach
tags: [refactoring, analysis, improvement]
---

# Refactoring with Analysis Workflow

## Overview
Data-driven refactoring using cbw-analyze and cbw-reuse to identify targets and verify improvements.

## Quick Start
```bash
# 1. Analyze before refactoring
cbw-analyze --metrics > before.txt

# 2. Find reuse opportunities
cbw-reuse --report

# 3. Refactor
# ... make changes ...

# 4. Verify improvement
cbw-analyze --metrics > after.txt
diff before.txt after.txt
```

## Pre-Refactoring Phase

### 1. Establish Baseline
```bash
# Save current state
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics > refactor_baseline.txt

# Get full picture
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path . > refactor_full.txt
```

### 2. Identify Targets
Find refactoring candidates:
```bash
# Large files needing split
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics | grep "lines"

# Duplicate code
cbw-reuse --report

# High coupling
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --deps | head -10
```

### 3. Prioritize Targets
Rank by impact:
```bash
# Score each target
# Priority = Size × Complexity × Usage

# Example: Large files used by many modules
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics  # Get file sizes
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --deps     # Get dependencies
```

Priority matrix:
| Size | Dependencies | Priority | Action |
|------|--------------|----------|--------|
| >1000 | >10 | Critical | Split immediately |
| 500-1000 | 5-10 | High | Plan for next sprint |
| 300-500 | 2-5 | Medium | Address in spare time |
| <300 | <2 | Low | Monitor |

## Refactoring Phase

### Pattern 1: Extract Function
When `cbw-reuse` shows duplicate functions:

```bash
# 1. Find duplicates
cbw-reuse --duplicates

# 2. Create shared module
touch shared/utils.sh

# 3. Extract function
# Move function from file1.sh and file2.sh to shared/utils.sh

# 4. Update imports
# Add: source shared/utils.sh

# 5. Verify
python3 ~/dotfiles/ai/scripts/cbw_debug.py file1.sh
python3 ~/dotfiles/ai/scripts/cbw_debug.py file2.sh
```

### Pattern 2: Split Large File
When `cbw-analyze` shows files >500 lines:

```bash
# 1. Identify targets
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics | awk '/lines/ && $1 > 500'

# 2. Analyze structure
cbw-debug large_script.sh --flow

# 3. Plan split
# - Group related functions
# - Create modules by feature
# - Keep main script as orchestrator

# 4. Execute
# Create: large_script/feature1.sh
# Create: large_script/feature2.sh
# Update: large_script/main.sh (source new modules)

# 5. Verify
cbw-debug large_script/main.sh
cbw-debug large_script/feature1.sh
```

### Pattern 3: Improve Documentation
When comment ratio <5%:

```bash
# 1. Check current ratio
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics | grep "ratio"

# 2. Identify poorly documented files
cbw-debug script.sh  # Check for missing docstrings

# 3. Add documentation
# - Function docstrings
# - Module headers
# - Complex logic comments
# - Usage examples

# 4. Verify improvement
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics | grep "ratio"
```

### Pattern 4: Reduce Coupling
When dependencies are excessive:

```bash
# 1. Map dependencies
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --deps

# 2. Identify high-coupling modules
# Look for: imports >7, imported_by >10

# 3. Apply decoupling strategies
# - Dependency injection
# - Interface abstraction
# - Event-driven architecture
# - Mediator pattern

# 4. Verify
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --deps | grep problematic_module
```

### Pattern 5: Add Error Handling
When scripts lack proper error handling:

```bash
# 1. Check error handling
cbw-debug script.sh | grep -E "(strict_mode|trap|error)"

# 2. Add strict mode (if missing)
sed -i '2i set -euo pipefail' script.sh

# 3. Add trap (if long script)
cat >> script.sh << 'EOF'

cleanup() {
    # Cleanup code
    rm -f temp_files
}
trap cleanup EXIT
EOF

# 4. Verify
cbw-debug script.sh
```

## Verification Phase

### 1. Metrics Comparison
```bash
# Compare before/after
diff refactor_baseline.txt after_refactor.txt

# Should show:
# - Reduced file sizes
# - Increased comment ratio
# - Cleaner dependency graph
```

### 2. Functionality Check
```bash
# Run tests
./run_tests.sh

# Check specific functionality
./refactored_script.sh --test

# Verify no regressions
diff output_old.txt output_new.txt
```

### 3. Architecture Consistency
```bash
# Verify patterns still consistent
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path . | grep "Patterns"

# Check structure
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --structure
```

### 4. Documentation Update
```bash
# Update agents.md if structure changed
cbw-agents-md ~/project

# Update architecture diagrams
cbw-visualize --mermaid > docs/architecture.md
```

## Refactoring Checklist

### Before Starting
- [ ] Establish baseline metrics
- [ ] Identify all targets
- [ ] Prioritize by impact
- [ ] Plan approach for each target
- [ ] Create backup branch

### During Refactoring
- [ ] Refactor one target at a time
- [ ] Run debugger after each change
- [ ] Test functionality
- [ ] Update documentation
- [ ] Commit incremental changes

### After Refactoring
- [ ] Compare metrics (should improve)
- [ ] Run full test suite
- [ ] Update architecture docs
- [ ] Code review
- [ ] Merge to main

## Common Refactoring Scenarios

### Scenario 1: Technical Debt Cleanup
```bash
# 1. Find all debt
cbw-reuse --report > debt.txt
cbw-analyze --metrics > metrics.txt

# 2. Categorize debt
grep "duplicate" debt.txt      # Function extraction
grep "lines" metrics.txt       # File splitting
grep "ratio" metrics.txt       # Documentation

# 3. Create plan
cat > refactor_plan.md << 'EOF'
## Sprint 1: Critical
- Split files >1000 lines
- Extract duplicates used >5 times

## Sprint 2: High Priority
- Add error handling to all scripts
- Improve comment ratio to >10%

## Sprint 3: Medium
- Reduce coupling in high-dep modules
- Standardize naming conventions
EOF

# 4. Execute sprints
```

### Scenario 2: Feature Addition Preparation
```bash
# 1. Analyze current state
cbw-analyze --path .

# 2. Identify where feature fits
cbw-visualize --tree

# 3. Check if refactoring needed
# - Is there a clear location?
# - Are dependencies manageable?
# - Is architecture extensible?

# 4. Refactor if needed
# - Create extension points
# - Add interfaces
# - Reduce coupling

# 5. Add feature
# - Follow existing patterns
# - Add tests
# - Update docs

# 6. Verify
cbw-analyze --metrics
cbw-debug new_feature.sh
```

### Scenario 3: Migration Preparation
```bash
# 1. Map current architecture
cbw-visualize --mermaid > current_arch.md

# 2. Identify migration targets
# - Components to keep
# - Components to replace
# - Dependencies to break

# 3. Plan migration path
# - Phase 1: Add abstraction layer
# - Phase 2: Migrate component by component
# - Phase 3: Remove old code

# 4. Execute with verification at each phase
```

## Integration with Development Workflow

### Git Workflow
```bash
# Branch for refactoring
git checkout -b refactor/cleanup-scripts

# Incremental commits
git add script1.sh
git commit -m "refactor: extract common functions from script1"

# Push and create PR
git push origin refactor/cleanup-scripts

# Include analysis in PR description
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics > pr_metrics.txt
echo "Metrics improvement:" >> PR_DESCRIPTION.md
diff baseline.txt current.txt >> PR_DESCRIPTION.md
```

### Continuous Monitoring
```bash
# Add to CI
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics
# Fail if:
# - Comment ratio < 5%
# - Any file > 1000 lines
# - New circular dependencies
```

### Team Standards
```bash
# Shared standards document
cat > STANDARDS.md << 'EOF'
## Code Standards

### File Size
- Soft limit: 300 lines
- Hard limit: 500 lines
- Exception approval needed for >500

### Documentation
- Minimum 10% comment ratio
- All functions must have docstrings
- Complex logic requires inline comments

### Error Handling
- All scripts must use set -euo pipefail
- Functions must validate inputs
- Cleanup required for temp resources

### Dependencies
- Maximum 7 imports per module
- Prefer composition over inheritance
- Use dependency injection for testability
EOF
```

## Success Metrics

A successful refactoring shows:
- ✅ Reduced average file size
- ✅ Increased comment ratio
- ✅ Reduced duplicate code
- ✅ Cleaner dependency graph
- ✅ Same or better test coverage
- ✅ Improved architecture patterns

## Troubleshooting

### Metrics Got Worse
- Check if functionality preserved
- Verify no accidental deletions
- Ensure tests still pass
- Consider rollback and retry

### Tests Failing After Refactor
- Check for subtle behavior changes
- Verify all dependencies updated
- Run debugger on changed files
- Add missing error handling

### Architecture Patterns Changed Unexpectedly
- Review refactoring approach
- May indicate architectural shift
- Update documentation accordingly
- Verify intentional vs accidental

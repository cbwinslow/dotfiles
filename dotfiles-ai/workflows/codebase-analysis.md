---
description: Analyze codebase structure, metrics, and architecture patterns
tags: [analysis, architecture, metrics]
---

# Codebase Analysis Workflow

## Quick Start
```bash
cbw-analyze --path ~/project       # Full analysis
cbw-analyze --metrics                # Metrics only
cbw-analyze --structure              # Structure only
```

## Analysis Types

### 1. Initial Assessment
For new or unfamiliar projects:
```bash
# Full report
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path ~/project

# Focus on structure
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --structure

# Check health metrics
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics
```

Key areas to review:
- 📁 Directory structure (organization)
- 🏗️ Architectural patterns (design approach)
- 📊 Code metrics (health indicators)
- 🔗 Dependencies (coupling)

### 2. Health Check Monitoring
Track metrics over time:
```bash
# Current state
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics > metrics_$(date +%Y%m%d).txt

# Compare with previous
diff metrics_20240101.txt metrics_20240201.txt
```

Watch these metrics:
| Metric | Good | Warning | Action |
|--------|------|---------|--------|
| Comment ratio | >10% | 5-10% | Add docs |
| Max file size | <300 | 300-500 | Refactor |
| Test ratio | >1:3 | 1:5 | Add tests |
| Directory depth | <5 | >7 | Restructure |

### 3. Architecture Review
Verify patterns match intent:
```bash
# Check detected patterns
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path .

# Should see patterns like:
# ✓ CLI Tools (if building CLI)
# ✓ Library (if building library)
# ✗ MVC (if not using MVC)
```

### 4. Dependency Analysis
Understand module relationships:
```bash
# Full dependency map
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --deps

# Most connected modules (key components)
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --deps | head -20
```

## Analysis Workflow

### Step 1: Structure Overview
```bash
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --structure
```

Questions to answer:
- Is the directory structure logical?
- Are entry points clear?
- Where are configs/tests/docs?
- What's the file type distribution?

### Step 2: Metrics Baseline
```bash
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics
```

Record baseline:
```bash
# Save for comparison
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics > baseline.txt
```

### Step 3: Architecture Patterns
```bash
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path .
```

Check detected patterns:
- Do they match the project's goals?
- Are there mixed patterns?
- Is the architecture consistent?

### Step 4: Identify Hotspots
Look for areas needing attention:
```bash
# Largest files (refactoring targets)
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics | grep "lines"

# Most connected modules
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --deps | head -10
```

### Step 5: Documentation
Generate project overview:
```bash
# Save full report
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path . > PROJECT_ANALYSIS.md

# Add to README
echo "## Project Statistics" >> README.md
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics >> README.md
```

## Specific Use Cases

### Use Case 1: Project Onboarding
```bash
# 1. Clone repo
git clone <repo>
cd <repo>

# 2. Quick analysis
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --structure

# 3. Understand architecture
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path . | grep "Patterns"

# 4. Find entry points
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --structure | grep "Entry Points"

# 5. Check tests
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --structure | grep "Test files"
```

### Use Case 2: Refactoring Planning
```bash
# 1. Get current metrics
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics > before.txt

# 2. Identify targets
# - Files >500 lines
# - Low comment ratio
# - High dependency count

# 3. Plan changes
# - Split large files
# - Add documentation
# - Reduce coupling

# 4. Execute refactoring

# 5. Verify improvement
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics > after.txt
diff before.txt after.txt
```

### Use Case 3: Code Review Preparation
```bash
# 1. Analyze PR changes
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path changed_dir/

# 2. Check metrics impact
# - Comment ratio should not decrease
# - No new files >500 lines
# - Dependencies reasonable

# 3. Review architecture
# - Patterns should be consistent
# - No circular dependencies introduced
```

### Use Case 4: Technical Debt Assessment
```bash
# 1. Full analysis
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path . > debt_assessment.txt

# 2. Identify debt
# - Low comment ratio = documentation debt
# - Large files = complexity debt
# - High coupling = maintenance debt
# - Missing tests = quality debt

# 3. Prioritize
# - Critical: Files >1000 lines
# - High: Comment ratio <5%
# - Medium: Test ratio <1:5
# - Low: Directory depth >7

# 4. Create roadmap
```

## Integration

### Weekly Health Reports
```bash
#!/bin/bash
# weekly_report.sh

echo "=== Weekly Code Health Report ==="
echo "Date: $(date)"
echo ""

echo "📊 Metrics"
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics

echo ""
echo "🏗️  Architecture"
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path . | grep "Patterns"

echo ""
echo "🔗 Top Dependencies"
python3 ~/dotfiles/ai/scripts/cbw_analyze.py --deps | head -5
```

### CI/CD Integration
```yaml
# .github/workflows/analysis.yml
name: Code Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Analysis
        run: |
          python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics
          python3 ~/dotfiles/ai/scripts/cbw_analyze.py --deps
      
      - name: Check Metrics
        run: |
          # Fail if comment ratio < 5%
          RATIO=$(python3 ~/dotfiles/ai/scripts/cbw_analyze.py --metrics | grep "ratio" | awk '{print $3}')
          if (( $(echo "$RATIO < 5" | bc -l) )); then
            echo "Comment ratio too low: $RATIO%"
            exit 1
          fi
```

### IDE Integration
```json
// VS Code tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Analyze Project",
      "type": "shell",
      "command": "python3 ~/dotfiles/ai/scripts/cbw_analyze.py --path .",
      "group": "build"
    }
  ]
}
```

## Analysis Checklist

Before making changes:
- [ ] Run full analysis
- [ ] Review directory structure
- [ ] Check architecture patterns
- [ ] Note code metrics baseline
- [ ] Identify dependencies
- [ ] Find hotspots (large files, etc.)

After making changes:
- [ ] Re-run analysis
- [ ] Compare metrics
- [ ] Verify patterns still consistent
- [ ] Check no new hotspots created
- [ ] Update documentation

## Metrics Interpretation

### Comment Ratio
- **>15%**: Excellent documentation
- **10-15%**: Good documentation
- **5-10%**: Needs improvement
- **<5%**: Critical lack of docs

### File Size
- **<100 lines**: Small, focused
- **100-300 lines**: Good size
- **300-500 lines**: Getting large
- **>500 lines**: Needs splitting

### Dependency Count
- **1-3 imports**: Low coupling
- **4-7 imports**: Moderate
- **>7 imports**: High coupling, consider refactoring

## Success Criteria

A healthy codebase has:
- ✅ Clear directory structure
- ✅ Consistent architecture patterns
- ✅ Comment ratio >10%
- ✅ No files >500 lines
- ✅ Reasonable dependency graph
- ✅ Tests present

## Troubleshooting

### Analysis is Slow
- Use `--structure` or `--metrics` for specific checks
- Exclude large directories (node_modules, venv)
- Run on specific subdirectories

### Unexpected Patterns
- Patterns are heuristic-based
- Manual review may be needed
- Consider updating pattern detection

### Missing Metrics
- Ensure files are indexed
- Check file permissions
- Verify Python environment

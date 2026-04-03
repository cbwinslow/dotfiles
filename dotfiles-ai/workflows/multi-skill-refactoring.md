---
description: Multi-skill workflow for comprehensive code refactoring
tags: [refactoring, multi-skill, analyze, debug, visualize]
---

# Multi-Skill Refactoring Workflow

## Overview
This workflow chains multiple skills together for comprehensive code refactoring:
1. **analyze** - Understand codebase structure
2. **debug** - Find issues before refactoring
3. **visualize** - Document current architecture
4. **refactor** - Apply changes
5. **analyze** - Verify improvements

## Prerequisites
All skills must be available:
- analyze
- debug
- visualize
- python-refactor
- coding

## Workflow Steps

### Phase 1: Analysis (analyze skill)

```bash
# Step 1: Analyze current codebase
cbw-analyze --path ~/project --report > /tmp/refactor_analysis.txt

# Review findings
cat /tmp/refactor_analysis.txt
```

**Key metrics to capture:**
- File sizes (look for large files >300 lines)
- Comment ratios (should be >10%)
- Complexity hotspots
- Dependency chains

### Phase 2: Pre-Refactor Debugging (debug skill)

```bash
# Step 2: Debug scripts before touching them
for script in ~/project/scripts/*.sh; do
    echo "Checking: $script"
    cbw-debug "$script" >> /tmp/debug_report.txt 2>&1
done

# Review issues
grep -i "error\|warning\|critical" /tmp/debug_report.txt
```

**Fix critical issues before refactoring.**

### Phase 3: Architecture Visualization (visualize skill)

```bash
# Step 3: Document current state
cbw-visualize --path ~/project --mermaid > /tmp/current_architecture.md

# Save to project docs
cp /tmp/current_architecture.md ~/project/docs/architecture_before.md
```

**This creates a baseline for comparison.**

### Phase 4: Refactoring (coding + python-refactor skills)

#### Pattern 1: Extract Function
```python
# Before: Large function
def process_data(data):
    # 100 lines of code...
    pass

# After: Extracted functions
def validate_data(data):
    """Validate input data."""
    pass

def transform_data(data):
    """Transform data format."""
    pass

def save_data(data):
    """Save to storage."""
    pass

def process_data(data):
    """Process data through pipeline."""
    validate_data(data)
    transformed = transform_data(data)
    save_data(transformed)
```

#### Pattern 2: Split Large File
```bash
# Before: large_module.py (500 lines)
# After:
#   - large_module/
#     - __init__.py
#     - core.py
#     - utils.py
#     - constants.py
```

```python
# Use analyze skill to identify split points
cbw-analyze --path large_module.py --structure

# Split based on:
# - Function groups
# - Class hierarchies
# - Utility functions
```

#### Pattern 3: Add Type Hints
```python
# Use python-refactor skill patterns
# Before:
def process(data, config):
    return transformed

# After:
from typing import Dict, Any

def process(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Process data with configuration.
    
    Args:
        data: Input data dictionary
        config: Processing configuration
        
    Returns:
        Transformed data
    """
    return transformed
```

### Phase 5: Post-Refactor Verification

```bash
# Step 5a: Re-analyze to verify improvements
cbw-analyze --path ~/project --metrics > /tmp/post_metrics.txt

# Compare with baseline
diff /tmp/refactor_metrics.txt /tmp/post_metrics.txt

# Step 5b: Re-debug to ensure no regressions
cbw-debug ~/project/scripts/*.sh

# Step 5c: Visualize new architecture
cbw-visualize --path ~/project --mermaid > ~/project/docs/architecture_after.md
```

## Skill Chaining Examples

### Example 1: Complete Module Refactor

```bash
#!/bin/bash
# complete_refactor.sh

MODULE="auth"
PROJECT="~/myapp"

echo "=== Phase 1: Analysis ==="
cbw-analyze --path "$PROJECT/src/$MODULE" --report > "/tmp/${MODULE}_analysis.txt"

echo "=== Phase 2: Debug ==="
cbw-debug "$PROJECT/src/$MODULE"/*.py > "/tmp/${MODULE}_debug.txt"

echo "=== Phase 3: Visualize ==="
cbw-visualize --path "$PROJECT/src/$MODULE" --mermaid > "$PROJECT/docs/${MODULE}_before.md"

echo "=== Phase 4: Refactor ==="
# Manual: Apply refactoring patterns based on analysis

echo "=== Phase 5: Verify ==="
cbw-analyze --path "$PROJECT/src/$MODULE" --metrics > "/tmp/${MODULE}_post.txt"
cbw-debug "$PROJECT/src/$MODULE"/*.py

echo "=== Complete ==="
```

### Example 2: Agent-Assisted Refactor

```python
# refactor_agent.py
import subprocess
import sys

class RefactorAgent:
    """Agent that chains skills for refactoring."""
    
    def __init__(self, project_path):
        self.project = project_path
        self.findings = {}
    
    def phase1_analyze(self):
        """Analyze codebase."""
        result = subprocess.run(
            ['cbw-analyze', '--path', self.project, '--report'],
            capture_output=True, text=True
        )
        self.findings['analysis'] = result.stdout
        
        # Extract key issues
        issues = []
        for line in result.stdout.split('\n'):
            if 'lines' in line and '300' in line:
                issues.append(('large_file', line))
            if 'comment' in line and '%' in line:
                issues.append(('low_comments', line))
        
        self.findings['issues'] = issues
        return issues
    
    def phase2_debug(self):
        """Debug identified files."""
        issues = []
        for issue_type, line in self.findings['issues']:
            if issue_type == 'large_file':
                # Extract filename
                filename = line.split()[0]
                result = subprocess.run(
                    ['cbw-debug', filename],
                    capture_output=True, text=True
                )
                if 'error' in result.stdout.lower():
                    issues.append((filename, result.stdout))
        
        self.findings['debug_issues'] = issues
        return issues
    
    def phase3_plan(self):
        """Create refactoring plan."""
        plan = []
        
        for issue_type, line in self.findings['issues']:
            if issue_type == 'large_file':
                filename = line.split()[0]
                plan.append({
                    'file': filename,
                    'action': 'split_into_modules',
                    'reason': 'File exceeds 300 lines'
                })
            elif issue_type == 'low_comments':
                filename = line.split()[0]
                plan.append({
                    'file': filename,
                    'action': 'add_docstrings',
                    'reason': 'Comment ratio below 10%'
                })
        
        return plan
    
    def execute(self):
        """Execute full workflow."""
        print("=== Phase 1: Analysis ===")
        issues = self.phase1_analyze()
        print(f"Found {len(issues)} issues")
        
        print("\n=== Phase 2: Debug ===")
        debug_issues = self.phase2_debug()
        if debug_issues:
            print(f"⚠️  {len(debug_issues)} files have errors - fix first!")
            return False
        
        print("\n=== Phase 3: Planning ===")
        plan = self.phase3_plan()
        print(f"Refactoring plan ({len(plan)} items):")
        for item in plan:
            print(f"  - {item['file']}: {item['action']}")
        
        print("\n=== Ready for Phase 4: Refactoring ===")
        return True

# Usage
if __name__ == '__main__':
    agent = RefactorAgent(sys.argv[1])
    agent.execute()
```

## Success Metrics

### Before/After Comparison

```bash
# Create comparison report
cat > /tmp/refactor_comparison.md << 'EOF'
# Refactoring Report

## Metrics Comparison

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Avg file size | 450 lines | 180 lines | -60% |
| Comment ratio | 5% | 15% | +10% |
| Functions/file | 12 | 4 | -67% |
| Test coverage | 45% | 78% | +33% |

## Issues Fixed
- ❌ 3 files >500 lines → ✅ All <200 lines
- ❌ 2 circular dependencies → ✅ Resolved
- ❌ Missing type hints → ✅ 100% coverage

## Architecture
- Before: [See architecture_before.md]
- After: [See architecture_after.md]
EOF
```

## Skill Integration Points

### Where Each Skill Contributes

1. **analyze**
   - Identifies refactoring targets
   - Provides metrics baseline
   - Finds dependency issues

2. **debug**
   - Prevents breaking working code
   - Finds hidden issues
   - Validates after changes

3. **visualize**
   - Documents before state
   - Shows improvement
   - Aids communication

4. **python-refactor**
   - Provides refactoring patterns
   - Suggests improvements
   - Validates Python code

5. **coding**
   - Implements changes
   - Adds documentation
   - Reviews code quality

## Best Practices

### Do:
- ✅ Always analyze before refactoring
- ✅ Debug before touching code
- ✅ Visualize architecture changes
- ✅ Test after each phase
- ✅ Document decisions

### Don't:
- ❌ Skip analysis phase
- ❌ Refactor without tests
- ❌ Ignore debug warnings
- ❌ Change too much at once

## Troubleshooting

### Analysis Fails
```bash
# Check path exists
ls -la ~/project

# Try with absolute path
cbw-analyze --path $(realpath ~/project)
```

### Debug Shows Many Errors
```bash
# Focus on critical first
cbw-debug script.sh | grep -i "critical\|error" | head -10

# Fix incrementally
# Don't try to fix all at once
```

### Visualization Too Complex
```bash
# Focus on specific directory
cbw-visualize --path ~/project/src/core --mermaid

# Or use tree view
cbw-visualize --path ~/project --tree
```

## Related Workflows
- code-review - Review refactored code
- codebase-analysis - Deep analysis
- refactoring-with-analysis - Data-driven refactoring
- agent-lifecycle - Managing refactor agents

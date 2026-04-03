---
description: Debug and fix script issues using automated analysis
tags: [debugging, scripts, quality]
---

# Script Debugging Workflow

## Quick Start
```bash
cbw-debug script.sh              # Debug a script
cbw-debug script.sh --fixes    # Get suggested fixes
```

## Step-by-Step Debugging Process

### 1. Initial Analysis
Run the debugger on the target script:
```bash
python3 ~/dotfiles/ai/scripts/cbw_debug.py problematic.sh
```

Review the output sections:
- 📊 Overview (line count, issues, warnings)
- ❌ Issues (must fix)
- ⚠️ Warnings (should review)
- 💡 Suggestions (best practices)
- 🔧 Functions (detected functions)
- 🌐 External Tools (dependencies)

### 2. Fix Critical Issues
Address all issues first:
```bash
# Example fixes based on output
# Missing shebang:
echo '#!/bin/bash' | cat - problematic.sh > temp && mv temp problematic.sh

# Add strict mode:
sed -i '2i set -euo pipefail' problematic.sh

# Make executable:
chmod +x problematic.sh
```

### 3. Review Warnings
Check warnings and decide which to fix:
```bash
# Common warnings to fix:
# - Unquoted variables → Add quotes: "$VAR"
# - cd without check → Add: cd dir || exit 1
# - Hardcoded paths → Use variables: "$HOME/..."
# - Old backticks → Replace: $(command)
```

### 4. Verify Flow
Check control flow:
```bash
python3 ~/dotfiles/ai/scripts/cbw_debug.py problematic.sh --flow
```

Ensure:
- Functions are properly defined
- Entry points are clear
- Dependencies are available

### 5. Apply Suggested Fixes
Get automated fix suggestions:
```bash
python3 ~/dotfiles/ai/scripts/cbw_debug.py problematic.sh --fixes
```

Apply each fix:
```bash
# Example: Add error handling
cat >> problematic.sh << 'EOF'

# Error handling
trap 'echo "Error on line $LINENO"' ERR
EOF
```

### 6. Re-run Debugger
Verify all issues resolved:
```bash
python3 ~/dotfiles/ai/scripts/cbw_debug.py problematic.sh
```

Should show:
- Issues: 0
- Warnings: minimized
- No critical problems

### 7. Test Script
Execute in safe environment:
```bash
# Dry run (if supported)
bash -n problematic.sh

# Run with tracing
bash -x problematic.sh 2>&1 | head -50

# Run for real (test environment)
./problematic.sh
```

## Common Issues & Solutions

### Issue: Missing Shebang
```bash
# Fix:
echo '#!/bin/bash' | cat - script.sh > temp && mv temp script.sh
```

### Issue: No Error Handling
```bash
# Fix: Add at line 2
sed -i '2i set -euo pipefail' script.sh
```

### Issue: Unquoted Variables
```bash
# Before:
cp $SOURCE $DEST

# After:
cp "$SOURCE" "$DEST"
```

### Issue: cd Without Check
```bash
# Before:
cd /some/dir

# After:
cd /some/dir || exit 1
```

### Issue: Not Executable
```bash
chmod +x script.sh
```

## Batch Debugging
Debug multiple scripts at once:
```bash
# All shell scripts
python3 ~/dotfiles/ai/scripts/cbw_debug.py --batch *.sh

# All Python scripts
python3 ~/dotfiles/ai/scripts/cbw_debug.py --batch *.py

# Mixed
python3 ~/dotfiles/ai/scripts/cbw_debug.py --batch script1.sh script2.py
```

## Integration with Development

### Pre-commit Check
```bash
# .git/hooks/pre-commit
#!/bin/bash
for file in $(git diff --cached --name-only | grep '\.sh$'); do
    echo "Checking $file..."
    python3 ~/dotfiles/ai/scripts/cbw_debug.py "$file" || exit 1
done
```

### CI/CD Pipeline
```yaml
# .github/workflows/quality.yml
- name: Script Quality Check
  run: |
    python3 ~/dotfiles/ai/scripts/cbw_debug.py --batch scripts/*.sh
    if [ $? -ne 0 ]; then
      echo "Script issues found"
      exit 1
    fi
```

### IDE Integration
```bash
# VS Code task (tasks.json)
{
  "label": "Debug Script",
  "type": "shell",
  "command": "python3 ~/dotfiles/ai/scripts/cbw_debug.py ${file}"
}
```

## Debugging Checklist

- [ ] Run debugger on target script
- [ ] Fix all critical issues
- [ ] Review and address warnings
- [ ] Verify control flow
- [ ] Apply suggested fixes
- [ ] Re-run debugger (issues = 0)
- [ ] Test script execution
- [ ] Check with shellcheck if available

## Success Criteria

A script passes debugging when:
1. ✅ No critical issues
2. ✅ All warnings addressed or documented
3. ✅ Proper error handling in place
4. ✅ Follows best practices
5. ✅ Successfully executes

## Troubleshooting

### Debugger Won't Run
```bash
# Check Python
python3 --version

# Check script exists
ls -la ~/dotfiles/ai/scripts/cbw_debug.py

# Check permissions
chmod +x ~/dotfiles/ai/scripts/cbw_debug.py
```

### False Positives
Some warnings may not apply:
- Document why with comments
- Use `# shellcheck disable=SC####` if using shellcheck
- Note in code review

### Complex Scripts
For large/complex scripts:
1. Debug function by function
2. Use `--flow` to understand structure
3. Consider splitting into modules
4. Add comprehensive comments

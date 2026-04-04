#!/usr/bin/env python3
"""
CBW Script Debugger - Debug and analyze shell/Python scripts
"""

import os
import sys
import re
import ast
import subprocess
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import search_files_content, get_shell_files, get_python_files


class ScriptDebugger:
    """Debug and analyze scripts for common issues."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []
    
    def debug_shell_script(self, script_path: str) -> dict:
        """Debug a shell script for common issues."""
        if not os.path.exists(script_path):
            return {"error": f"File not found: {script_path}"}
        
        with open(script_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        self.issues = []
        self.warnings = []
        self.suggestions = []
        
        # Check shebang
        if not lines[0].startswith('#!'):
            self.issues.append({
                'line': 1,
                'type': 'missing_shebang',
                'message': 'Missing shebang line (#!/bin/bash)'
            })
        
        # Check for strict mode
        has_strict_mode = any('set -euo pipefail' in line for line in lines)
        if not has_strict_mode:
            self.warnings.append({
                'line': 0,
                'type': 'no_strict_mode',
                'message': 'Consider adding "set -euo pipefail" for error handling'
            })
        
        # Check for common mistakes
        for i, line in enumerate(lines, 1):
            # Variable without quotes
            if re.search(r'\$[A-Z_]+[^"]', line) and not line.strip().startswith('#'):
                if not re.search(r'\$\{[^}]+\}', line):  # Not already quoted
                    self.warnings.append({
                        'line': i,
                        'type': 'unquoted_variable',
                        'message': f'Unquoted variable: {line.strip()[:50]}'
                    })
            
            # Backticks (old style)
            if '`' in line and '$("' not in line:
                self.suggestions.append({
                    'line': i,
                    'type': 'old_backticks',
                    'message': 'Consider using $() instead of backticks'
                })
            
            # Hardcoded paths
            if re.search(r'/home/\w+/', line) and not line.strip().startswith('#'):
                self.warnings.append({
                    'line': i,
                    'type': 'hardcoded_path',
                    'message': f'Hardcoded path detected: {line.strip()[:50]}'
                })
            
            # Missing error handling for cd
            if re.match(r'^\s*cd\s+', line) and '||' not in line:
                self.warnings.append({
                    'line': i,
                    'type': 'cd_without_check',
                    'message': 'cd without error check (add "|| exit 1")'
                })
            
            # Using test with ==
            if re.search(r'\[\s+.*==', line):
                self.suggestions.append({
                    'line': i,
                    'type': 'test_with_equals',
                    'message': 'Consider using "=" instead of "==" for POSIX compatibility'
                })
            
            # Uninitialized variables
            if re.search(r'\$\{?[A-Z_]+\}?', line):
                var_name = re.search(r'\$\{?([A-Z_]+)\}?', line).group(1)
                # Check if initialized earlier
                initialized = any(f'{var_name}=' in l for l in lines[:i-1])
                if not initialized and var_name not in ['HOME', 'USER', 'PWD', 'PATH']:
                    self.warnings.append({
                        'line': i,
                        'type': 'uninitialized_var',
                        'message': f'Variable {var_name} may be uninitialized'
                    })
        
        # Check for traps
        has_trap = any('trap ' in line for line in lines)
        if not has_trap and len(lines) > 50:
            self.suggestions.append({
                'line': 0,
                'type': 'no_cleanup',
                'message': 'Consider adding trap for cleanup on long scripts'
            })
        
        # Check if executable
        if not os.access(script_path, os.X_OK):
            self.warnings.append({
                'line': 0,
                'type': 'not_executable',
                'message': f'Script is not executable (chmod +x {script_path})'
            })
        
        # Try shellcheck if available
        shellcheck_results = self._run_shellcheck(script_path)
        
        return {
            'file': script_path,
            'total_lines': len(lines),
            'issues': self.issues,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'shellcheck': shellcheck_results
        }
    
    def debug_python_script(self, script_path: str) -> dict:
        """Debug a Python script for common issues."""
        if not os.path.exists(script_path):
            return {"error": f"File not found: {script_path}"}
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        self.issues = []
        self.warnings = []
        self.suggestions = []
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {
                'error': f"Syntax error: {e}"
            }
        
        lines = content.split('\n')
        
        # Check for main guard
        has_main = any(isinstance(node, ast.If) and 
                        isinstance(node.test, ast.Compare) and
                        isinstance(node.test.left, ast.Name) and
                        node.test.left.id == '__name__'
                        for node in ast.walk(tree))
        
        if not has_main and len(lines) > 30:
            self.suggestions.append({
                'line': 0,
                'type': 'no_main_guard',
                'message': 'Consider adding if __name__ == "__main__": guard'
            })
        
        # Check for bare except
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.warnings.append({
                        'line': node.lineno,
                        'type': 'bare_except',
                        'message': 'Bare except clause - specify exception type'
                    })
        
        # Check for print statements (should use logging)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    # Check if in __main__ or function
                    self.suggestions.append({
                        'line': node.lineno,
                        'type': 'print_statement',
                        'message': 'Consider using logging instead of print'
                    })
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    self.suggestions.append({
                        'line': node.lineno,
                        'type': 'missing_docstring',
                        'message': f'Function "{node.name}" missing docstring'
                    })
        
        # Check for wildcard imports
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.names[0].name == '*':
                    self.warnings.append({
                        'line': node.lineno,
                        'type': 'wildcard_import',
                        'message': f'Wildcard import from {node.module}'
                    })
        
        # Check for mutable default arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults + node.args.kw_defaults:
                    if isinstance(default, (ast.List, ast.Dict)):
                        self.warnings.append({
                            'line': node.lineno,
                            'type': 'mutable_default',
                            'message': f'Mutable default argument in function "{node.name}"'
                        })
        
        # Run pylint if available
        pylint_results = self._run_pylint(script_path)
        
        return {
            'file': script_path,
            'total_lines': len(lines),
            'issues': self.issues,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'pylint': pylint_results
        }
    
    def _run_shellcheck(self, script_path: str) -> list:
        """Run shellcheck if available."""
        try:
            result = subprocess.run(
                ['shellcheck', '-f', 'json', script_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return []
            import json
            return json.loads(result.stdout)[:5]  # Limit to 5
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
    
    def _run_pylint(self, script_path: str) -> list:
        """Run pylint if available."""
        try:
            result = subprocess.run(
                ['pylint', '--output-format=json', script_path],
                capture_output=True,
                text=True,
                timeout=15
            )
            import json
            issues = json.loads(result.stdout)
            return [{'line': i['line'], 'message': i['message'], 'type': i['type']} 
                    for i in issues if i['type'] in ['error', 'warning']][:5]
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            return []
    
    def analyze_script_flow(self, script_path: str) -> dict:
        """Analyze the control flow of a script."""
        if not os.path.exists(script_path):
            return {"error": f"File not found: {script_path}"}
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        ext = Path(script_path).suffix
        
        flow = {
            'file': script_path,
            'functions': [],
            'entry_points': [],
            'external_calls': [],
            'dependencies': []
        }
        
        if ext in ['.sh', '.bash']:
            # Find functions
            funcs = re.findall(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)', content, re.MULTILINE)
            flow['functions'] = funcs
            
            # Find entry points (main)
            if 'main()' in content or 'if [ "${BASH_SOURCE[0]}"' in content:
                flow['entry_points'].append('main')
            
            # Find external calls
            externals = re.findall(r'\b(curl|wget|psql|docker|kubectl|python3|node|npm|git)\b', content)
            flow['external_calls'] = list(set(externals))
            
            # Find sourced files
            sourced = re.findall(r'source\s+(\S+)', content)
            flow['dependencies'] = sourced
            
        elif ext == '.py':
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        flow['functions'].append(node.name)
                        if node.name == 'main':
                            flow['entry_points'].append('main')
                    
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            flow['external_calls'].append(alias.name)
                    
                    elif isinstance(node, ast.ImportFrom):
                        flow['external_calls'].append(node.module)
            except:
                pass
        
        return flow
    
    def generate_fixes(self, script_path: str) -> list:
        """Generate suggested fixes for issues found."""
        debug_info = self.debug_shell_script(script_path)
        
        if 'error' in debug_info:
            return []
        
        fixes = []
        
        for issue in debug_info['issues'] + debug_info['warnings']:
            if issue['type'] == 'missing_shebang':
                fixes.append({
                    'line': 1,
                    'action': 'insert',
                    'content': '#!/bin/bash\n',
                    'reason': 'Add shebang for script execution'
                })
            
            elif issue['type'] == 'no_strict_mode':
                fixes.append({
                    'line': 2,
                    'action': 'insert',
                    'content': 'set -euo pipefail\n',
                    'reason': 'Add strict error handling'
                })
            
            elif issue['type'] == 'not_executable':
                fixes.append({
                    'action': 'command',
                    'command': f'chmod +x {script_path}',
                    'reason': 'Make script executable'
                })
        
        return fixes
    
    def report(self, script_path: str):
        """Generate a debug report for a script."""
        ext = Path(script_path).suffix
        
        if ext in ['.sh', '.bash']:
            debug_info = self.debug_shell_script(script_path)
        elif ext == '.py':
            debug_info = self.debug_python_script(script_path)
        else:
            print(f"Unsupported file type: {ext}")
            return
        
        if 'error' in debug_info:
            print(f"Error: {debug_info['error']}")
            return
        
        print("=" * 70)
        print(f"DEBUG REPORT: {script_path}")
        print("=" * 70)
        
        print(f"\n📊 Overview")
        print(f"  Total lines: {debug_info['total_lines']}")
        print(f"  Issues: {len(debug_info['issues'])}")
        print(f"  Warnings: {len(debug_info['warnings'])}")
        print(f"  Suggestions: {len(debug_info['suggestions'])}")
        
        if debug_info['issues']:
            print(f"\n❌ Issues (Must Fix)")
            print("-" * 70)
            for issue in debug_info['issues']:
                print(f"  Line {issue['line']}: {issue['message']}")
        
        if debug_info['warnings']:
            print(f"\n⚠️  Warnings")
            print("-" * 70)
            for warning in debug_info['warnings'][:10]:
                print(f"  Line {warning['line']}: {warning['message']}")
            if len(debug_info['warnings']) > 10:
                print(f"  ... and {len(debug_info['warnings']) - 10} more")
        
        if debug_info['suggestions']:
            print(f"\n💡 Suggestions")
            print("-" * 70)
            for sugg in debug_info['suggestions'][:5]:
                print(f"  Line {sugg['line']}: {sugg['message']}")
        
        # Show flow analysis
        flow = self.analyze_script_flow(script_path)
        if flow.get('functions'):
            print(f"\n🔧 Functions ({len(flow['functions'])})")
            print("-" * 70)
            for func in flow['functions'][:10]:
                print(f"  - {func}()")
        
        if flow.get('external_calls'):
            print(f"\n🌐 External Tools")
            print("-" * 70)
            for tool in flow['external_calls'][:10]:
                print(f"  - {tool}")
        
        # Show suggested fixes
        fixes = self.generate_fixes(script_path)
        if fixes:
            print(f"\n🔨 Suggested Fixes")
            print("-" * 70)
            for fix in fixes:
                if fix['action'] == 'command':
                    print(f"  Run: {fix['command']}")
                else:
                    print(f"  Line {fix['line']}: {fix['action']} '{fix['content']}'")
                print(f"    Reason: {fix['reason']}")
        
        print("\n" + "=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Script Debugger')
    parser.add_argument('script', nargs='?', help='Script to debug')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--flow', action='store_true', help='Show control flow')
    parser.add_argument('--fixes', action='store_true', help='Show suggested fixes')
    parser.add_argument('--batch', nargs='+', help='Debug multiple scripts')
    args = parser.parse_args()
    
    debugger = ScriptDebugger()
    
    if args.batch:
        for script in args.batch:
            if os.path.exists(script):
                print(f"\n{'='*70}")
                print(f"Analyzing: {script}")
                print('='*70)
                debugger.report(script)
    
    elif args.script:
        if args.flow:
            flow = debugger.analyze_script_flow(args.script)
            print(f"\nControl Flow: {args.script}")
            print("=" * 70)
            print(f"\nFunctions: {', '.join(flow['functions'])}")
            print(f"Entry Points: {', '.join(flow['entry_points'])}")
            print(f"External Tools: {', '.join(flow['external_calls'])}")
            print(f"Dependencies: {', '.join(flow['dependencies'])}")
        elif args.fixes:
            fixes = debugger.generate_fixes(args.script)
            print(f"\nSuggested Fixes for: {args.script}")
            print("=" * 70)
            for fix in fixes:
                print(f"\n{fix}")
        else:
            debugger.report(args.script)
    
    else:
        print("Script Debugger - Usage:")
        print("  cbw-debug script.sh           # Debug a script")
        print("  cbw-debug script.sh --flow     # Show control flow")
        print("  cbw-debug script.sh --fixes    # Show suggested fixes")
        print("  cbw-debug --batch *.sh         # Debug multiple scripts")


if __name__ == '__main__':
    main()

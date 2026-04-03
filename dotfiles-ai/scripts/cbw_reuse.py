#!/usr/bin/env python3
"""
Code Reuse Finder - Find and suggest code reuse opportunities
"""

import os
import sys
import re
from collections import defaultdict
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import search_files_content, get_python_files, get_shell_files


class CodeReuseFinder:
    """Find opportunities for code reuse and deduplication."""
    
    def __init__(self):
        self.patterns_found = defaultdict(list)
    
    def find_duplicate_functions(self) -> dict:
        """Find function definitions that appear in multiple files."""
        duplicates = {}
        
        # Find shell functions
        shell_funcs = self._find_shell_functions()
        for func_name, locations in shell_funcs.items():
            if len(locations) > 1:
                duplicates[func_name] = {
                    'type': 'shell function',
                    'count': len(locations),
                    'locations': locations
                }
        
        # Find Python functions
        python_funcs = self._find_python_functions()
        for func_name, locations in python_funcs.items():
            if len(locations) > 1:
                duplicates[func_name] = {
                    'type': 'python function',
                    'count': len(locations),
                    'locations': locations
                }
        
        return duplicates
    
    def _find_shell_functions(self) -> dict:
        """Find shell function definitions across files."""
        funcs = defaultdict(list)
        
        # Search for function patterns
        results = search_files_content(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*\(\)', 
                                       file_extensions=['.sh', '.bash'], 
                                       max_results=100)
        
        for r in results:
            text = r.get('chunk_text', '')
            matches = re.findall(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)', text, re.MULTILINE)
            for func in matches:
                # Skip common names
                if func not in ['main', 'if', 'then', 'else']:
                    funcs[func].append(r['file_path'])
        
        return dict(funcs)
    
    def _find_python_functions(self) -> dict:
        """Find Python function definitions across files."""
        funcs = defaultdict(list)
        
        results = search_files_content(r'^def [a-zA-Z_][a-zA-Z0-9_]*\(', 
                                       file_extensions=['.py'], 
                                       max_results=100)
        
        for r in results:
            text = r.get('chunk_text', '')
            matches = re.findall(r'^def ([a-zA-Z_][a-zA-Z0-9_]*)\(', text, re.MULTILINE)
            for func in matches:
                # Skip common names
                if func not in ['main', 'init', 'run']:
                    funcs[func].append(r['file_path'])
        
        return dict(funcs)
    
    def find_common_patterns(self) -> dict:
        """Find common code patterns that could be extracted."""
        patterns = {}
        
        # Error handling patterns
        error_patterns = [
            ("set -euo pipefail", "Strict error handling"),
            ("trap.*EXIT", "Cleanup trap"),
            ("|| exit 1", "Error exit"),
            ("if \[ \$\? -ne 0 \]", "Exit code check"),
        ]
        
        for pattern, desc in error_patterns:
            results = search_files_content(pattern, file_extensions=['.sh'], max_results=20)
            if len(results) > 2:
                patterns[desc] = {
                    'pattern': pattern,
                    'count': len(results),
                    'files': [r['file_path'] for r in results[:5]]
                }
        
        # API patterns
        api_patterns = [
            ("curl.*-H.*Authorization", "API auth header"),
            ("httpx.Client", "HTTPX client"),
            ("requests.get", "Requests GET"),
            ("json.loads", "JSON parsing"),
        ]
        
        for pattern, desc in api_patterns:
            results = search_files_content(pattern, max_results=20)
            if len(results) > 2:
                patterns[desc] = {
                    'pattern': pattern,
                    'count': len(results),
                    'files': [r['file_path'] for r in results[:5]]
                }
        
        # Database patterns
        db_patterns = [
            ("psql.*-c", "PostgreSQL command"),
            ("sqlite3", "SQLite command"),
            ("cursor\(\)", "DB cursor"),
        ]
        
        for pattern, desc in db_patterns:
            results = search_files_content(pattern, max_results=20)
            if len(results) > 2:
                patterns[desc] = {
                    'pattern': pattern,
                    'count': len(results),
                    'files': [r['file_path'] for r in results[:5]]
                }
        
        return patterns
    
    def suggest_refactors(self) -> list:
        """Suggest specific refactoring opportunities."""
        suggestions = []
        
        # Find duplicate functions
        dups = self.find_duplicate_functions()
        for func_name, info in dups.items():
            if info['count'] >= 3:
                suggestions.append({
                    'type': 'extract_function',
                    'priority': 'high',
                    'description': f"Extract '{func_name}' to shared module",
                    'details': f"Found in {info['count']} files",
                    'locations': info['locations']
                })
        
        # Find common initialization patterns
        init_patterns = self.find_common_patterns()
        for name, info in init_patterns.items():
            if info['count'] >= 5:
                suggestions.append({
                    'type': 'extract_module',
                    'priority': 'medium',
                    'description': f"Create shared '{name}' utility",
                    'details': f"Used {info['count']} times",
                    'files': info['files']
                })
        
        return sorted(suggestions, key=lambda x: (0 if x['priority'] == 'high' else 1, -x.get('count', 0)))
    
    def find_similar_scripts(self, script_path: str) -> list:
        """Find scripts similar to a given one."""
        if not os.path.exists(script_path):
            return []
        
        # Read the script
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Extract key patterns
        patterns = []
        
        # Find command usage
        commands = re.findall(r'\b(curl|docker|psql|kubectl|python3|node|npm)\b', content)
        for cmd in set(commands):
            patterns.append(cmd)
        
        # Find function names
        funcs = re.findall(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)', content, re.MULTILINE)
        for func in set(funcs)[:3]:
            patterns.append(func)
        
        # Search for similar
        similar = []
        for pattern in patterns:
            results = search_files_content(pattern, 
                                           file_extensions=['.sh', '.py'], 
                                           max_results=10)
            for r in results:
                if r['file_path'] != script_path:
                    similar.append({
                        'file': r['file_path'],
                        'shared_pattern': pattern,
                        'similarity': 'high' if pattern in commands else 'medium'
                    })
        
        # Deduplicate
        seen = set()
        unique = []
        for s in similar:
            if s['file'] not in seen:
                seen.add(s['file'])
                unique.append(s)
        
        return unique[:10]
    
    def generate_library_suggestions(self) -> list:
        """Suggest libraries/modules to create based on patterns."""
        suggestions = []
        
        # Check for database patterns
        db_results = search_files_content("psql", file_extensions=['.sh'], max_results=10)
        if len(db_results) >= 3:
            suggestions.append({
                'name': 'db_utils.sh',
                'purpose': 'Database connection and query helpers',
                'functions': ['db_query()', 'db_backup()', 'db_connect()'],
                'usage_count': len(db_results),
                'files': [r['file_path'] for r in db_results[:5]]
            })
        
        # Check for API patterns
        api_results = search_files_content("curl", file_extensions=['.sh'], max_results=10)
        if len(api_results) >= 3:
            suggestions.append({
                'name': 'api_client.sh',
                'purpose': 'API request helpers',
                'functions': ['api_get()', 'api_post()', 'api_auth()'],
                'usage_count': len(api_results),
                'files': [r['file_path'] for r in api_results[:5]]
            })
        
        # Check for logging patterns
        log_results = search_files_content(r'echo.*\[.*\]', file_extensions=['.sh'], max_results=10)
        if len(log_results) >= 3:
            suggestions.append({
                'name': 'logging.sh',
                'purpose': 'Consistent logging functions',
                'functions': ['log_info()', 'log_error()', 'log_debug()'],
                'usage_count': len(log_results),
                'files': [r['file_path'] for r in log_results[:5]]
            })
        
        return suggestions
    
    def report(self):
        """Generate a full reuse report."""
        print("=" * 70)
        print("CODE REUSE & REFACTORING OPPORTUNITIES")
        print("=" * 70)
        
        # Duplicate functions
        dups = self.find_duplicate_functions()
        if dups:
            print("\n📋 DUPLICATE FUNCTIONS")
            print("-" * 70)
            for func_name, info in sorted(dups.items(), key=lambda x: -x[1]['count']):
                print(f"\n  {func_name}() - {info['type']}")
                print(f"  Found in {info['count']} files:")
                for loc in info['locations'][:5]:
                    print(f"    - {loc}")
                if len(info['locations']) > 5:
                    print(f"    ... and {len(info['locations']) - 5} more")
        
        # Common patterns
        patterns = self.find_common_patterns()
        if patterns:
            print("\n🔁 COMMON PATTERNS (Consider Extracting)")
            print("-" * 70)
            for name, info in sorted(patterns.items(), key=lambda x: -x[1]['count']):
                print(f"\n  {name}")
                print(f"  Pattern: {info['pattern']}")
                print(f"  Used {info['count']} times")
        
        # Refactoring suggestions
        refactors = self.suggest_refactors()
        if refactors:
            print("\n🔧 REFACTORING SUGGESTIONS")
            print("-" * 70)
            for sugg in refactors[:10]:
                priority_icon = "🔴" if sugg['priority'] == 'high' else "🟡"
                print(f"\n  {priority_icon} {sugg['description']}")
                print(f"     {sugg['details']}")
        
        # Library suggestions
        libs = self.generate_library_suggestions()
        if libs:
            print("\n📚 SUGGESTED LIBRARIES TO CREATE")
            print("-" * 70)
            for lib in libs:
                print(f"\n  {lib['name']}")
                print(f"  Purpose: {lib['purpose']}")
                print(f"  Functions: {', '.join(lib['functions'])}")
                print(f"  Used in {lib['usage_count']} files")
        
        print("\n" + "=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Find code reuse opportunities')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--similar-to', type=str, help='Find scripts similar to given file')
    parser.add_argument('--duplicates', action='store_true', help='Show only duplicates')
    parser.add_argument('--suggest-libs', action='store_true', help='Suggest libraries to create')
    args = parser.parse_args()
    
    finder = CodeReuseFinder()
    
    if args.report:
        finder.report()
    
    elif args.similar_to:
        similar = finder.find_similar_scripts(args.similar_to)
        print(f"\n📂 Scripts similar to: {args.similar_to}")
        print("=" * 70)
        for s in similar:
            print(f"\n  {s['file']}")
            print(f"  Shared pattern: {s['shared_pattern']} ({s['similarity']} similarity)")
    
    elif args.duplicates:
        dups = finder.find_duplicate_functions()
        print("\n📋 Duplicate Functions")
        print("=" * 70)
        for func_name, info in sorted(dups.items(), key=lambda x: -x[1]['count']):
            print(f"\n  {func_name}() - in {info['count']} files")
    
    elif args.suggest_libs:
        libs = finder.generate_library_suggestions()
        print("\n📚 Suggested Libraries")
        print("=" * 70)
        for lib in libs:
            print(f"\n  {lib['name']}")
            print(f"  Purpose: {lib['purpose']}")
            print(f"  Functions: {', '.join(lib['functions'])}")
    
    else:
        finder.report()


if __name__ == '__main__':
    main()

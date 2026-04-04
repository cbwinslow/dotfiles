#!/usr/bin/env python3
"""
Script Pattern Analyzer - Extract reusable patterns from indexed shell scripts
Uses CBW RAG to find common patterns, functions, and best practices
"""

import os
import sys
import re
import subprocess
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import _get_db, find_similar_code, search_files_content


class ScriptPatternAnalyzer:
    """Analyze shell scripts for patterns and improvements."""
    
    def __init__(self):
        self.db = _get_db()
        
    def find_common_functions(self) -> dict:
        """Find commonly defined functions across scripts."""
        # Query for function definitions
        results = search_files_content(
            "^[a-zA-Z_][a-zA-Z0-9_]*\\s*\\(\\)\\s*\\{",
            file_extensions=['.sh', '.bash'],
            max_results=50
        )
        
        functions = {}
        for r in results:
            text = r.get('chunk_text', '')
            # Extract function names
            matches = re.findall(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)', text, re.MULTILINE)
            for func in matches:
                if func not in functions:
                    functions[func] = []
                functions[func].append(r['file_path'])
        
        return functions
    
    def find_error_handling_patterns(self) -> list:
        """Find error handling patterns in scripts."""
        patterns = [
            ("set -euo pipefail", "Strict mode"),
            ("trap \"", "Signal handling"),
            ("if \[ \$\? -ne 0 \]", "Exit code check"),
            ("|| { echo", "Error with message"),
            ("2>&1", "stderr redirect"),
        ]
        
        found = []
        for pattern, desc in patterns:
            results = search_files_content(
                pattern,
                file_extensions=['.sh', '.bash'],
                max_results=20
            )
            if results:
                found.append({
                    'pattern': pattern,
                    'description': desc,
                    'count': len(results),
                    'examples': [r['file_path'] for r in results[:3]]
                })
        
        return found
    
    def find_script_templates(self) -> list:
        """Find script templates and boilerplate patterns."""
        templates = []
        
        # Find shebang patterns
        with self.db.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT 
                    split_part(chunk_text, E'\n', 1) as shebang,
                    COUNT(*) as count
                FROM file_chunks fc
                JOIN files f ON fc.file_id = f.id
                WHERE f.file_extension IN ('.sh', '.bash')
                AND f.is_deleted = FALSE
                AND chunk_text LIKE '#!/%%'
                GROUP BY split_part(chunk_text, E'\n', 1)
                ORDER BY count DESC
                LIMIT 10
            """)
            for row in cur.fetchall():
                templates.append({
                    'type': 'shebang',
                    'pattern': row[0],
                    'count': row[1]
                })
        
        return templates
    
    def find_db_connection_patterns(self) -> list:
        """Find database connection patterns."""
        patterns = [
            "psql",
            "CBW_RAG_DATABASE",
            "postgresql://",
            "sqlite3",
        ]
        
        found = []
        for pattern in patterns:
            results = search_files_content(pattern, max_results=10)
            if results:
                found.append({
                    'pattern': pattern,
                    'files': [r['file_path'] for r in results[:5]],
                    'count': len(results)
                })
        
        return found
    
    def find_api_call_patterns(self) -> list:
        """Find API call patterns (curl, httpx, requests)."""
        patterns = [
            ("curl -", "Curl commands"),
            ("httpx.Client", "HTTPX client"),
            ("requests.get", "Requests"),
            ("POST http", "HTTP POST"),
        ]
        
        found = []
        for pattern, desc in patterns:
            results = search_files_content(pattern, max_results=10)
            if results:
                found.append({
                    'pattern': pattern,
                    'description': desc,
                    'count': len(results)
                })
        
        return found
    
    def generate_script_improvements(self, script_path: str) -> dict:
        """Analyze a script and suggest improvements based on indexed patterns."""
        if not os.path.exists(script_path):
            return {"error": f"Script not found: {script_path}"}
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        suggestions = {
            'missing_strict_mode': 'set -euo pipefail' not in content,
            'no_shebang': not content.startswith('#!'),
            'no_error_handling': '||' not in content and 'if [ $? ' not in content,
            'hardcoded_paths': len(re.findall(r'/home/\w+/', content)) > 0,
            'no_trap': 'trap ' not in content,
            'missing_functions': [],
        }
        
        # Find similar scripts for reference
        similar = search_files_content(
            os.path.basename(script_path).replace('.sh', ''),
            file_extensions=['.sh'],
            max_results=5
        )
        suggestions['similar_scripts'] = [s['file_path'] for s in similar]
        
        return suggestions
    
    def report(self):
        """Generate a full analysis report."""
        print("=" * 70)
        print("SCRIPT PATTERN ANALYZER REPORT")
        print("=" * 70)
        
        # Error handling patterns
        print("\n📋 ERROR HANDLING PATTERNS")
        print("-" * 40)
        patterns = self.find_error_handling_patterns()
        for p in patterns:
            print(f"  {p['description']}: {p['count']} occurrences")
            for ex in p['examples'][:2]:
                print(f"    - {ex}")
        
        # API patterns
        print("\n🌐 API CALL PATTERNS")
        print("-" * 40)
        api_patterns = self.find_api_call_patterns()
        for p in api_patterns:
            print(f"  {p['description']}: {p['count']} occurrences")
        
        # DB patterns
        print("\n🗄️  DATABASE PATTERNS")
        print("-" * 40)
        db_patterns = self.find_db_connection_patterns()
        for p in db_patterns:
            print(f"  {p['pattern']}: {p['count']} files")
        
        # Functions
        print("\n🔧 COMMON FUNCTIONS")
        print("-" * 40)
        funcs = self.find_common_functions()
        for func, files in sorted(funcs.items(), key=lambda x: -len(x[1]))[:10]:
            if len(files) > 1:
                print(f"  {func}(): used in {len(files)} files")
        
        print("\n" + "=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Analyze shell script patterns')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--analyze', type=str, help='Analyze specific script')
    parser.add_argument('--find-pattern', type=str, help='Find specific pattern')
    args = parser.parse_args()
    
    analyzer = ScriptPatternAnalyzer()
    
    if args.report:
        analyzer.report()
    elif args.analyze:
        suggestions = analyzer.generate_script_improvements(args.analyze)
        print(f"\n📊 Analysis for: {args.analyze}")
        print("-" * 40)
        for key, value in suggestions.items():
            if isinstance(value, bool) and value:
                print(f"  ⚠️  {key.replace('_', ' ')}")
            elif key == 'similar_scripts' and value:
                print(f"\n  📚 Similar scripts:")
                for s in value:
                    print(f"      - {s}")
    elif args.find_pattern:
        results = search_files_content(args.find_pattern, max_results=20)
        print(f"\n🔍 Pattern '{args.find_pattern}' found in {len(results)} files:")
        for r in results[:10]:
            print(f"  - {r['file_path']}")
    else:
        analyzer.report()


if __name__ == '__main__':
    main()

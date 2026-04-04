#!/usr/bin/env python3
"""
Auto Documenter - Generate documentation from shell scripts
Uses RAG to understand script functionality and generate markdown docs
"""

import os
import sys
import re
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import search_files_content, get_shell_files


class AutoDocumenter:
    """Automatically generate documentation for scripts."""
    
    def __init__(self):
        self.doc_patterns = self._load_doc_patterns()
    
    def _load_doc_patterns(self) -> dict:
        """Load documentation patterns from indexed files."""
        patterns = {
            'usage_headers': ['Usage:', 'Examples:', '## Usage'],
            'param_patterns': ['Args:', 'Parameters:', '- `--'],
        }
        return patterns
    
    def analyze_script(self, script_path: str) -> dict:
        """Analyze a script and extract information."""
        if not os.path.exists(script_path):
            return {"error": "File not found"}
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        analysis = {
            'path': script_path,
            'shebang': None,
            'description': None,
            'functions': [],
            'variables': [],
            'dependencies': [],
            'usage_examples': [],
        }
        
        # Extract shebang
        lines = content.split('\n')
        if lines and lines[0].startswith('#!'):
            analysis['shebang'] = lines[0]
        
        # Extract description from comments
        for line in lines[:20]:
            if line.startswith('#') and not line.startswith('#!'):
                text = line[1:].strip()
                if len(text) > 10 and not text.startswith('-'):
                    analysis['description'] = text
                    break
        
        # Extract functions
        func_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)'
        for line in lines:
            match = re.match(func_pattern, line.strip())
            if match:
                analysis['functions'].append(match.group(1))
        
        # Extract variables (environment)
        var_pattern = r'\$\{?([A-Z_][A-Z0-9_]*)\}?'
        vars_found = set(re.findall(var_pattern, content))
        analysis['variables'] = sorted(vars_found)[:20]
        
        # Find dependencies
        deps = []
        common_deps = ['curl', 'jq', 'psql', 'docker', 'kubectl', 'python3', 'node']
        for dep in common_deps:
            if re.search(rf'\b{dep}\b', content):
                deps.append(dep)
        analysis['dependencies'] = deps
        
        # Find usage examples in comments
        for i, line in enumerate(lines):
            if 'Example' in line or line.strip().startswith('# $') or line.strip().startswith('# ./'):
                example = line[1:].strip() if line.startswith('#') else line
                if len(example) > 5:
                    analysis['usage_examples'].append(example)
        
        return analysis
    
    def generate_markdown(self, script_path: str) -> str:
        """Generate markdown documentation for a script."""
        analysis = self.analyze_script(script_path)
        
        if 'error' in analysis:
            return f"# Error\n\n{analysis['error']}"
        
        name = os.path.basename(script_path)
        
        md = []
        md.append(f"# {name}")
        md.append("")
        
        if analysis['description']:
            md.append(analysis['description'])
            md.append("")
        
        md.append(f"**Path:** `{script_path}`")
        md.append("")
        
        if analysis['shebang']:
            md.append(f"**Shebang:** `{analysis['shebang']}`")
            md.append("")
        
        # Dependencies
        if analysis['dependencies']:
            md.append("## Dependencies")
            md.append("")
            for dep in analysis['dependencies']:
                md.append(f"- {dep}")
            md.append("")
        
        # Functions
        if analysis['functions']:
            md.append("## Functions")
            md.append("")
            for func in analysis['functions']:
                md.append(f"### `{func}()`")
                md.append("")
                # Try to find function documentation
                md.append(f"User-defined function.")
                md.append("")
        
        # Environment Variables
        if analysis['variables']:
            md.append("## Environment Variables")
            md.append("")
            for var in analysis['variables'][:15]:
                md.append(f"- `${var}`")
            md.append("")
        
        # Usage Examples
        if analysis['usage_examples']:
            md.append("## Usage Examples")
            md.append("")
            for ex in analysis['usage_examples'][:5]:
                md.append(f"```bash")
                md.append(ex)
                md.append("```")
                md.append("")
        
        # Find similar scripts via RAG
        similar = self._find_similar_scripts(name)
        if similar:
            md.append("## Similar Scripts")
            md.append("")
            for s in similar[:5]:
                md.append(f"- `{s}`")
            md.append("")
        
        md.append("---")
        md.append("*Auto-generated by cbw-doc*")
        
        return '\n'.join(md)
    
    def _find_similar_scripts(self, script_name: str) -> list:
        """Find similar scripts using RAG."""
        base_name = script_name.replace('.sh', '').replace('.bash', '')
        results = search_files_content(base_name, file_extensions=['.sh'], max_results=10)
        
        similar = []
        for r in results:
            path = r.get('file_path', '')
            if path != script_name and path not in similar:
                similar.append(path)
        
        return similar
    
    def generate_index(self, output_path: str = None) -> str:
        """Generate an index of all documented scripts."""
        scripts = get_shell_files(limit=100)
        
        md = []
        md.append("# Shell Scripts Index")
        md.append("")
        md.append(f"*Generated from {len(scripts)} indexed scripts*")
        md.append("")
        
        # Group by directory
        by_dir = {}
        for s in scripts:
            path = s['file_path']
            dir_name = os.path.dirname(path)
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(s)
        
        for dir_name, files in sorted(by_dir.items()):
            md.append(f"## {dir_name}")
            md.append("")
            for f in files[:10]:
                md.append(f"- [{f['file_name']}]({f['file_path']})")
            md.append("")
        
        index_content = '\n'.join(md)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(index_content)
            print(f"Index written to: {output_path}")
        
        return index_content


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Auto Documenter for Shell Scripts')
    parser.add_argument('--doc', type=str, help='Generate docs for specific script')
    parser.add_argument('--output', type=str, help='Output file for generated docs')
    parser.add_argument('--index', action='store_true', help='Generate scripts index')
    parser.add_argument('--index-output', type=str, help='Output path for index')
    args = parser.parse_args()
    
    docgen = AutoDocumenter()
    
    if args.doc:
        markdown = docgen.generate_markdown(args.doc)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(markdown)
            print(f"Documentation written to: {args.output}")
        else:
            print(markdown)
    
    elif args.index:
        docgen.generate_index(args.index_output)
    
    else:
        print("Auto Documenter - Usage:")
        print("  cbw-doc --doc <script.sh> [--output docs.md]")
        print("  cbw-doc --index [--index-output SCRIPTS.md]")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Directory Dependency Mapper - Map dependencies between directories
"""

import os
import sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import search_files_content, get_python_files, get_shell_files


class DependencyMapper:
    """Map dependencies and relationships between directories."""
    
    def __init__(self, base_path='~/dotfiles'):
        self.base_path = Path(base_path).expanduser()
        self.dependencies = defaultdict(lambda: {'imports': set(), 'used_by': set(), 'tools': set()})
    
    def map_python_dependencies(self):
    """Map Python import dependencies."""
        files = get_python_files(limit=100)
        
        for f in files:
            path = f['file_path']
            dir_name = os.path.dirname(path)
            
            # Search for imports in this file
            results = search_files_content(r'^from|^import', 
                                          file_extensions=['.py'], 
                                          max_results=50)
            
            for r in results:
                if r['file_path'] == path:
                    text = r.get('chunk_text', '')
                    lines = text.split('\n')
                    
                    for line in lines:
                        # Parse imports
                        if line.startswith('from') or line.startswith('import'):
                            # Extract module name
                            parts = line.split()
                            if len(parts) >= 2:
                                module = parts[1].split('.')[0]
                                if module not in ['os', 'sys', 'json', 're', 'time', 'datetime', 'argparse']:
                                    self.dependencies[dir_name]['imports'].add(module)
    
    def map_shell_dependencies(self):
        """Map shell script dependencies."""
        files = get_shell_files(limit=100)
        
        for f in files:
            path = f['file_path']
            dir_name = os.path.dirname(path)
            
            # Search for source commands
            results = search_files_content(r'source.*\.sh', 
                                          file_extensions=['.sh'], 
                                          max_results=50)
            
            for r in results:
                if r['file_path'] == path:
                    text = r.get('chunk_text', '')
                    # Extract sourced files
                    import re
                    sourced = re.findall(r'source\s+([^\s]+\.sh)', text)
                    for s in sourced:
                        self.dependencies[dir_name]['imports'].add(s)
            
            # Check for tool usage
            tools = ['docker', 'kubectl', 'psql', 'curl', 'python3', 'node', 'npm']
            for tool in tools:
                results = search_files_content(rf'\b{tool}\b', 
                                              file_extensions=['.sh'], 
                                              max_results=5)
                for r in results:
                    if r['file_path'] == path:
                        self.dependencies[dir_name]['tools'].add(tool)
    
    def find_cross_references(self):
        """Find cross-references between directories."""
        # Map which directories reference which
        for dir_name, info in self.dependencies.items():
            for imp in info['imports']:
                # Find which directory provides this import
                for other_dir, other_info in self.dependencies.items():
                    if other_dir != dir_name:
                        if any(imp in f for f in os.listdir(other_dir) if os.path.isfile(os.path.join(other_dir, f))):
                            self.dependencies[dir_name]['used_by'].add(other_dir)
    
    def generate_map(self):
        """Generate the full dependency map."""
        self.map_python_dependencies()
        self.map_shell_dependencies()
        self.find_cross_references()
        
        return dict(self.dependencies)
    
    def visualize_dependencies(self):
        """Generate a text visualization of dependencies."""
        deps = self.generate_map()
        
        print("=" * 70)
        print("DIRECTORY DEPENDENCY MAP")
        print("=" * 70)
        
        # Top-level directories only
        top_dirs = [d for d in deps.keys() if str(d).count('/') <= 4]
        
        for dir_path in sorted(top_dirs):
            info = deps[dir_path]
            dir_name = os.path.basename(dir_path)
            
            print(f"\n📁 {dir_name}/")
            print(f"   Path: {dir_path}")
            
            if info['imports']:
                print(f"   Imports from: {', '.join(info['imports'])}")
            
            if info['tools']:
                print(f"   Tools used: {', '.join(info['tools'])}")
            
            if info['used_by']:
                print(f"   Referenced by: {len(info['used_by'])} directories")
    
    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram syntax."""
        deps = self.generate_map()
        
        lines = ["```mermaid", "graph TD"]
        
        # Create nodes
        nodes = {}
        for i, dir_path in enumerate(deps.keys()):
            node_id = f"dir{i}"
            nodes[dir_path] = node_id
            dir_name = os.path.basename(dir_path)
            lines.append(f"    {node_id}[{dir_name}]")
        
        # Create edges
        for dir_path, info in deps.items():
            for imp in info['imports']:
                # Find target node
                for target_path, target_id in nodes.items():
                    if imp in target_path or target_path in imp:
                        lines.append(f"    {nodes[dir_path]} --> {target_id}")
        
        lines.append("```")
        return '\n'.join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Directory Dependency Mapper')
    parser.add_argument('--visualize', action='store_true', help='Show dependency visualization')
    parser.add_argument('--mermaid', action='store_true', help='Generate Mermaid diagram')
    parser.add_argument('--base', type=str, default='~/dotfiles', help='Base path')
    args = parser.parse_args()
    
    mapper = DependencyMapper(args.base)
    
    if args.mermaid:
        print(mapper.generate_mermaid())
    elif args.visualize:
        mapper.visualize_dependencies()
    else:
        mapper.visualize_dependencies()


if __name__ == '__main__':
    main()

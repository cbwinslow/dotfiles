#!/usr/bin/env python3
"""
Code Structure Analyzer - High-level architecture analysis
"""

import os
import sys
import re
import ast
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import (
    search_files_content, 
    get_python_files, 
    get_shell_files,
    get_system_stats
)


class StructureAnalyzer:
    """Analyze high-level code structure and architecture."""
    
    def __init__(self, base_path='~/dotfiles'):
        self.base_path = Path(base_path).expanduser()
        self.modules = defaultdict(dict)
        self.dependencies = defaultdict(set)
        self.architecture = {}
    
    def analyze_directory_structure(self, path: str = None) -> dict:
        """Analyze the overall directory structure."""
        if not path:
            path = self.base_path
        
        path = Path(path)
        
        structure = {
            'root': str(path),
            'total_dirs': 0,
            'total_files': 0,
            'by_type': defaultdict(int),
            'depth_distribution': defaultdict(int),
            'entry_points': [],
            'config_files': [],
            'test_files': []
        }
        
        for root, dirs, files in os.walk(path):
            # Skip hidden and special directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.config', '.github']]
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'node_modules', 'venv', '.venv']]
            
            rel_path = Path(root).relative_to(path)
            depth = len(rel_path.parts)
            
            structure['total_dirs'] += len(dirs)
            structure['total_files'] += len(files)
            structure['depth_distribution'][depth] += len(files)
            
            for f in files:
                ext = Path(f).suffix.lower()
                structure['by_type'][ext if ext else 'no_extension'] += 1
                
                # Identify entry points
                if f in ['main.py', 'index.js', 'app.py', 'server.py', 'cli.py']:
                    structure['entry_points'].append(os.path.join(root, f))
                
                # Identify config files
                if f in ['config.yaml', 'config.json', '.env', 'setup.py', 'pyproject.toml']:
                    structure['config_files'].append(os.path.join(root, f))
                
                # Identify test files
                if f.startswith('test_') or f.endswith('_test.py') or f.endswith('.spec.js'):
                    structure['test_files'].append(os.path.join(root, f))
        
        return dict(structure)
    
    def analyze_module_dependencies(self) -> dict:
        """Analyze Python module dependencies."""
        deps = defaultdict(lambda: {'imports': set(), 'imported_by': set()})
        
        python_files = get_python_files(limit=100)
        
        for f in python_files:
            path = f['file_path']
            module_name = self._path_to_module(path)
            
            # Read file and parse imports
            try:
                with open(path, 'r') as file:
                    content = file.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            deps[module_name]['imports'].add(alias.name)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            deps[module_name]['imports'].add(node.module)
                            deps[node.module]['imported_by'].add(module_name)
            except:
                pass
        
        return {k: {'imports': list(v['imports']), 
                    'imported_by': list(v['imported_by'])} 
                for k, v in deps.items()}
    
    def _path_to_module(self, path: str) -> str:
        """Convert file path to module name."""
        rel_path = Path(path).relative_to(self.base_path)
        parts = list(rel_path.parts)
        
        # Remove .py extension
        if parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]
        
        return '.'.join(parts)
    
    def find_architecture_patterns(self) -> dict:
        """Identify architectural patterns in the codebase."""
        patterns = {
            'mvc': False,
            'layered': False,
            'microservices': False,
            'plugin_based': False,
            'cli_tools': False,
            'library': False
        }
        
        # Check for MVC
        has_models = any('model' in d.lower() for d in self._get_dirs())
        has_views = any('view' in d.lower() for d in self._get_dirs())
        has_controllers = any('controller' in d.lower() for d in self._get_dirs())
        if has_models and (has_views or has_controllers):
            patterns['mvc'] = True
        
        # Check for CLI tools
        scripts = get_shell_files(limit=50)
        if len(scripts) > 5:
            patterns['cli_tools'] = True
        
        # Check for plugin architecture
        if any('plugin' in d.lower() or 'extension' in d.lower() for d in self._get_dirs()):
            patterns['plugin_based'] = True
        
        # Check for library structure
        if any(f == '__init__.py' for f in self._get_files()):
            patterns['library'] = True
        
        return patterns
    
    def _get_dirs(self):
        """Get all directories."""
        dirs = []
        for root, dirnames, _ in os.walk(self.base_path):
            dirs.extend(dirnames)
        return dirs
    
    def _get_files(self):
        """Get all files."""
        files = []
        for root, _, filenames in os.walk(self.base_path):
            files.extend(filenames)
        return files
    
    def analyze_code_metrics(self) -> dict:
        """Analyze code metrics."""
        metrics = {
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'avg_file_size': 0,
            'largest_files': []
        }
        
        all_files = []
        
        for root, _, files in os.walk(self.base_path):
            for f in files:
                if f.endswith(('.py', '.sh', '.js', '.ts')):
                    path = os.path.join(root, f)
                    try:
                        with open(path, 'r') as file:
                            lines = file.readlines()
                        
                        total = len(lines)
                        code = sum(1 for l in lines if l.strip() and not l.strip().startswith('#'))
                        comments = sum(1 for l in lines if l.strip().startswith('#'))
                        blank = sum(1 for l in lines if not l.strip())
                        
                        metrics['total_lines'] += total
                        metrics['code_lines'] += code
                        metrics['comment_lines'] += comments
                        metrics['blank_lines'] += blank
                        
                        all_files.append((path, total))
                    except:
                        pass
        
        # Sort by size
        all_files.sort(key=lambda x: x[1], reverse=True)
        metrics['largest_files'] = all_files[:10]
        
        # Calculate average
        if all_files:
            metrics['avg_file_size'] = metrics['total_lines'] / len(all_files)
        
        return metrics
    
    def generate_architecture_report(self):
        """Generate a comprehensive architecture report."""
        print("=" * 70)
        print("CODE STRUCTURE ANALYSIS")
        print("=" * 70)
        
        # Directory structure
        structure = self.analyze_directory_structure()
        print(f"\n📁 Directory Structure")
        print("-" * 70)
        print(f"  Root: {structure['root']}")
        print(f"  Total directories: {structure['total_dirs']}")
        print(f"  Total files: {structure['total_files']}")
        print(f"\n  By file type:")
        for ext, count in sorted(structure['by_type'].items(), key=lambda x: -x[1])[:10]:
            print(f"    {ext or '(no ext)':15} {count:5} files")
        
        # Entry points
        if structure['entry_points']:
            print(f"\n🚪 Entry Points ({len(structure['entry_points'])})")
            print("-" * 70)
            for ep in structure['entry_points'][:10]:
                print(f"  - {ep}")
        
        # Config files
        if structure['config_files']:
            print(f"\n⚙️  Configuration Files ({len(structure['config_files'])})")
            print("-" * 70)
            for cf in structure['config_files'][:10]:
                print(f"  - {cf}")
        
        # Architecture patterns
        patterns = self.find_architecture_patterns()
        print(f"\n🏗️  Architectural Patterns Detected")
        print("-" * 70)
        for pattern, detected in patterns.items():
            status = "✓" if detected else "✗"
            print(f"  {status} {pattern.replace('_', ' ').title()}")
        
        # Code metrics
        metrics = self.analyze_code_metrics()
        print(f"\n📊 Code Metrics")
        print("-" * 70)
        print(f"  Total lines: {metrics['total_lines']:,}")
        print(f"  Code lines: {metrics['code_lines']:,}")
        print(f"  Comment lines: {metrics['comment_lines']:,}")
        print(f"  Blank lines: {metrics['blank_lines']:,}")
        if metrics['total_lines'] > 0:
            ratio = (metrics['comment_lines'] / metrics['total_lines']) * 100
            print(f"  Comment ratio: {ratio:.1f}%")
        print(f"  Average file size: {metrics['avg_file_size']:.0f} lines")
        
        # Largest files
        if metrics['largest_files']:
            print(f"\n📄 Largest Files")
            print("-" * 70)
            for path, size in metrics['largest_files'][:10]:
                print(f"  {size:5} lines  {path}")
        
        # Module dependencies
        deps = self.analyze_module_dependencies()
        if deps:
            print(f"\n🔗 Module Dependencies")
            print("-" * 70)
            
            # Find most connected modules
            connected = [(m, len(d['imports']) + len(d['imported_by'])) 
                        for m, d in deps.items()]
            connected.sort(key=lambda x: x[1], reverse=True)
            
            for module, count in connected[:10]:
                if count > 0:
                    d = deps[module]
                    print(f"\n  {module}")
                    print(f"    Imports: {len(d['imports'])}, Used by: {len(d['imported_by'])}")
        
        print("\n" + "=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Code Structure Analyzer')
    parser.add_argument('--path', type=str, default='~/dotfiles', help='Base path to analyze')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--structure', action='store_true', help='Show structure only')
    parser.add_argument('--metrics', action='store_true', help='Show metrics only')
    parser.add_argument('--deps', action='store_true', help='Show dependencies only')
    args = parser.parse_args()
    
    analyzer = StructureAnalyzer(args.path)
    
    if args.structure:
        structure = analyzer.analyze_directory_structure()
        print("Directory Structure:")
        print(f"  Directories: {structure['total_dirs']}")
        print(f"  Files: {structure['total_files']}")
        print(f"  By type: {dict(structure['by_type'])}")
    
    elif args.metrics:
        metrics = analyzer.analyze_code_metrics()
        print("Code Metrics:")
        print(f"  Total lines: {metrics['total_lines']}")
        print(f"  Code/Comment/Blank: {metrics['code_lines']}/{metrics['comment_lines']}/{metrics['blank_lines']}")
    
    elif args.deps:
        deps = analyzer.analyze_module_dependencies()
        print("Module Dependencies:")
        for module, info in list(deps.items())[:10]:
            print(f"  {module}: imports {len(info['imports'])}, used by {len(info['imported_by'])}")
    
    else:
        analyzer.generate_architecture_report()


if __name__ == '__main__':
    main()

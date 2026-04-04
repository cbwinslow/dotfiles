#!/usr/bin/env python3
"""
Architecture Visualizer - Visualize code architecture and relationships
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import search_files_content, get_python_files, get_shell_files


class ArchitectureVisualizer:
    """Visualize high-level architecture and relationships."""
    
    def __init__(self, base_path='~/dotfiles'):
        self.base_path = Path(base_path).expanduser()
        self.components = []
        self.connections = []
    
    def identify_components(self) -> list:
        """Identify major components in the codebase."""
        components = []
        
        # Scan for skill directories
        skills_dir = self.base_path / 'ai' / 'skills'
        if skills_dir.exists():
            for d in skills_dir.iterdir():
                if d.is_dir() and not d.name.startswith('.'):
                    components.append({
                        'name': d.name,
                        'type': 'skill',
                        'path': str(d),
                        'description': self._read_skill_md(d)
                    })
        
        # Scan for agent configs
        agents_dir = self.base_path / 'ai' / 'agents'
        if agents_dir.exists():
            for f in agents_dir.iterdir():
                if f.suffix in ['.yaml', '.yml']:
                    components.append({
                        'name': f.stem,
                        'type': 'agent',
                        'path': str(f),
                        'description': f'Agent configuration'
                    })
        
        # Scan for scripts
        scripts_dir = self.base_path / 'ai' / 'scripts'
        if scripts_dir.exists():
            tools = []
            for f in scripts_dir.iterdir():
                if f.suffix == '.py' and f.name.startswith('cbw_'):
                    tools.append({
                        'name': f.stem.replace('cbw_', ''),
                        'type': 'tool',
                        'path': str(f),
                        'description': self._get_script_description(f)
                    })
            if tools:
                components.append({
                    'name': 'organization_tools',
                    'type': 'tool_suite',
                    'children': tools,
                    'description': 'Code organization and analysis tools'
                })
        
        # Scan for shared resources
        shared_dir = self.base_path / 'ai' / 'shared'
        if shared_dir.exists():
            for d in shared_dir.iterdir():
                if d.is_dir():
                    components.append({
                        'name': d.name,
                        'type': 'shared',
                        'path': str(d),
                        'description': f'Shared {d.name}'
                    })
        
        return components
    
    def _read_skill_md(self, skill_dir: Path) -> str:
        """Read SKILL.md from skill directory."""
        skill_md = skill_dir / 'SKILL.md'
        if skill_md.exists():
            with open(skill_md, 'r') as f:
                lines = f.readlines()
                for line in lines[:5]:
                    if line.strip() and not line.startswith('#'):
                        return line.strip()[:60]
        return f'{skill_dir.name} skill'
    
    def _get_script_description(self, script_path: Path) -> str:
        """Get description from script docstring."""
        try:
            with open(script_path, 'r') as f:
                lines = f.readlines()
                for line in lines[:10]:
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        # Found docstring start
                        desc = line.strip().strip('"').strip("'")
                        if desc:
                            return desc
        except:
            pass
        return f'{script_path.stem} tool'
    
    def find_relationships(self, components: list) -> list:
        """Find relationships between components."""
        relationships = []
        
        # Find which agents use which skills
        for comp in components:
            if comp['type'] == 'agent':
                # Read agent config
                try:
                    with open(comp['path'], 'r') as f:
                        content = f.read()
                    
                    # Look for skill references
                    for other in components:
                        if other['type'] == 'skill':
                            if other['name'] in content:
                                relationships.append({
                                    'from': comp['name'],
                                    'to': other['name'],
                                    'type': 'uses'
                                })
                except:
                    pass
            
            elif comp['type'] == 'skill':
                # Check if skill uses shared resources
                shared_dir = self.base_path / 'ai' / 'shared'
                if shared_dir.exists():
                    for d in shared_dir.iterdir():
                        if d.is_dir():
                            # Check if skill references this shared resource
                            results = search_files_content(
                                d.name, 
                                file_extensions=['.py', '.sh'],
                                max_results=5
                            )
                            for r in results:
                                if comp['path'] in r['file_path']:
                                    relationships.append({
                                        'from': comp['name'],
                                        'to': d.name,
                                        'type': 'uses'
                                    })
                                    break
        
        return relationships
    
    def visualize_tree(self, components: list = None) -> str:
        """Generate a tree visualization."""
        if components is None:
            components = self.identify_components()
        
        lines = ["Code Architecture", "=" * 50, ""]
        
        # Group by type
        by_type = defaultdict(list)
        for comp in components:
            by_type[comp['type']].append(comp)
        
        # Print tree
        lines.append("📦 dotfiles/ai/")
        
        for type_name, comps in sorted(by_type.items()):
            lines.append(f"  ├── 📁 {type_name}s/ ({len(comps)} items)")
            
            for i, comp in enumerate(comps):
                is_last = (i == len(comps) - 1)
                prefix = "  │   └── " if is_last else "  │   ├── "
                
                if 'children' in comp:
                    lines.append(f"{prefix}📦 {comp['name']}")
                    for j, child in enumerate(comp['children']):
                        child_last = (j == len(comp['children']) - 1)
                        child_prefix = "  │       └── " if child_last else "  │       ├── "
                        lines.append(f"{child_prefix}🔧 {child['name']}")
                else:
                    icon = "🤖" if comp['type'] == 'agent' else "⚡" if comp['type'] == 'skill' else "📦"
                    lines.append(f"{prefix}{icon} {comp['name']}")
        
        return '\n'.join(lines)
    
    def visualize_mermaid(self, components: list = None, relationships: list = None) -> str:
        """Generate Mermaid diagram."""
        if components is None:
            components = self.identify_components()
        if relationships is None:
            relationships = self.find_relationships(components)
        
        lines = ["```mermaid", "graph TD"]
        
        # Define nodes
        node_ids = {}
        for i, comp in enumerate(components):
            node_id = f"C{i}"
            node_ids[comp['name']] = node_id
            
            if comp['type'] == 'agent':
                lines.append(f"    {node_id}[{comp['name']}]")
            elif comp['type'] == 'skill':
                lines.append(f"    {node_id}({comp['name']})")
            elif comp['type'] == 'tool_suite':
                lines.append(f"    {node_id}[{comp['name']}]")
            else:
                lines.append(f"    {node_id}(({comp['name']}))")
        
        # Define connections
        for rel in relationships:
            if rel['from'] in node_ids and rel['to'] in node_ids:
                lines.append(f"    {node_ids[rel['from']]} -->|{rel['type']}| {node_ids[rel['to']]}")
        
        lines.append("```")
        return '\n'.join(lines)
    
    def visualize_flow(self) -> str:
        """Visualize data flow."""
        lines = ["Data Flow", "=" * 50, ""]
        
        # Typical flow in this system
        flow = [
            ("📥 Indexing", "RAG system indexes files"),
            ("🔍 Analysis", "Tools analyze patterns"),
            ("📊 Reporting", "Generate insights"),
            ("🤖 Agent Support", "AI agents use insights"),
        ]
        
        for i, (step, desc) in enumerate(flow):
            lines.append(f"  {i+1}. {step}")
            lines.append(f"     {desc}")
            if i < len(flow) - 1:
                lines.append("      ↓")
        
        return '\n'.join(lines)
    
    def generate_summary(self):
        """Generate a visual summary."""
        components = self.identify_components()
        relationships = self.find_relationships(components)
        
        print("=" * 70)
        print("ARCHITECTURE VISUALIZATION")
        print("=" * 70)
        
        print("\n" + self.visualize_tree(components))
        
        print("\n" + "=" * 70)
        print(self.visualize_flow())
        
        if relationships:
            print("\n" + "=" * 70)
            print("Component Relationships")
            print("-" * 70)
            for rel in relationships[:20]:
                print(f"  {rel['from']} --{rel['type']}--> {rel['to']}")
        
        print("\n" + "=" * 70)
        print("Mermaid Diagram (for documentation)")
        print("-" * 70)
        print(self.visualize_mermaid(components, relationships))


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Architecture Visualizer')
    parser.add_argument('--path', type=str, default='~/dotfiles', help='Base path')
    parser.add_argument('--tree', action='store_true', help='Show tree view')
    parser.add_argument('--mermaid', action='store_true', help='Generate Mermaid diagram')
    parser.add_argument('--flow', action='store_true', help='Show data flow')
    parser.add_argument('--summary', action='store_true', help='Show full summary')
    args = parser.parse_args()
    
    visualizer = ArchitectureVisualizer(args.path)
    
    if args.tree:
        components = visualizer.identify_components()
        print(visualizer.visualize_tree(components))
    
    elif args.mermaid:
        components = visualizer.identify_components()
        relationships = visualizer.find_relationships(components)
        print(visualizer.visualize_mermaid(components, relationships))
    
    elif args.flow:
        print(visualizer.visualize_flow())
    
    elif args.summary:
        visualizer.generate_summary()
    
    else:
        visualizer.generate_summary()


if __name__ == '__main__':
    main()

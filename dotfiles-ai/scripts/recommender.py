#!/usr/bin/env python3
"""
Shell Command Recommender
Suggests commands based on what you have in your indexed scripts
"""

import os
import sys
import re
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import search_files_content, get_shell_files


class CommandRecommender:
    """Recommend shell commands based on indexed patterns."""
    
    def __init__(self):
        self.command_db = self._build_command_db()
    
    def _build_command_db(self) -> dict:
        """Build database of commands from indexed scripts."""
        db = {
            'database': [],
            'docker': [],
            'git': [],
            'file_ops': [],
            'network': [],
            'system': [],
            'ai': [],
        }
        
        # Search for common command patterns
        patterns = [
            ('psql', 'database', 'PostgreSQL commands'),
            ('docker', 'docker', 'Docker operations'),
            ('docker-compose', 'docker', 'Docker Compose'),
            ('git ', 'git', 'Git operations'),
            ('kubectl', 'system', 'Kubernetes'),
            ('curl ', 'network', 'HTTP requests'),
            ('find ', 'file_ops', 'File search'),
            ('grep ', 'file_ops', 'Text search'),
            ('rsync', 'file_ops', 'File sync'),
            ('ollama', 'ai', 'Ollama AI'),
            ('letta', 'ai', 'Letta agents'),
        ]
        
        for pattern, category, desc in patterns:
            results = search_files_content(pattern, max_results=10)
            for r in results:
                # Extract the command line
                text = r.get('chunk_text', '')
                lines = text.split('\n')
                for line in lines:
                    if pattern in line and not line.strip().startswith('#'):
                        db[category].append({
                            'command': line.strip(),
                            'file': r['file_path'],
                            'description': desc
                        })
        
        return db
    
    def recommend_for_task(self, task_description: str) -> list:
        """Recommend commands for a specific task."""
        task_lower = task_description.lower()
        recommendations = []
        
        # Task to category mapping
        task_map = {
            'database': ['db', 'sql', 'postgres', 'query', 'psql'],
            'docker': ['container', 'docker', 'compose', 'image'],
            'git': ['git', 'commit', 'branch', 'push', 'pull'],
            'file_ops': ['file', 'find', 'search', 'copy', 'sync'],
            'network': ['curl', 'api', 'http', 'request', 'download'],
            'system': ['process', 'kill', 'system', 'service'],
            'ai': ['ai', 'ollama', 'letta', 'agent', 'model'],
        }
        
        # Find matching categories
        matched_categories = set()
        for category, keywords in task_map.items():
            if any(kw in task_lower for kw in keywords):
                matched_categories.add(category)
        
        # Get commands from matched categories
        for cat in matched_categories:
            if cat in self.command_db:
                # Get unique commands
                seen = set()
                for cmd in self.command_db[cat]:
                    cmd_key = cmd['command'][:60]  # First 60 chars as key
                    if cmd_key not in seen and len(cmd['command']) < 200:
                        seen.add(cmd_key)
                        recommendations.append(cmd)
        
        return recommendations[:10]
    
    def find_one_liners(self) -> list:
        """Find useful one-liners from scripts."""
        one_liners = []
        
        # Search for common one-liner patterns
        patterns = [
            r'find.*-exec',
            r'grep.*\|',
            r'curl.*\|',
            r'psql.*-c',
            r'docker.*\|',
            r'jq ',
            r'sed ',
        ]
        
        for pattern in patterns:
            results = search_files_content(pattern.replace('\\', ''), max_results=5)
            for r in results:
                text = r.get('chunk_text', '')
                lines = text.split('\n')
                for line in lines:
                    if re.search(pattern, line) and 20 < len(line) < 150:
                        one_liners.append({
                            'command': line.strip(),
                            'source': r['file_path'],
                            'pattern': pattern
                        })
        
        return one_liners[:15]
    
    def get_psql_patterns(self) -> list:
        """Get PostgreSQL/psql command patterns."""
        results = search_files_content("psql", max_results=20)
        patterns = []
        
        for r in results:
            text = r.get('chunk_text', '')
            lines = text.split('\n')
            for line in lines:
                if 'psql' in line and ('-c' in line or '-f' in line or '<<' in line):
                    patterns.append({
                        'command': line.strip(),
                        'file': r['file_path']
                    })
        
        return patterns[:10]
    
    def get_docker_patterns(self) -> list:
        """Get Docker command patterns."""
        patterns = []
        
        docker_cmds = ['docker run', 'docker build', 'docker-compose', 'docker exec', 'docker logs']
        for cmd in docker_cmds:
            results = search_files_content(cmd, max_results=5)
            for r in results:
                text = r.get('chunk_text', '')
                lines = text.split('\n')
                for line in lines:
                    if cmd in line and not line.strip().startswith('#'):
                        patterns.append({
                            'command': line.strip(),
                            'file': r['file_path'],
                            'type': cmd
                        })
        
        return patterns[:15]


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Shell Command Recommender')
    parser.add_argument('--task', type=str, help='Describe your task for recommendations')
    parser.add_argument('--oneliners', action='store_true', help='Show useful one-liners')
    parser.add_argument('--psql', action='store_true', help='Show PostgreSQL patterns')
    parser.add_argument('--docker', action='store_true', help='Show Docker patterns')
    args = parser.parse_args()
    
    recommender = CommandRecommender()
    
    if args.task:
        print(f"\n💡 Commands for: {args.task}")
        print("=" * 60)
        recs = recommender.recommend_for_task(args.task)
        for i, rec in enumerate(recs[:8], 1):
            print(f"\n{i}. {rec['description']}")
            print(f"   Command: {rec['command'][:80]}")
            print(f"   Source: {rec['file']}")
    
    elif args.oneliners:
        print("\n🔥 Useful One-Liners")
        print("=" * 60)
        liners = recommender.find_one_liners()
        for liner in liners[:10]:
            print(f"\n{liner['command'][:80]}")
            print(f"   From: {liner['source']}")
    
    elif args.psql:
        print("\n🐘 PostgreSQL Patterns")
        print("=" * 60)
        patterns = recommender.get_psql_patterns()
        for p in patterns[:10]:
            print(f"\n{p['command'][:80]}")
            print(f"   From: {p['file']}")
    
    elif args.docker:
        print("\n🐳 Docker Patterns")
        print("=" * 60)
        patterns = recommender.get_docker_patterns()
        for p in patterns[:10]:
            print(f"\n{p['type']}: {p['command'][:80]}")
            print(f"   From: {p['file']}")
    
    else:
        print("\n🎯 Shell Command Recommender")
        print("=" * 60)
        print("\nUsage examples:")
        print("  recommender --task 'database backup'")
        print("  recommender --task 'docker deployment'")
        print("  recommender --oneliners")
        print("  recommender --psql")
        print("  recommender --docker")


if __name__ == '__main__':
    main()

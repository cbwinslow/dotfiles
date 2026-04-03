#!/usr/bin/env python3
"""
Skill Discovery Tool - Help agents discover and use available skills
"""

import os
import sys
import yaml
from pathlib import Path

SKILLS_DIR = Path("/home/cbwinslow/dotfiles/ai/skills")


class SkillDiscovery:
    """Discover and provide information about available skills."""
    
    def __init__(self):
        self.skills = self._load_all_skills()
    
    def _load_all_skills(self):
        """Load all available skills."""
        skills = {}
        
        if not SKILLS_DIR.exists():
            return skills
        
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                skill_md = skill_dir / 'SKILL.md'
                if skill_md.exists():
                    skills[skill_dir.name] = {
                        'path': str(skill_dir),
                        'doc': str(skill_md)
                    }
        
        return skills
    
    def list_skills(self):
        """List all available skills."""
        print("=" * 70)
        print("AVAILABLE SKILLS")
        print("=" * 70)
        print()
        
        categories = {
            'Debug & Analysis': ['debug', 'analyze', 'visualize', 'python-refactor', 'reuse', 'tasks'],
            'Letta Memory': ['letta_agents', 'letta_memory', 'letta_blocks', 'letta_backup', 'a0_memory', 'autonomous_memory', 'unified_memory'],
            'Operations': ['docker-ops', 'github', 'infrastructure', 'system-maintenance', 'shell'],
            'Security': ['bitwarden', 'bitwarden_secrets'],
            'Development': ['coding', 'research', 'knowledge', 'skills', 'conversation_logger'],
            'Framework': ['letta_model_picker', 'letta_integration']
        }
        
        for category, skill_names in categories.items():
            print(f"\n{category}")
            print("-" * 70)
            for name in skill_names:
                if name in self.skills:
                    print(f"  ✓ {name}")
                else:
                    print(f"  ✗ {name} (not found)")
        
        print()
        print(f"Total: {len(self.skills)} skills available")
    
    def get_skill_info(self, skill_name):
        """Get detailed info about a skill."""
        if skill_name not in self.skills:
            print(f"Skill not found: {skill_name}")
            return
        
        skill_path = self.skills[skill_name]['doc']
        
        try:
            with open(skill_path, 'r') as f:
                content = f.read()
                # Extract first few sections
                lines = content.split('\n')
                
                print(f"=" * 70)
                print(f"SKILL: {skill_name}")
                print(f"=" * 70)
                print()
                
                # Print first 50 lines
                for line in lines[:50]:
                    print(line)
                
                if len(lines) > 50:
                    print(f"\n... ({len(lines) - 50} more lines)")
                    print(f"Full doc: {skill_path}")
        except Exception as e:
            print(f"Error reading skill: {e}")
    
    def check_skill(self, skill_name):
        """Check if a skill is available."""
        if skill_name in self.skills:
            print(f"✓ Skill '{skill_name}' is available")
            print(f"  Location: {self.skills[skill_name]['path']}")
            return True
        else:
            print(f"✗ Skill '{skill_name}' not found")
            return False
    
    def recommend_skills(self, task_type):
        """Recommend skills for a task type."""
        recommendations = {
            'coding': ['debug', 'analyze', 'coding', 'python-refactor', 'reuse'],
            'debugging': ['debug', 'analyze', 'visualize'],
            'devops': ['docker-ops', 'infrastructure', 'system-maintenance', 'shell'],
            'research': ['research', 'knowledge', 'letta_memory'],
            'security': ['bitwarden', 'bitwarden_secrets'],
            'memory': ['letta_agents', 'letta_memory', 'letta_blocks', 'unified_memory'],
            'all': list(self.skills.keys())
        }
        
        print(f"=" * 70)
        print(f"RECOMMENDED SKILLS FOR: {task_type}")
        print(f"=" * 70)
        print()
        
        if task_type in recommendations:
            for skill in recommendations[task_type]:
                status = "✓" if skill in self.skills else "✗"
                print(f"  {status} {skill}")
        else:
            print(f"Unknown task type: {task_type}")
            print("Available types: coding, debugging, devops, research, security, memory, all")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Skill Discovery Tool')
    parser.add_argument('--list', action='store_true', help='List all skills')
    parser.add_argument('--info', type=str, help='Get info about a skill')
    parser.add_argument('--check', type=str, help='Check if skill is available')
    parser.add_argument('--recommend', type=str, help='Recommend skills for task type')
    args = parser.parse_args()
    
    discovery = SkillDiscovery()
    
    if args.list:
        discovery.list_skills()
    elif args.info:
        discovery.get_skill_info(args.info)
    elif args.check:
        discovery.check_skill(args.check)
    elif args.recommend:
        discovery.recommend_skills(args.recommend)
    else:
        discovery.list_skills()


if __name__ == '__main__':
    main()

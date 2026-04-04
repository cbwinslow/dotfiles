#!/usr/bin/env python3
"""
AI Config Validator
Validates and suggests improvements for AI agent configurations
"""

import os
import sys
import yaml
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import search_files_content, get_config_files


class AIConfigValidator:
    """Validate AI agent configurations."""
    
    REQUIRED_FIELDS = ['name', 'model', 'skills']
    RECOMMENDED_FIELDS = ['tools', 'system_prompt', 'memory']
    
    def __init__(self):
        self.known_patterns = self._load_known_patterns()
    
    def _load_known_patterns(self) -> dict:
        """Load known good patterns from indexed configs."""
        patterns = {
            'models': [],
            'skills': set(),
            'tools': set(),
        }
        
        # Find model configurations
        results = search_files_content("model:", file_extensions=['.yaml', '.yml'], max_results=20)
        for r in results:
            text = r.get('chunk_text', '')
            if 'gpt-4' in text or 'claude' in text or 'ollama' in text.lower():
                lines = text.split('\n')
                for line in lines:
                    if 'model:' in line:
                        model = line.split(':')[1].strip().strip('"\'')
                        if model and model not in patterns['models']:
                            patterns['models'].append(model)
        
        # Find common skills
        results = search_files_content("skills:", file_extensions=['.yaml'], max_results=20)
        for r in results:
            text = r.get('chunk_text', '')
            if 'unified_memory' in text or 'cbw_rag' in text or 'shell' in text:
                patterns['skills'].add('unified_memory')
                patterns['skills'].add('shell')
                patterns['skills'].add('cbw_rag')
        
        return patterns
    
    def validate_agent_config(self, config_path: str) -> dict:
        """Validate an agent YAML configuration."""
        if not os.path.exists(config_path):
            return {"error": "File not found"}
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            return {"error": f"YAML parse error: {e}"}
        
        issues = []
        warnings = []
        suggestions = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in config:
                issues.append(f"Missing required field: {field}")
        
        # Check recommended fields
        for field in self.RECOMMENDED_FIELDS:
            if field not in config:
                warnings.append(f"Missing recommended field: {field}")
        
        # Validate model
        if 'model' in config:
            model = config['model']
            if isinstance(model, dict) and 'id' in model:
                model_id = model['id']
                # Check if it's a known pattern
                known_models = ['gpt-4', 'claude-3-5', 'anthropic', 'ollama']
                if not any(km in str(model_id).lower() for km in known_models):
                    warnings.append(f"Unusual model ID: {model_id}")
        
        # Validate skills
        if 'skills' in config and isinstance(config['skills'], list):
            available_skills = self._find_available_skills()
            for skill in config['skills']:
                if skill not in available_skills:
                    warnings.append(f"Skill not found: {skill}")
        
        # Check for unified_memory (recommended)
        if 'skills' in config and 'unified_memory' not in config['skills']:
            suggestions.append("Consider adding 'unified_memory' skill for RAG integration")
        
        # Check for MCP servers
        if 'mcp_servers' not in config:
            suggestions.append("Consider adding MCP servers for extended functionality")
        
        return {
            'file': config_path,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'config': config
        }
    
    def _find_available_skills(self) -> set:
        """Find available skills from indexed files."""
        skills = set()
        results = search_files_content("SKILL.md", max_results=30)
        for r in results:
            path = r.get('file_path', '')
            parts = path.split('/')
            if 'skills' in parts:
                idx = parts.index('skills')
                if idx + 1 < len(parts):
                    skills.add(parts[idx + 1])
        return skills
    
    def find_similar_configs(self, config_path: str) -> list:
        """Find similar agent configurations."""
        basename = os.path.basename(config_path).replace('.yaml', '').replace('.yml', '')
        
        # Search for configs with similar names
        results = search_files_content(basename, file_extensions=['.yaml'], max_results=10)
        
        similar = []
        for r in results:
            if r['file_path'] != config_path:
                similar.append(r['file_path'])
        
        return similar[:5]
    
    def generate_improved_config(self, config_path: str) -> str:
        """Generate an improved version of a config."""
        validation = self.validate_agent_config(config_path)
        
        if 'error' in validation:
            return f"# Error: {validation['error']}"
        
        config = validation['config']
        
        # Build improved config
        improved = []
        improved.append(f"# Improved configuration for: {config.get('name', 'Unnamed')}")
        improved.append(f"# Original: {config_path}")
        improved.append("")
        
        # Add missing recommended fields
        if validation['suggestions']:
            improved.append("# Suggestions:")
            for s in validation['suggestions']:
                improved.append(f"# - {s}")
            improved.append("")
        
        # Add sample MCP server config if missing
        if 'mcp_servers' not in config:
            improved.append("# Consider adding MCP servers:")
            improved.append("# mcp_servers:")
            improved.append("#   - name: cbw_rag")
            improved.append("#     command: python3 /home/cbwinslow/dotfiles/ai/shared/mcp/rag_server.py")
            improved.append("")
        
        return '\n'.join(improved)
    
    def scan_all_configs(self) -> list:
        """Scan all indexed config files."""
        results = []
        config_files = get_config_files(limit=100)
        
        for cf in config_files:
            path = cf['file_path']
            if 'agents' in path or path.endswith(('.yaml', '.yml')):
                validation = self.validate_agent_config(path)
                if 'error' not in validation or validation.get('valid'):
                    results.append({
                        'file': path,
                        'name': validation['config'].get('name', 'Unknown'),
                        'valid': validation['valid'],
                        'issues': len(validation['issues']),
                        'warnings': len(validation['warnings'])
                    })
        
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='AI Config Validator')
    parser.add_argument('--validate', type=str, help='Validate a specific config file')
    parser.add_argument('--scan-all', action='store_true', help='Scan all indexed configs')
    parser.add_argument('--improve', type=str, help='Generate improvements for config')
    parser.add_argument('--find-similar', type=str, help='Find similar configs')
    args = parser.parse_args()
    
    validator = AIConfigValidator()
    
    if args.validate:
        result = validator.validate_agent_config(args.validate)
        print(f"\n📋 Validation: {result['file']}")
        print("=" * 60)
        print(f"Valid: {'✓' if result['valid'] else '✗'}")
        
        if result['issues']:
            print("\n❌ Issues:")
            for i in result['issues']:
                print(f"  - {i}")
        
        if result['warnings']:
            print("\n⚠️  Warnings:")
            for w in result['warnings']:
                print(f"  - {w}")
        
        if result['suggestions']:
            print("\n💡 Suggestions:")
            for s in result['suggestions']:
                print(f"  - {s}")
    
    elif args.scan_all:
        results = validator.scan_all_configs()
        print(f"\n🔍 Found {len(results)} agent configs")
        print("=" * 60)
        for r in results:
            status = "✓" if r['valid'] and r['warnings'] == 0 else "⚠️" if r['valid'] else "✗"
            print(f"{status} {r['name']:30} ({r['issues']} issues, {r['warnings']} warnings)")
            print(f"   {r['file']}")
    
    elif args.improve:
        improved = validator.generate_improved_config(args.improve)
        print(improved)
    
    elif args.find_similar:
        similar = validator.find_similar_configs(args.find_similar)
        print(f"\n📚 Similar configs to {args.find_similar}:")
        for s in similar:
            print(f"  - {s}")
    
    else:
        print("AI Config Validator - Usage:")
        print("  validator --validate <config.yaml>")
        print("  validator --scan-all")
        print("  validator --improve <config.yaml>")
        print("  validator --find-similar <config.yaml>")


if __name__ == '__main__':
    main()

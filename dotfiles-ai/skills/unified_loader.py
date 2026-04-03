#!/usr/bin/env python3
"""
Unified AI Skill Loader
=======================
Automatically discovers and loads skills for ALL AI agents:
- claude, cline, codex, gemini, kilocode, openclaw, opencode, qwen, vscode, windsurf

Industry Standard Pattern:
- Single source: ~/dotfiles/ai/skills/
- Symlinks per agent: ~/.claude/skills/ -> ~/dotfiles/ai/skills/
- Auto-discovery via SKILL.md files
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Skill:
    """Represents a single AI skill"""
    name: str
    description: str
    version: str
    category: str
    path: Path
    tags: List[str]
    agents: List[str]  # Which agents can use this skill
    
    @property
    def skill_md_path(self) -> Path:
        return self.path / "SKILL.md"
    
    @property
    def is_available(self) -> bool:
        return self.skill_md_path.exists()


class UnifiedSkillLoader:
    """
    Universal skill loader for all AI agents.
    
    Based on industry standards from:
    - OpenAgentSkills (https://github.com/Notysoty/openagentskills)
    - SkillShare pattern (symlinks to ~/.config/)
    - OpenCode skill discovery
    """
    
    def __init__(self, dotfiles_path: str = None):
        self.dotfiles = Path(dotfiles_path or os.path.expanduser("~/dotfiles"))
        self.ai_root = self.dotfiles / "ai"
        
        # Primary skill locations (single source of truth)
        self.skills_dirs = [
            self.ai_root / "skills",           # Main skills folder
            self.ai_root / "shared" / "skills", # Legacy shared skills
        ]
        
        # Agent config directories (where they expect skills)
        self.agent_configs = {
            "claude": Path.home() / ".claude",
            "cline": Path.home() / ".cline", 
            "codex": Path.home() / ".codex",
            "gemini": Path.home() / ".gemini",
            "kilocode": Path.home() / ".kilocode",
            "openclaw": Path.home() / ".openclaw",
            "opencode": Path.home() / ".opencode",
            "qwen": Path.home() / ".qwen",
            "vscode": Path.home() / ".vscode" / "ai",
            "windsurf": Path.home() / ".windsurf",
        }
        
        # Dotfiles agent configs
        self.dotfiles_agents = self.ai_root / "agents"
        
        self._skills_cache: Dict[str, Skill] = {}
    
    def discover_skills(self) -> List[Skill]:
        """Scan all skill directories and build registry"""
        skills = []
        
        for skills_dir in self.skills_dirs:
            if not skills_dir.exists():
                continue
                
            for skill_path in skills_dir.iterdir():
                if not skill_path.is_dir():
                    continue
                    
                skill_md = skill_path / "SKILL.md"
                if skill_md.exists():
                    skill = self._parse_skill(skill_path)
                    if skill:
                        skills.append(skill)
                        self._skills_cache[skill.name] = skill
        
        return skills
    
    def _parse_skill(self, skill_path: Path) -> Optional[Skill]:
        """Parse SKILL.md frontmatter to extract metadata"""
        skill_md = skill_path / "SKILL.md"
        
        try:
            content = skill_md.read_text()
            
            # Extract frontmatter (YAML between --- markers)
            if content.startswith("---"):
                _, frontmatter, _ = content.split("---", 2)
                metadata = yaml.safe_load(frontmatter)
            else:
                metadata = {}
            
            return Skill(
                name=metadata.get("name", skill_path.name),
                description=metadata.get("description", "No description"),
                version=metadata.get("version", "1.0.0"),
                category=metadata.get("category", "general"),
                path=skill_path,
                tags=metadata.get("tags", []),
                agents=metadata.get("agents", ["all"])  # Default: all agents
            )
            
        except Exception as e:
            print(f"⚠️  Failed to parse {skill_path}: {e}")
            return None
    
    def setup_agent_symlinks(self, agent_name: str = None):
        """
        Create symlinks from agent config dirs to unified skills folder.
        
        Args:
            agent_name: Specific agent to setup, or None for all
        """
        agents_to_setup = [agent_name] if agent_name else self.agent_configs.keys()
        
        for agent in agents_to_setup:
            agent_dir = self.agent_configs.get(agent)
            if not agent_dir:
                continue
            
            # Create agent config dir if needed
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # Create skills symlink
            skills_link = agent_dir / "skills"
            unified_skills = self.ai_root / "skills"
            
            try:
                if skills_link.exists() or skills_link.is_symlink():
                    skills_link.unlink()
                
                skills_link.symlink_to(unified_skills, target_is_directory=True)
                print(f"✅ {agent}: ~/.{agent}/skills/ -> ~/dotfiles/ai/skills/")
                
            except Exception as e:
                print(f"❌ {agent}: Failed to create symlink: {e}")
    
    def get_skills_for_agent(self, agent_name: str) -> List[Skill]:
        """Get all skills available to a specific agent"""
        all_skills = self.discover_skills()
        
        return [
            skill for skill in all_skills
            if "all" in skill.agents or agent_name in skill.agents
        ]
    
    def load_skill(self, skill_name: str, agent_name: str = None) -> Optional[str]:
        """Load a skill's content for use by an agent"""
        skill = self._skills_cache.get(skill_name)
        
        if not skill:
            # Try to discover it
            self.discover_skills()
            skill = self._skills_cache.get(skill_name)
        
        if not skill or not skill.is_available:
            return None
        
        # Check if agent can use this skill
        if agent_name and "all" not in skill.agents:
            if agent_name not in skill.agents:
                return None
        
        return skill.skill_md_path.read_text()
    
    def generate_agent_config(self, agent_name: str) -> dict:
        """Generate complete skill configuration for an agent"""
        skills = self.get_skills_for_agent(agent_name)
        
        return {
            "agent": agent_name,
            "skills_root": str(self.ai_root / "skills"),
            "available_skills": [
                {
                    "name": s.name,
                    "description": s.description,
                    "version": s.version,
                    "category": s.category,
                    "path": str(s.path),
                }
                for s in skills
            ],
            "skill_count": len(skills),
        }
    
    def export_registry(self) -> Path:
        """Export skill registry to JSON for external tools"""
        registry_path = self.ai_root / "skills" / "registry.json"
        
        skills_data = []
        for skill in self.discover_skills():
            skills_data.append({
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
                "category": skill.category,
                "path": str(skill.path),
                "tags": skill.tags,
                "agents": skill.agents,
            })
        
        registry = {
            "version": "2.0.0",
            "skills_count": len(skills_data),
            "skills": skills_data,
            "last_updated": str(__import__('datetime').datetime.now()),
        }
        
        registry_path.write_text(json.dumps(registry, indent=2))
        return registry_path


def main():
    """CLI interface for skill management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified AI Skill Loader")
    parser.add_argument("action", choices=["setup", "list", "discover", "config", "export"])
    parser.add_argument("--agent", help="Specific agent name")
    parser.add_argument("--skill", help="Specific skill name")
    
    args = parser.parse_args()
    
    loader = UnifiedSkillLoader()
    
    if args.action == "setup":
        loader.setup_agent_symlinks(args.agent)
        print("\n✅ Setup complete! All agents now share unified skills.")
        
    elif args.action == "list":
        agent = args.agent or "all"
        skills = loader.get_skills_for_agent(agent)
        
        print(f"\n📚 Skills available to {agent}:")
        for skill in skills:
            print(f"  • {skill.name} ({skill.category}) - {skill.description}")
        print(f"\nTotal: {len(skills)} skills")
        
    elif args.action == "discover":
        skills = loader.discover_skills()
        print(f"\n🔍 Discovered {len(skills)} skills:")
        for skill in skills:
            agents = ", ".join(skill.agents) if "all" not in skill.agents else "all agents"
            print(f"  • {skill.name} → {agents}")
            
    elif args.action == "config":
        agent = args.agent or "default"
        config = loader.generate_agent_config(agent)
        print(json.dumps(config, indent=2))
        
    elif args.action == "export":
        registry_path = loader.export_registry()
        print(f"✅ Registry exported to: {registry_path}")


if __name__ == "__main__":
    main()

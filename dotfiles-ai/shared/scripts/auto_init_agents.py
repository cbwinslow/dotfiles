#!/usr/bin/env python3
"""
Auto Initialize Agents Script

Automatically configures all AI agents with global rules and centralized settings.
"""

import os
import sys
import json
import yaml
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AgentInitializer:
    def __init__(self, base_path: str = "/home/cbwinslow/dotfiles/ai"):
        self.base_path = Path(base_path)
        self.global_rules_path = self.base_path / "global_rules" / "agent_init_rules.md"
        self.configs_path = self.base_path / "configs"
        self.scripts_path = self.base_path / "scripts"
        
        self.agents = {
            "opencode": {"type": "cli", "config_file": "opencode/config.yaml", "init_script": "init_opencode.py", "shell_alias": "opencode"},
            "gemini": {"type": "cli", "config_file": "gemini/config.yaml", "init_script": "init_gemini.py", "shell_alias": "gemini"},
            "claude": {"type": "cli", "config_file": "claude/config.yaml", "init_script": "init_claude.py", "shell_alias": "claude"},
            "cline": {"type": "cli", "config_file": "cline/config.yaml", "init_script": "init_cline.py", "shell_alias": "cline"},
            "kilocode": {"type": "cli", "config_file": "kilocode/config.yaml", "init_script": "init_kilocode.py", "shell_alias": "kilocode"},
            "vscode": {"type": "ide", "config_file": "vscode/config.yaml", "init_script": "init_vscode.py", "shell_alias": "vscode"},
            "windsurf": {"type": "cli", "config_file": "windsurf/config.yaml", "init_script": "init_windsurf.py", "shell_alias": "windsurf"},
            "openclaw": {"type": "cli", "config_file": "openclaw/config.yaml", "init_script": "init_openclaw.py", "shell_alias": "openclaw"}
        }
    
    def check_prerequisites(self) -> bool:
        logger.info("Checking prerequisites...")
        try:
            import letta_integration
            logger.info("✓ letta_integration package is available")
        except ImportError:
            logger.error("✗ letta_integration package not found")
            return False
        
        if not self.global_rules_path.exists():
            logger.error(f"✗ Global rules not found at {self.global_rules_path}")
            return False
        logger.info("✓ Global rules found")
        
        if not self.configs_path.exists():
            logger.error(f"✗ Configs directory not found at {self.configs_path}")
            return False
        logger.info("✓ Configs directory found")
        
        return True
    
    def create_agent_init_script(self, agent_name: str, agent_config: Dict[str, Any]) -> bool:
        logger.info(f"Creating initialization script for {agent_name}...")
        init_script_path = self.scripts_path / agent_config["init_script"]
        
        agent_name_upper = agent_name.upper()
        shell_alias = agent_config["shell_alias"]
        
        # Build script content using string concatenation to avoid f-string issues
        lines = []
        lines.append('#!/usr/bin/env python3')
        lines.append('"""')
        lines.append(f'Auto-initialization script for {agent_name} agent')
        lines.append('"""')
        lines.append('')
        lines.append('import os')
        lines.append('import sys')
        lines.append('from pathlib import Path')
        lines.append('')
        lines.append('sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "agent_memory"))')
        lines.append('')
        lines.append('try:')
        lines.append('    from agent_memory import store_agent_context, get_agent_context')
        lines.append('    logger.info("✓ Agent memory system loaded successfully")')
        lines.append('except Exception as e:')
        lines.append('    logger.error(f"Failed to import Agent memory system: {e}")')
        lines.append('    sys.exit(1)')
        lines.append('')
        lines.append('def initialize_agent():')
        lines.append(f'    logger.info("Initializing {agent_name} agent with global rules...")')
        lines.append('    ')
        lines.append('    global_rules_path = Path(__file__).parent.parent / "global_rules" / "agent_init_rules.md"')
        lines.append('    if global_rules_path.exists():')
        lines.append("        with open(global_rules_path, 'r') as f:")
        lines.append('            global_rules = f.read()')
        lines.append('        logger.info("✓ Global rules loaded")')
        lines.append('    else:')
        lines.append('        logger.error("✗ Global rules not found")')
        lines.append('        return False')
        lines.append('    ')
        lines.append('    agent_context = {')
        lines.append('        "initialized": True,')
        lines.append('        "global_rules_loaded": True,')
        lines.append('        "memory_backend": "agent_memory",')
        lines.append('        "letta_connected": False,')
        lines.append('    }')
        lines.append('    ')
        lines.append('    context_id = store_agent_context(')
        lines.append(f'        agent_name="{agent_name}",')
        lines.append('        context_key="agent_configuration",')
        lines.append('        context_value=str(agent_context)')
        lines.append('    )')
        lines.append('    ')
        lines.append('    if context_id:')
        lines.append('        logger.info(f"✓ Agent context stored with ID: {context_id}")')
        lines.append('    else:')
        lines.append('        logger.error("✗ Failed to store agent context")')
        lines.append('        return False')
        lines.append('    ')
        lines.append('    store_agent_context(')
        lines.append(f'        agent_name="{agent_name}",')
        lines.append('        context_key="initialization_complete",')
        lines.append('        context_value="true"')
        lines.append('    )')
        lines.append('    ')
        lines.append(f'    logger.info(f"✓ {agent_name} agent initialized successfully")')
        lines.append('    return True')
        lines.append('')
        lines.append('def setup_shell_integration():')
        lines.append('    logger.info("Setting up shell integration...")')
        lines.append('    ')
        lines.append('    shell_config = """')
        lines.append(f'# Agent AI Skills System - {agent_name} Agent')
        lines.append('export AI_SKILLS_SYSTEM="/home/cbwinslow/dotfiles/ai"')
        lines.append(f'export {agent_name_upper}_RULES="$AI_SKILLS_SYSTEM/global_rules/agent_init_rules.md"')
        lines.append(f'alias {shell_alias}="{shell_alias} --init-rules $AI_SKILLS_SYSTEM/global_rules"')
        lines.append('"""')
        lines.append('    ')
        lines.append('    home_dir = Path.home()')
        lines.append('    shell_rc = home_dir / ".zshrc" if Path(home_dir / ".zshrc").exists() else home_dir / ".bashrc"')
        lines.append('    ')
        lines.append('    if shell_rc.exists():')
        lines.append("        with open(shell_rc, 'r') as f:")
        lines.append('            content = f.read()')
        lines.append('        if "AI_SKILLS_SYSTEM" in content:')
        lines.append('            logger.info("✓ Shell integration already configured")')
        lines.append('            return True')
        lines.append('    ')
        lines.append("    with open(shell_rc, 'a') as f:")
        lines.append('        f.write(shell_config)')
        lines.append('    ')
        lines.append('    logger.info(f"✓ Shell integration added to {shell_rc}")')
        lines.append('    return True')
        lines.append('')
        lines.append('if __name__ == "__main__":')
        lines.append('    if initialize_agent():')
        lines.append('        setup_shell_integration()')
        lines.append(f'        logger.info("🎉 {agent_name} agent setup complete!")')
        lines.append('        sys.exit(0)')
        lines.append('    else:')
        lines.append(f'        logger.error("❌ {agent_name} agent setup failed!")')
        lines.append('        sys.exit(1)')
        
        script_content = '\n'.join(lines) + '\n'
        
        try:
            with open(init_script_path, 'w') as f:
                f.write(script_content)
            os.chmod(init_script_path, 0o755)
            logger.info(f"✓ Initialization script created: {init_script_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create initialization script: {e}")
            return False
    
    def create_framework_integration(self) -> bool:
        logger.info("Creating framework integration files...")
        frameworks_dir = self.base_path / "frameworks"
        frameworks_dir.mkdir(parents=True, exist_ok=True)
        
        for framework in ["langchain", "crewai", "autogen"]:
            fw_dir = frameworks_dir / framework
            fw_dir.mkdir(parents=True, exist_ok=True)
            with open(fw_dir / "integration.py", 'w') as f:
                f.write(f'"""{framework.title()} Integration with Agent AI Skills System"""\n')
            logger.info(f"✓ {framework.title()} integration created")
        
        return True
    
    def create_shell_aliases(self) -> bool:
        logger.info("Creating shell aliases...")
        home_dir = Path.home()
        shell_rc = home_dir / ".zshrc" if Path(home_dir / ".zshrc").exists() else home_dir / ".bashrc"
        
        aliases = """
# Agent AI Skills System - Global Agent Aliases
export AI_SKILLS_SYSTEM="/home/cbwinslow/dotfiles/ai"
export LETTA_SERVER_URL="http://localhost:8283"

alias opencode="opencode --init-rules $AI_SKILLS_SYSTEM/global_rules"
alias gemini="gemini --init-rules $AI_SKILLS_SYSTEM/global_rules"  
alias claude="claude --init-rules $AI_SKILLS_SYSTEM/global_rules"
alias cline="cline --init-rules $AI_SKILLS_SYSTEM/global_rules"
alias kilocode="kilocode --init-rules $AI_SKILLS_SYSTEM/global_rules"
alias windsurf="windsurf --init-rules $AI_SKILLS_SYSTEM/global_rules"
alias openclaw="openclaw --init-rules $AI_SKILLS_SYSTEM/global_rules"
alias init-all-agents="python3 $AI_SKILLS_SYSTEM/scripts/auto_init_agents.py"
"""
        
        try:
            if shell_rc.exists():
                with open(shell_rc, 'r') as f:
                    content = f.read()
                if "AI_SKILLS_SYSTEM" in content:
                    logger.info("✓ Shell aliases already configured")
                    return True
            
            with open(shell_rc, 'a') as f:
                f.write(aliases)
            logger.info(f"✓ Shell aliases added to {shell_rc}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create shell aliases: {e}")
            return False
    
    def run_full_initialization(self) -> bool:
        logger.info("=" * 60)
        logger.info("Agent AI Skills System - Agent Auto-Initialization")
        logger.info("=" * 60)
        
        if not self.check_prerequisites():
            logger.error("❌ Prerequisites not met.")
            return False
        
        if not self.create_framework_integration():
            logger.error("❌ Framework integration failed.")
            return False
        
        for agent_name, agent_config in self.agents.items():
            if not self.create_agent_init_script(agent_name, agent_config):
                logger.error(f"❌ Failed to create initialization script for {agent_name}")
                return False
        
        if not self.create_shell_aliases():
            logger.error("❌ Failed to create shell aliases.")
            return False
        
        logger.info("=" * 60)
        logger.info("🎉 Agent Auto-Initialization Complete!")
        logger.info("=" * 60)
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Auto-initialize AI agents")
    parser.add_argument("--agent", help="Initialize specific agent")
    parser.add_argument("--all", action="store_true", help="Initialize all agents")
    parser.add_argument("--frameworks", action="store_true", help="Create framework integrations only")
    parser.add_argument("--aliases", action="store_true", help="Create shell aliases only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    initializer = AgentInitializer()
    
    if args.agent:
        if args.agent in initializer.agents:
            agent_config = initializer.agents[args.agent]
            success = initializer.create_agent_init_script(args.agent, agent_config)
            if success:
                logger.info(f"✓ Initialization script created for {args.agent}")
            else:
                logger.error(f"✗ Failed to create initialization script for {args.agent}")
                sys.exit(1)
        else:
            logger.error(f"✗ Unknown agent: {args.agent}")
            sys.exit(1)
    elif args.frameworks:
        success = initializer.create_framework_integration()
        if success:
            logger.info("✓ Framework integrations created")
        else:
            logger.error("✗ Framework integration failed")
            sys.exit(1)
    elif args.aliases:
        success = initializer.create_shell_aliases()
        if success:
            logger.info("✓ Shell aliases created")
        else:
            logger.error("✗ Shell alias creation failed")
            sys.exit(1)
    else:
        success = initializer.run_full_initialization()
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()

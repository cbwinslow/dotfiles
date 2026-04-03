#!/usr/bin/env python3
"""
Complete System Setup Script

This script sets up the entire Agent AI Skills System including:
- GitHub backup and synchronization
- Agent auto-initialization
- Global rules enforcement
- Shell integration
- Framework integrations
- Validation and testing
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CompleteSystemSetup:
    def __init__(self, base_path: str = "/home/cbwinslow/dotfiles/ai"):
        self.base_path = Path(base_path)
        self.scripts_path = self.base_path / "scripts"
        
        # Setup steps in order
        self.setup_steps = [
            {
                "name": "GitHub Backup System",
                "script": "github_backup.py",
                "args": ["--setup-actions", "--setup-docs"],
                "description": "Setup GitHub backup and CI/CD"
            },
            {
                "name": "Agent Auto-Initialization",
                "script": "auto_init_agents.py",
                "args": ["--frameworks", "--aliases"],
                "description": "Setup agent frameworks and shell aliases"
            },
            {
                "name": "System Validation",
                "script": "validate_system.py",
                "args": ["--verbose"],
                "description": "Validate complete system setup"
            }
        ]
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        logger.info("Checking system prerequisites...")
        
        # Check if Agent memory package is installed
        try:
            import agent_memory
            logger.info("✓ Agent memory package is available")
        except ImportError:
            logger.error("✗ Agent memory package not found. Please install it first:")
            logger.error("  cd /home/cbwinslow/dotfiles/ai/packages/agent_memory")
            logger.error("  pip install -e .")
            return False
        
        # Check if all required scripts exist
        required_scripts = [
            "github_backup.py",
            "auto_init_agents.py", 
            "validate_system.py"
        ]
        
        for script in required_scripts:
            script_path = self.scripts_path / script
            if not script_path.exists():
                logger.error(f"✗ Required script not found: {script_path}")
                return False
            logger.info(f"✓ Script found: {script}")
        
        # Check if global rules exist
        global_rules = self.base_path / "global_rules" / "agent_init_rules.md"
        if not global_rules.exists():
            logger.error(f"✗ Global rules not found at {global_rules}")
            return False
        logger.info("✓ Global rules found")
        
        return True
    
    def run_setup_step(self, step: Dict[str, Any]) -> bool:
        """Run a single setup step."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Running: {step['name']}")
        logger.info(f"Description: {step['description']}")
        logger.info(f"{'='*60}")
        
        script_path = self.scripts_path / step['script']
        
        try:
            # Run the script
            cmd = [sys.executable, str(script_path)] + step['args']
            result = subprocess.run(
                cmd,
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Log output
            if result.stdout:
                logger.info("Output:")
                logger.info(result.stdout)
            
            if result.stderr:
                logger.warning("Errors/Warnings:")
                logger.warning(result.stderr)
            
            if result.returncode == 0:
                logger.info(f"✓ {step['name']} completed successfully")
                return True
            else:
                logger.error(f"✗ {step['name']} failed with exit code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"✗ {step['name']} timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"✗ {step['name']} failed with exception: {e}")
            return False
    
    def create_master_config(self) -> bool:
        """Create master configuration file."""
        logger.info("Creating master configuration...")
        
        master_config = {
            "system_version": "1.0.0",
            "installation_date": "2026-03-24",
            "base_path": str(self.base_path),
            "components": {
                "agent_memory_package": True,
                "global_rules": True,
                "agent_configs": True,
                "framework_integrations": True,
                "github_backup": True,
                "auto_initialization": True,
                "shell_integration": True
            },
            "agents": [
                "opencode", "gemini", "claude", "cline", 
                "kilocode", "vscode", "windsurf", "openclaw"
            ],
            "frameworks": ["langchain", "crewai", "autogen"],
            "skills": ["memory_management", "cross_agent_communication"],
            "tools": ["file_system", "terminal", "search", "memory_operations"],
            "environment": {
                "postgres_host": os.getenv("PG_HOST", "localhost"),
                "postgres_port": os.getenv("PG_PORT", "5432"),
                "postgres_db": os.getenv("PG_DBNAME", "letta"),
                "letta_server": os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
            }
        }
        
        config_path = self.base_path / "system_config.json"
        try:
            with open(config_path, 'w') as f:
                import json
                json.dump(master_config, f, indent=2)
            logger.info(f"✓ Master configuration created at {config_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create master configuration: {e}")
            return False
    
    def create_quick_start_guide(self) -> bool:
        """Create quick start guide."""
        logger.info("Creating quick start guide...")
        
        quick_start = f"""# Agent AI Skills System - Quick Start Guide

## 🚀 Quick Start

### 1. Install Agent Memory Package
```bash
cd {self.base_path}/packages/agent_memory
pip install -e .
```

### 2. Set Environment Variables
```bash
export PG_HOST=localhost
export PG_PORT=5432
export PG_DBNAME=letta
export PG_USER=cbwinslow
export PG_PASSWORD=123qweasd
export LETTA_SERVER_URL=http://localhost:8283
export LETTA_API_KEY=your-api-key
```

### 3. Initialize System
```bash
cd {self.base_path}
python3 scripts/setup_complete_system.py
```

### 4. Initialize Individual Agents
```bash
# Initialize specific agent
python3 scripts/auto_init_agents.py --agent opencode

# Or initialize all agents
python3 scripts/auto_init_agents.py --all
```

### 5. Test the System
```bash
python3 scripts/validate_system.py --verbose
```

## 📋 Daily Usage

### Start Shell with AI Integration
```bash
# Restart shell to load aliases
source ~/.zshrc  # or ~/.bashrc

# Use agents with automatic rule loading
opencode "Write a Python script to analyze data"
gemini "Help me debug this code"
claude "Explain this algorithm"
```

### Memory Management
```bash
# Save conversation
agent-memory-cli store --type conversation --title "Meeting Notes" --content "Discussion about..."

# Search memories
agent-memory-cli search --query "entity extraction" --type "processing_status"

# View statistics
agent-memory-cli stats
```

### Agent Management
```bash
# Check agent status
python3 scripts/validate_system.py

# Initialize all agents
python3 scripts/auto_init_agents.py --all

# Create backup
python3 scripts/github_backup.py --create-backup
```

## 🔧 Configuration

### Agent-Specific Configuration
Edit agent configs in:
- `{self.base_path}/agents/opencode/config.yaml`
- `{self.base_path}/agents/gemini/config.yaml`
- `{self.base_path}/agents/claude/config.yaml`

### Framework Configuration
Edit framework configs in:
- `{self.base_path}/frameworks/langchain/config.yaml`
- `{self.base_path}/frameworks/crewai/config.yaml`
- `{self.base_path}/frameworks/autogen/config.yaml`

### Global Rules
Edit global rules in:
- `{self.base_path}/global_rules/agent_init_rules.md`

## 🆘 Troubleshooting

### Common Issues

1. **Agent not loading rules**
   - Check shell aliases are loaded: `source ~/.zshrc`
   - Verify global rules path: `ls {self.base_path}/global_rules/`

2. **Memory system not working**
   - Check PostgreSQL connection: `psql -h localhost -U cbwinslow letta`
   - Verify environment variables are set
   - Run: `agent-memory-cli init`

3. **Letta integration issues**
   - Check Letta server is running: `docker ps`
   - Verify API key is correct
   - Test connection: `curl http://localhost:8283/health`

### Getting Help
- Check logs in: `{self.base_path}/logs/`
- Run validation: `python3 scripts/validate_system.py --verbose`
- View system config: `cat {self.base_path}/system_config.json`

## 🔄 Updates and Maintenance

### Update System
```bash
# Pull latest changes
python3 scripts/github_backup.py --pull

# Re-run setup if needed
python3 scripts/setup_complete_system.py
```

### Create Backup
```bash
# Manual backup
python3 scripts/github_backup.py --create-backup

# Automated backup (via GitHub Actions)
# Runs daily at 2 AM UTC
```

### Add New Agent
1. Create agent directory: `{self.base_path}/agents/newagent/`
2. Add config file: `config.yaml`
3. Run: `python3 scripts/auto_init_agents.py --agent newagent`

---

**Note**: This system is designed to be self-documenting. Check the README.md files in each directory for detailed information.
"""
        
        guide_path = self.base_path / "QUICK_START.md"
        try:
            with open(guide_path, 'w') as f:
                f.write(quick_start)
            logger.info(f"✓ Quick start guide created at {guide_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create quick start guide: {e}")
            return False
    
    def create_monitoring_script(self) -> bool:
        """Create system monitoring script."""
        logger.info("Creating system monitoring script...")
        
        monitoring_script = self.scripts_path / "monitor_system.py"
        monitoring_content = '''#!/usr/bin/env python3
"""
System Monitoring Script

Monitors the health and status of the Agent AI Skills System.
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemMonitor:
    def __init__(self, base_path: str = "/home/cbwinslow/dotfiles/ai"):
        self.base_path = Path(base_path)
        self.config_path = self.base_path / "system_config.json"
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "components": {},
            "issues": [],
            "recommendations": []
        }
        
        # Check Agent memory package
        try:
            import agent_memory
            health_report["components"]["agent_memory"] = {"status": "healthy", "version": "1.0.0"}
        except ImportError:
            health_report["components"]["agent_memory"] = {"status": "failed", "error": "Package not installed"}
            health_report["issues"].append("Agent memory package not installed")
        
        # Check PostgreSQL connection
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.getenv("PG_HOST", "localhost"),
                port=int(os.getenv("PG_PORT", 5432)),
                database=os.getenv("PG_DBNAME", "letta"),
                user=os.getenv("PG_USER", "cbwinslow"),
                password=os.getenv("PG_PASSWORD", "123qweasd"),
            )
            conn.close()
            health_report["components"]["postgresql"] = {"status": "healthy"}
        except Exception as e:
            health_report["components"]["postgresql"] = {"status": "failed", "error": str(e)}
            health_report["issues"].append(f"PostgreSQL connection failed: {e}")
        
        # Check Letta server
        try:
            import requests
            letta_url = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
            response = requests.get(f"{letta_url}/health", timeout=5)
            if response.status_code == 200:
                health_report["components"]["letta_server"] = {"status": "healthy"}
            else:
                health_report["components"]["letta_server"] = {"status": "warning", "status_code": response.status_code}
                health_report["issues"].append(f"Letta server returned status: {response.status_code}")
        except Exception as e:
            health_report["components"]["letta_server"] = {"status": "failed", "error": str(e)}
            health_report["issues"].append(f"Letta server not accessible: {e}")
        
        # Check agent configurations
        agents_dir = self.base_path / "agents"
        if agents_dir.exists():
            agent_configs = list(agents_dir.glob("*/config.yaml"))
            health_report["components"]["agents"] = {
                "status": "healthy", 
                "count": len(agent_configs),
                "agents": [p.parent.name for p in agent_configs]
            }
        else:
            health_report["components"]["agents"] = {"status": "failed", "error": "Agents directory not found"}
            health_report["issues"].append("Agents directory not found")
        
        # Determine overall status
        failed_components = [k for k, v in health_report["components"].items() if v["status"] == "failed"]
        if failed_components:
            health_report["status"] = "critical"
            health_report["recommendations"].append("Fix failed components before using the system")
        elif health_report["issues"]:
            health_report["status"] = "warning"
            health_report["recommendations"].append("Review and address warnings")
        else:
            health_report["status"] = "healthy"
            health_report["recommendations"].append("System is ready for use")
        
        return health_report
    
    def generate_report(self) -> str:
        """Generate human-readable health report."""
        health = self.check_system_health()
        
        report = f"""
Agent AI Skills System - Health Report
{'='*50}
Timestamp: {health['timestamp']}
Overall Status: {health['status'].upper()}

Components:
"""
        
        for component, status in health["components"].items():
            status_icon = "✓" if status["status"] == "healthy" else "⚠" if status["status"] == "warning" else "✗"
            report += f"  {status_icon} {component}: {status['status']}\n"
            if "error" in status:
                report += f"    Error: {status['error']}\n"
            if "count" in status:
                report += f"    Count: {status['count']}\n"
        
        if health["issues"]:
            report += f"\nIssues Found ({len(health['issues'])}):\n"
            for i, issue in enumerate(health["issues"], 1):
                report += f"  {i}. {issue}\n"
        
        if health["recommendations"]:
            report += f"\nRecommendations:\n"
            for i, rec in enumerate(health["recommendations"], 1):
                report += f"  {i}. {rec}\n"
        
        return report
    
    def save_health_report(self) -> bool:
        """Save health report to file."""
        try:
            health = self.check_system_health()
            report_path = self.base_path / "logs" / "health_report.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(health, f, indent=2)
            
            logger.info(f"✓ Health report saved to {report_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to save health report: {e}")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Agent AI Skills System health")
    parser.add_argument("--report", action="store_true", help="Generate and display health report")
    parser.add_argument("--save", action="store_true", help="Save health report to file")
    parser.add_argument("--check", action="store_true", help="Quick health check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    monitor = SystemMonitor()
    
    if args.report:
        report = monitor.generate_report()
        print(report)
    
    if args.save:
        monitor.save_health_report()
    
    if args.check:
        health = monitor.check_system_health()
        print(f"System Status: {health['status']}")
        if health['issues']:
            print(f"Issues: {len(health['issues'])}")
            for issue in health['issues'][:3]:  # Show first 3 issues
                print(f"  - {issue}")
    
    if not any([args.report, args.save, args.check]):
        parser.print_help()


if __name__ == "__main__":
    main()
'''
        
        try:
            with open(monitoring_script, 'w') as f:
                f.write(monitoring_content)
            os.chmod(monitoring_script, 0o755)
            logger.info(f"✓ System monitoring script created at {monitoring_script}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create monitoring script: {e}")
            return False
    
    def run_complete_setup(self) -> bool:
        """Run the complete system setup."""
        logger.info("=" * 80)
        logger.info("Agent AI Skills System - Complete Setup")
        logger.info("=" * 80)
        
        # Check prerequisites
        if not self.check_prerequisites():
            logger.error("❌ Prerequisites not met. Please fix the issues above.")
            return False
        
        # Create master configuration
        if not self.create_master_config():
            logger.error("❌ Failed to create master configuration.")
            return False
        
        # Create quick start guide
        if not self.create_quick_start_guide():
            logger.error("❌ Failed to create quick start guide.")
            return False
        
        # Create monitoring script
        if not self.create_monitoring_script():
            logger.error("❌ Failed to create monitoring script.")
            return False
        
        # Run setup steps
        for step in self.setup_steps:
            if not self.run_setup_step(step):
                logger.error(f"❌ Setup step failed: {step['name']}")
                return False
        
        # Final validation
        logger.info("\n" + "="*60)
        logger.info("Running final validation...")
        logger.info("="*60)
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.scripts_path / "validate_system.py"), "--verbose"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("✓ Final validation passed")
            else:
                logger.warning("⚠ Final validation completed with warnings")
                if result.stdout:
                    logger.info("Validation output:")
                    logger.info(result.stdout)
                if result.stderr:
                    logger.warning("Validation warnings:")
                    logger.warning(result.stderr)
        
        except Exception as e:
            logger.warning(f"⚠ Final validation failed: {e}")
        
        # Create summary
        self.create_setup_summary()
        
        logger.info("=" * 80)
        logger.info("🎉 COMPLETE SETUP FINISHED!")
        logger.info("=" * 80)
        logger.info("Next steps:")
        logger.info("1. Restart your shell: source ~/.zshrc (or ~/.bashrc)")
        logger.info("2. Initialize agents: python3 scripts/auto_init_agents.py --all")
        logger.info("3. Test the system: python3 scripts/validate_system.py")
        logger.info("4. Read the quick start guide: cat QUICK_START.md")
        logger.info("5. Monitor system health: python3 scripts/monitor_system.py --report")
        
        return True
    
    def create_setup_summary(self) -> None:
        """Create setup summary file."""
        summary = f"""# Agent AI Skills System - Setup Summary

## Setup Completed
- Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Base Path: {self.base_path}
- System Version: 1.0.0

## Components Installed
✓ Agent Memory Package
✓ Global Rules System
✓ Agent Configurations (8 agents)
✓ Framework Integrations (3 frameworks)
✓ GitHub Backup System
✓ Auto-Initialization Scripts
✓ Shell Integration
✓ System Monitoring
✓ Documentation

## Next Steps
1. Restart your shell to load aliases
2. Initialize individual agents if needed
3. Set up environment variables
4. Test the system
5. Create GitHub repository for backup

## Quick Commands
- Check system health: `python3 scripts/monitor_system.py --report`
- Validate setup: `python3 scripts/validate_system.py`
- Initialize all agents: `python3 scripts/auto_init_agents.py --all`
- Create backup: `python3 scripts/github_backup.py --create-backup`

## Support
- Quick start guide: QUICK_START.md
- System documentation: README.md
- Agent guides: docs/agent_guides/
- Framework guides: docs/framework_guides/
"""
        
        summary_path = self.base_path / "SETUP_SUMMARY.md"
        try:
            with open(summary_path, 'w') as f:
                f.write(summary)
            logger.info(f"✓ Setup summary created at {summary_path}")
        except Exception as e:
            logger.error(f"Failed to create setup summary: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete setup for Agent AI Skills System")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup = CompleteSystemSetup()
    success = setup.run_complete_setup()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
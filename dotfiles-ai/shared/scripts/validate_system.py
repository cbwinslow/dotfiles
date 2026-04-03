#!/usr/bin/env python3
"""
System Validation Script for Agent AI Skills System

Validates the entire AI skills system including:
- Package installation
- Configuration files
- Memory system functionality
- Agent configurations
- Framework integrations
- Tailscale network setup
"""

import os
import sys
import json
import yaml
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemValidator:
    def __init__(self, base_path: str = "/home/cbwinslow/dotfiles/ai"):
        self.base_path = Path(base_path)
        self.results = {
            "packages": {},
            "configurations": {},
            "memory_system": {},
            "agents": {},
            "frameworks": {},
            "network": {},
            "overall": {"status": "unknown", "score": 0, "total_checks": 0, "passed_checks": 0}
        }
    
    def validate_packages(self) -> bool:
        """Validate all packages are properly installed and configured."""
        logger.info("Validating packages...")
        
        packages = ["agent_memory"]
        all_valid = True
        
        for package in packages:
            package_path = self.base_path / "packages" / package
            package_valid = True
            
            # Check package directory exists
            if not package_path.exists():
                logger.error(f"Package directory not found: {package_path}")
                package_valid = False
                all_valid = False
            else:
                logger.info(f"✓ Package directory found: {package}")
            
            # Check required files
            required_files = ["__init__.py", "core.py", "config.py", "models.py", "cli.py", "setup.py", "README.md"]
            for file_name in required_files:
                file_path = package_path / file_name
                if not file_path.exists():
                    logger.error(f"Missing required file: {file_path}")
                    package_valid = False
                    all_valid = False
                else:
                    logger.info(f"✓ Required file found: {file_name}")
            
            # Check if package can be imported
            try:
                sys.path.insert(0, str(package_path.parent))
                if package == "agent_memory":
                    import agent_memory
                    logger.info(f"✓ Package import successful: {package}")
                else:
                    logger.info(f"✓ Package directory structure valid: {package}")
            except ImportError as e:
                logger.error(f"Failed to import package {package}: {e}")
                package_valid = False
                all_valid = False
            
            self.results["packages"][package] = package_valid
        
        return all_valid
    
    def validate_configurations(self) -> bool:
        """Validate configuration files."""
        logger.info("Validating configurations...")
        
        configs_valid = True
        
        # Check global configs
        global_configs = ["postgresql.yaml", "letta.yaml", "tailscale.yaml"]
        for config in global_configs:
            config_path = self.base_path / "configs" / config
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        yaml.safe_load(f)
                    logger.info(f"✓ Valid YAML config: {config}")
                except yaml.YAMLError as e:
                    logger.error(f"Invalid YAML in {config}: {e}")
                    configs_valid = False
                except Exception as e:
                    logger.error(f"Error reading {config}: {e}")
                    configs_valid = False
            else:
                logger.warning(f"Config file not found: {config}")
        
        # Check environment configs
        env_dir = self.base_path / "configs" / "environments"
        if env_dir.exists():
            env_configs = list(env_dir.glob("*.yaml"))
            for env_config in env_configs:
                try:
                    with open(env_config, 'r') as f:
                        yaml.safe_load(f)
                    logger.info(f"✓ Valid environment config: {env_config.name}")
                except yaml.YAMLError as e:
                    logger.error(f"Invalid YAML in {env_config}: {e}")
                    configs_valid = False
        else:
            logger.warning("Environment configs directory not found")
        
        self.results["configurations"]["global"] = configs_valid
        return configs_valid
    
    def validate_memory_system(self) -> bool:
        """Validate memory system functionality."""
        logger.info("Validating memory system...")
        
        memory_valid = True
        
        try:
            # Import agent_memory
            sys.path.insert(0, str(self.base_path / "packages" / "agent_memory"))
            import agent_memory
            
            # Test basic functionality
            logger.info("Testing memory system functions...")
            
            # Test config loading
            config = agent_memory.load_config()
            if config:
                logger.info("✓ Configuration loading successful")
            else:
                logger.error("Failed to load configuration")
                memory_valid = False
            
            # Test connection string generation
            conn_str = agent_memory.get_connection_string(config)
            if conn_str and "postgresql://" in conn_str:
                logger.info("✓ Connection string generation successful")
            else:
                logger.error("Failed to generate connection string")
                memory_valid = False
            
            # Test CLI availability
            try:
                result = subprocess.run(
                    ["python3", "-m", "agent_memory.cli", "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    logger.info("✓ CLI interface available")
                else:
                    logger.error(f"CLI interface failed: {result.stderr}")
                    memory_valid = False
            except subprocess.TimeoutExpired:
                logger.error("CLI interface timeout")
                memory_valid = False
            except Exception as e:
                logger.error(f"CLI interface error: {e}")
                memory_valid = False
            
        except ImportError as e:
            logger.error(f"Failed to import agent_memory: {e}")
            memory_valid = False
        except Exception as e:
            logger.error(f"Memory system validation error: {e}")
            memory_valid = False
        
        self.results["memory_system"]["basic_functionality"] = memory_valid
        return memory_valid
    
    def validate_agents(self) -> bool:
        """Validate agent configurations."""
        logger.info("Validating agent configurations...")
        
        agents_valid = True
        agents_dir = self.base_path / "agents"
        
        if not agents_dir.exists():
            logger.error("Agents directory not found")
            return False
        
        # Check specific agents
        target_agents = ["opencode", "gemini", "claude"]
        for agent in target_agents:
            agent_dir = agents_dir / agent
            agent_valid = True
            
            if not agent_dir.exists():
                logger.warning(f"Agent directory not found: {agent}")
                agent_valid = False
                agents_valid = False
                continue
            
            # Check config file
            config_file = agent_dir / "config.yaml"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    # Validate required fields
                    required_fields = ["name", "framework", "provider", "model"]
                    for field in required_fields:
                        if field not in config:
                            logger.error(f"Missing required field '{field}' in {agent} config")
                            agent_valid = False
                            agents_valid = False
                    
                    if agent_valid:
                        logger.info(f"✓ Valid agent configuration: {agent}")
                
                except yaml.YAMLError as e:
                    logger.error(f"Invalid YAML in {agent} config: {e}")
                    agent_valid = False
                    agents_valid = False
            else:
                logger.error(f"Config file not found for agent: {agent}")
                agent_valid = False
                agents_valid = False
            
            # Check subdirectories
            subdirs = ["prompts", "tools", "skills"]
            for subdir in subdirs:
                subdir_path = agent_dir / subdir
                if not subdir_path.exists():
                    logger.warning(f"Subdirectory not found for {agent}: {subdir}")
                else:
                    logger.info(f"✓ Agent subdirectory exists: {agent}/{subdir}")
            
            self.results["agents"][agent] = agent_valid
        
        return agents_valid
    
    def validate_frameworks(self) -> bool:
        """Validate framework configurations."""
        logger.info("Validating framework configurations...")
        
        frameworks_valid = True
        frameworks_dir = self.base_path / "frameworks"
        
        if not frameworks_dir.exists():
            logger.error("Frameworks directory not found")
            return False
        
        # Check specific frameworks
        target_frameworks = ["langchain", "crewai", "autogen"]
        for framework in target_frameworks:
            framework_dir = frameworks_dir / framework
            framework_valid = True
            
            if not framework_dir.exists():
                logger.warning(f"Framework directory not found: {framework}")
                framework_valid = False
                frameworks_valid = False
                continue
            
            # Check config file
            config_file = framework_dir / "config.yaml"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    # Validate required fields
                    required_fields = ["framework", "version"]
                    for field in required_fields:
                        if field not in config:
                            logger.error(f"Missing required field '{field}' in {framework} config")
                            framework_valid = False
                            frameworks_valid = False
                    
                    if framework_valid:
                        logger.info(f"✓ Valid framework configuration: {framework}")
                
                except yaml.YAMLError as e:
                    logger.error(f"Invalid YAML in {framework} config: {e}")
                    framework_valid = False
                    frameworks_valid = False
            else:
                logger.error(f"Config file not found for framework: {framework}")
                framework_valid = False
                frameworks_valid = False
            
            self.results["frameworks"][framework] = framework_valid
        
        return frameworks_valid
    
    def validate_network(self) -> bool:
        """Validate network and Tailscale setup."""
        logger.info("Validating network setup...")
        
        network_valid = True
        
        # Check Tailscale sync script
        sync_script = self.base_path / "scripts" / "tailscale_sync.sh"
        if sync_script.exists():
            logger.info("✓ Tailscale sync script found")
        else:
            logger.warning("Tailscale sync script not found")
            network_valid = False
        
        # Check if Tailscale is installed
        try:
            result = subprocess.run(["which", "tailscale"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✓ Tailscale is installed")
            else:
                logger.warning("Tailscale is not installed")
                network_valid = False
        except Exception as e:
            logger.error(f"Error checking Tailscale: {e}")
            network_valid = False
        
        # Check migration script
        migration_script = self.base_path / "scripts" / "create_symlinks.sh"
        if migration_script.exists():
            logger.info("✓ Migration script found")
        else:
            logger.warning("Migration script not found")
            network_valid = False
        
        self.results["network"]["basic_setup"] = network_valid
        return network_valid
    
    def validate_environment(self) -> bool:
        """Validate environment setup."""
        logger.info("Validating environment setup...")
        
        env_valid = True
        
        # Check required environment variables
        required_env_vars = [
            "PG_HOST", "PG_PORT", "PG_DBNAME", "PG_USER", "PG_PASSWORD"
        ]
        
        for var in required_env_vars:
            if os.getenv(var):
                logger.info(f"✓ Environment variable set: {var}")
            else:
                logger.warning(f"Environment variable not set: {var}")
                env_valid = False
        
        # Check if PostgreSQL is accessible
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
            logger.info("✓ PostgreSQL connection successful")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            env_valid = False
        
        # Check if Letta server is accessible
        try:
            import requests
            letta_url = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
            response = requests.get(f"{letta_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Letta server is accessible")
            else:
                logger.warning(f"Letta server returned status: {response.status_code}")
        except Exception as e:
            logger.warning(f"Letta server not accessible: {e}")
        
        self.results["environment"] = env_valid
        return env_valid
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete system validation."""
        logger.info("=" * 60)
        logger.info("Agent AI Skills System - Validation Report")
        logger.info("=" * 60)
        
        # Run all validations
        validations = [
            ("Packages", self.validate_packages),
            ("Configurations", self.validate_configurations),
            ("Memory System", self.validate_memory_system),
            ("Agents", self.validate_agents),
            ("Frameworks", self.validate_frameworks),
            ("Network", self.validate_network),
            ("Environment", self.validate_environment),
        ]
        
        total_checks = len(validations)
        passed_checks = 0
        
        for name, validator in validations:
            logger.info(f"\n--- {name} ---")
            try:
                if validator():
                    passed_checks += 1
                    logger.info(f"✓ {name} validation PASSED")
                else:
                    logger.error(f"✗ {name} validation FAILED")
            except Exception as e:
                logger.error(f"✗ {name} validation ERROR: {e}")
        
        # Calculate overall score
        score = (passed_checks / total_checks) * 100
        status = "HEALTHY" if score >= 80 else "WARNING" if score >= 60 else "CRITICAL"
        
        self.results["overall"] = {
            "status": status,
            "score": score,
            "total_checks": total_checks,
            "passed_checks": passed_checks
        }
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Overall Status: {self.results['overall']['status']}")
        logger.info(f"Score: {self.results['overall']['score']:.1f}%")
        logger.info(f"Checks Passed: {self.results['overall']['passed_checks']}/{self.results['overall']['total_checks']}")
        
        # Print detailed results
        for category, result in self.results.items():
            if category == "overall":
                continue
            logger.info(f"\n{category.upper()}:")
            if isinstance(result, dict):
                for item, status in result.items():
                    status_icon = "✓" if status else "✗"
                    logger.info(f"  {status_icon} {item}: {'PASS' if status else 'FAIL'}")
        
        logger.info("=" * 60)
        
        return self.results
    
    def save_results(self, output_file: str = "validation_report.json"):
        """Save validation results to JSON file."""
        output_path = self.base_path / output_file
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Validation report saved to: {output_path}")


def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Agent AI Skills System")
    parser.add_argument("--path", default="/home/cbwinslow/dotfiles/ai", help="Path to AI skills system")
    parser.add_argument("--output", default="validation_report.json", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = SystemValidator(args.path)
    results = validator.run_validation()
    validator.save_results(args.output)
    
    # Exit with appropriate code
    if results["overall"]["status"] == "HEALTHY":
        sys.exit(0)
    elif results["overall"]["status"] == "WARNING":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
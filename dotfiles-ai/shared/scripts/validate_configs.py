#!/usr/bin/env python3
"""
AI Config Validation Script
Validates all agent configurations against the base config schema.

Usage:
    python3 scripts/validate_configs.py
    python3 scripts/validate_configs.py --verbose
    python3 scripts/validate_configs.py --agent opencode
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single config"""
    agent_name: str
    valid: bool
    errors: List[str]
    warnings: List[str]


class ConfigValidator:
    """Validates AI agent configurations"""
    
    def __init__(self, ai_root: str = None):
        self.ai_root = Path(ai_root) if ai_root else Path.home() / "dotfiles" / "ai"
        self.base_config_path = self.ai_root / "base" / "base_agent.yaml"
        self.agents_dir = self.ai_root / "agents"
        self.errors = []
        self.warnings = []
        
    def load_yaml(self, path: Path) -> Optional[Dict]:
        """Load YAML file"""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"File not found: {path}")
            return None
        except yaml.YAMLError as e:
            logger.error(f"YAML error in {path}: {e}")
            return None
    
    def validate_base_config(self) -> bool:
        """Validate base configuration exists and is valid"""
        if not self.base_config_path.exists():
            self.errors.append(f"Base config not found: {self.base_config_path}")
            return False
        
        config = self.load_yaml(self.base_config_path)
        if not config:
            self.errors.append("Base config is invalid YAML")
            return False
        
        # Check required fields
        required_fields = ["provider", "model", "memory_backend", "letta", "skills", "tools"]
        for field in required_fields:
            if field not in config:
                self.warnings.append(f"Base config missing recommended field: {field}")
        
        # Validate provider is openrouter (our standard)
        if config.get("provider") != "openrouter":
            self.warnings.append(f"Base config provider is '{config.get('provider')}', expected 'openrouter'")
        
        # Validate model is openrouter/free
        if config.get("model") != "openrouter/free":
            self.warnings.append(f"Base config model is '{config.get('model')}', expected 'openrouter/free'")
        
        # Validate Letta configuration
        if "letta" not in config:
            self.errors.append("Base config missing 'letta' section")
            return False
        
        letta_config = config.get("letta", {})
        if not letta_config.get("auto_save_conversations"):
            self.warnings.append("Letta auto_save_conversations is disabled")
        
        if not letta_config.get("auto_create_memories"):
            self.warnings.append("Letta auto_create_memories is disabled")
        
        return True
    
    def validate_agent_config(self, agent_name: str) -> ValidationResult:
        """Validate a single agent configuration"""
        errors = []
        warnings = []
        
        config_path = self.agents_dir / agent_name / "config.yaml"
        
        if not config_path.exists():
            errors.append(f"Config file not found: {config_path}")
            return ValidationResult(agent_name, False, errors, warnings)
        
        config = self.load_yaml(config_path)
        if not config:
            errors.append("Config file is invalid YAML")
            return ValidationResult(agent_name, False, errors, warnings)
        
        # Check extends directive
        extends = config.get("extends")
        if not extends:
            warnings.append("Config does not extend base config")
        else:
            # Resolve relative path
            if extends.startswith("../../base/"):
                expected_base = self.base_config_path
                actual_base = config_path.parent / extends
                if not actual_base.resolve() == expected_base.resolve():
                    warnings.append(f"Extends path incorrect: {extends}")
        
        # Check required fields
        if "name" not in config:
            errors.append("Missing required field: name")
        
        # Check provider override (should use base)
        if "provider" in config:
            if config["provider"] != "openrouter":
                warnings.append(f"Agent overrides provider to '{config['provider']}', should use base")
        
        # Check model override (should use base)
        if "model" in config:
            if config["model"] != "openrouter/free":
                warnings.append(f"Agent overrides model to '{config['model']}', should use base")
        
        # Check Letta tools are included
        tools = config.get("tools", [])
        letta_tools = [t for t in tools if "letta_server" in str(t)]
        if not letta_tools:
            warnings.append("No Letta tools configured")
        
        # Check memory_backend
        if "memory_backend" in config:
            if config["memory_backend"] != "letta_server":
                warnings.append(f"memory_backend is '{config['memory_backend']}', should be 'letta_server'")
        
        return ValidationResult(agent_name, len(errors) == 0, errors, warnings)
    
    def validate_all_agents(self) -> List[ValidationResult]:
        """Validate all agent configurations"""
        results = []
        
        if not self.agents_dir.exists():
            self.errors.append(f"Agents directory not found: {self.agents_dir}")
            return results
        
        for agent_dir in self.agents_dir.iterdir():
            if agent_dir.is_dir():
                result = self.validate_agent_config(agent_dir.name)
                results.append(result)
        
        return results
    
    def validate_skills_registry(self) -> bool:
        """Validate skills registry"""
        registry_path = self.ai_root / "skills" / "registry.yaml"
        
        if not registry_path.exists():
            self.warnings.append(f"Skills registry not found: {registry_path}")
            return False
        
        registry = self.load_yaml(registry_path)
        if not registry:
            self.errors.append("Skills registry is invalid YAML")
            return False
        
        # Check for core skills
        core_skills = registry.get("core", {})
        required_core = ["memory_management", "entity_extraction", "conversation_logging"]
        for skill in required_core:
            if skill not in core_skills:
                self.warnings.append(f"Missing core skill in registry: {skill}")
        
        return True
    
    def validate_tools_registry(self) -> bool:
        """Validate tools registry"""
        registry_path = self.ai_root / "tools" / "registry.yaml"
        
        if not registry_path.exists():
            self.warnings.append(f"Tools registry not found: {registry_path}")
            return False
        
        registry = self.load_yaml(registry_path)
        if not registry:
            self.errors.append("Tools registry is invalid YAML")
            return False
        
        # Check for Letta tools
        letta_tools = registry.get("letta", {})
        required_letta = ["store_conversation", "search_memories", "check_server_health"]
        for tool in required_letta:
            if tool not in letta_tools:
                self.warnings.append(f"Missing Letta tool in registry: {tool}")
        
        return True
    
    def run_full_validation(self, verbose: bool = False) -> bool:
        """Run complete validation"""
        logger.info("=" * 60)
        logger.info("AI Configuration Validation")
        logger.info("=" * 60)
        
        all_valid = True
        
        # Validate base config
        logger.info("\n[1/5] Validating base configuration...")
        base_valid = self.validate_base_config()
        if base_valid:
            logger.info("✓ Base configuration is valid")
        else:
            logger.error("✗ Base configuration has errors")
            all_valid = False
        
        # Validate all agents
        logger.info("\n[2/5] Validating agent configurations...")
        agent_results = self.validate_all_agents()
        valid_agents = sum(1 for r in agent_results if r.valid)
        total_agents = len(agent_results)
        logger.info(f"✓ {valid_agents}/{total_agents} agents valid")
        
        for result in agent_results:
            if not result.valid:
                logger.error(f"  ✗ {result.agent_name}: {len(result.errors)} errors")
                for error in result.errors:
                    logger.error(f"    - {error}")
            elif result.warnings and verbose:
                logger.warning(f"  ! {result.agent_name}: {len(result.warnings)} warnings")
        
        # Validate skills registry
        logger.info("\n[3/5] Validating skills registry...")
        skills_valid = self.validate_skills_registry()
        if skills_valid:
            logger.info("✓ Skills registry is valid")
        else:
            logger.warning("✗ Skills registry has issues")
        
        # Validate tools registry
        logger.info("\n[4/5] Validating tools registry...")
        tools_valid = self.validate_tools_registry()
        if tools_valid:
            logger.info("✓ Tools registry is valid")
        else:
            logger.warning("✗ Tools registry has issues")
        
        # Check environment variables
        logger.info("\n[5/5] Checking environment variables...")
        env_vars = {
            "LETTA_SERVER_URL": os.getenv("LETTA_SERVER_URL"),
            "LETTA_API_KEY": os.getenv("LETTA_API_KEY"),
            "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        }
        
        for var, value in env_vars.items():
            if value:
                logger.info(f"✓ {var} is set")
            else:
                logger.warning(f"! {var} is not set")
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)
        
        if self.errors:
            logger.error(f"Errors: {len(self.errors)}")
            for error in self.errors:
                logger.error(f"  - {error}")
        
        if self.warnings:
            logger.warning(f"Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
        
        if all_valid and not self.errors:
            logger.info("\n✓ All validations passed!")
            return True
        else:
            logger.error("\n✗ Validation failed")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate AI configurations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show warnings")
    parser.add_argument("--ai-root", help="AI root directory")
    args = parser.parse_args()
    
    validator = ConfigValidator(args.ai_root)
    success = validator.run_full_validation(verbose=args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

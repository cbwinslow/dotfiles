#!/usr/bin/env python3
"""
Skill validation script for CI/CD pipelines.
Validates agent configuration and skill structure.
"""

import argparse
import json
import sys
import yaml
from pathlib import Path


def validate_agent(agent_name: str, repo_root: Path) -> dict:
    """Validate a single agent's configuration and skills."""
    errors = []
    warnings = []

    # Paths
    agents_dir = repo_root / "dotfiles" / "ai" / "agents"
    agent_cfg = agents_dir / agent_name / "config.yaml"
    shared_skills_dir = repo_root / "dotfiles" / "ai" / "shared" / "skills"
    skills_dir = repo_root / "dotfiles" / "ai" / "skills"

    # Check agent config exists
    if not agent_cfg.exists():
        errors.append(f"Agent config not found: {agent_cfg}")
        return {"success": False, "errors": errors, "warnings": warnings}

    # Load and validate YAML
    try:
        with open(agent_cfg) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {e}")
        return {"success": False, "errors": errors, "warnings": warnings}

    # Required fields
    required = ["name", "framework", "tools", "skills"]
    for field in required:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    # Validate skills list
    if "skills" in config:
        if not isinstance(config["skills"], list):
            errors.append("'skills' must be a list")
        else:
            for skill in config["skills"]:
                # Check if skill exists in shared skills or main registry
                skill_path = shared_skills_dir / skill
                registry_path = skills_dir / "registry.json"
                if not skill_path.exists() and registry_path.exists():
                    import json

                    try:
                        with open(registry_path) as f:
                            registry = json.load(f)
                        if skill not in [
                            s.get("name") for s in registry.get("skills", [])
                        ]:
                            warnings.append(
                                f"Skill '{skill}' not found in shared skills or registry"
                            )
                    except:
                        pass

    # Validate tools
    if "tools" in config:
        if not isinstance(config["tools"], list):
            errors.append("'tools' must be a list")
        elif len(config["tools"]) == 0:
            errors.append("'tools' list cannot be empty")

    return {
        "success": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "agent": agent_name,
        "config": {
            "name": config.get("name"),
            "framework": config.get("framework"),
            "skills_count": len(config.get("skills", [])),
            "tools_count": len(config.get("tools", [])),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Validate agent skills configuration")
    parser.add_argument("--agent", required=True, help="Agent name to validate")
    parser.add_argument(
        "--repo-root", type=Path, default=Path.cwd(), help="Repository root"
    )
    parser.add_argument("--output-json", type=Path, help="Output results to JSON file")

    args = parser.parse_args()

    result = validate_agent(args.agent, args.repo_root)

    # Print summary
    if result["success"]:
        print(f"✅ Agent '{args.agent}' configuration valid")
        if result["warnings"]:
            print(f"⚠️  Warnings: {len(result['warnings'])}")
            for w in result["warnings"]:
                print(f"   - {w}")
    else:
        print(f"❌ Agent '{args.agent}' validation failed")
        for e in result["errors"]:
            print(f"   - {e}")

    # Output JSON if requested
    if args.output_json:
        with open(args.output_json, "w") as f:
            json.dump(result, f, indent=2)

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
validate_skills.py — Per-agent skill validation for GitHub Actions CI.

Usage:
    python validate_skills.py --agent kilocode --repo-root . --output-json /tmp/result.json

Exit codes:
    0  All checks passed
    1  One or more checks failed
"""

import argparse
import json
import sys
import time
import subprocess
from pathlib import Path

AGENTS = [
    "kilocode", "opencode", "cline", "openclaw",
    "gemini", "qwen", "vscode", "windsurf",
]

# Skills that must be declared in every agent's config
UNIVERSAL_REQUIRED_SKILLS = {"memory_management", "cli_operations"}

# Tools that must be declared in every agent's config
UNIVERSAL_REQUIRED_TOOLS  = {"file_system", "terminal"}

# Agent-specific skills that should be present (in addition to universal ones)
AGENT_REQUIRED_SKILLS: dict[str, set[str]] = {
    "kilocode":  {"code_generation", "cbw_rag_query"},
    "opencode":  {"code_generation", "git_operations"},
    "cline":     {"code_generation", "debugging"},
    "openclaw":  {"code_generation"},
    "gemini":    {"research", "analysis"},
    "qwen":      {"code_generation", "analysis"},
    "vscode":    {"code_generation", "code_review"},
    "windsurf":  {"code_generation", "code_review"},
}


# ─────────────────────────────── helpers ────────────────────────────────────

class Reporter:
    def __init__(self, agent: str):
        self.agent   = agent
        self.passed  = []
        self.failed  = []
        self.skipped = []

    def ok(self, check: str, detail: str = ""):
        msg = f"[{check}]" + (f" — {detail}" if detail else "")
        self.passed.append(msg)
        print(f"  ✓ {check}" + (f": {detail}" if detail else ""))

    def fail(self, check: str, detail: str):
        msg = f"[{check}] {detail}"
        self.failed.append(msg)
        print(f"  ✗ {check}: {detail}")

    def skip(self, check: str, reason: str):
        self.skipped.append(f"[{check}] {reason}")
        print(f"  ~ {check}: {reason} (skipped)")

    @property
    def success(self) -> bool:
        return len(self.failed) == 0

    def as_dict(self) -> dict:
        return {
            "agent":   self.agent,
            "success": self.success,
            "passed":  self.passed,
            "failed":  self.failed,
            "skipped": self.skipped,
            "errors":  self.failed,   # alias for workflow summary step
        }


# ──────────────────────────── individual checks ──────────────────────────────

def check_config_yaml(r: Reporter, agent_dir: Path):
    """Validate config.yaml exists and has required keys/types."""
    try:
        import yaml
    except ImportError:
        r.skip("config_yaml", "pyyaml not installed")
        return

    cfg = agent_dir / "config.yaml"
    if not cfg.exists():
        r.fail("config_yaml", f"missing at {cfg}")
        return

    try:
        data = yaml.safe_load(cfg.read_text())
    except yaml.YAMLError as exc:
        r.fail("config_yaml", f"YAML parse error: {exc}")
        return

    r.ok("config_yaml", "file exists and parses")

    # Required top-level keys
    for key in ("name", "framework", "tools", "skills"):
        if key not in data:
            r.fail(f"config_yaml/{key}", f"key '{key}' missing")
        else:
            r.ok(f"config_yaml/{key}", f"{key} present")

    # Tools list
    tools = data.get("tools", [])
    if not isinstance(tools, list) or len(tools) == 0:
        r.fail("config_yaml/tools", "must be a non-empty list")
    else:
        for req in UNIVERSAL_REQUIRED_TOOLS:
            if req not in tools:
                r.fail("config_yaml/tools", f"universal tool '{req}' not declared")
            else:
                r.ok(f"config_yaml/tools/{req}", "present")

    # Skills list
    skills = data.get("skills", [])
    if not isinstance(skills, list) or len(skills) == 0:
        r.fail("config_yaml/skills", "must be a non-empty list")
        return

    all_required = UNIVERSAL_REQUIRED_SKILLS | AGENT_REQUIRED_SKILLS.get(r.agent, set())
    for req in sorted(all_required):
        if req not in skills:
            r.fail("config_yaml/skills", f"required skill '{req}' not declared")
        else:
            r.ok(f"config_yaml/skills/{req}", "present")


def check_agent_yaml(r: Reporter, agent_dir: Path):
    """Check the top-level <agent>.yaml stub file."""
    try:
        import yaml
    except ImportError:
        r.skip("agent_yaml", "pyyaml not installed")
        return

    stub = agent_dir.parent / f"{r.agent}.yaml"
    if not stub.exists():
        r.fail("agent_yaml", f"stub not found at {stub}")
        return

    try:
        yaml.safe_load(stub.read_text())
        r.ok("agent_yaml", f"{stub.name} parses")
    except yaml.YAMLError as exc:
        r.fail("agent_yaml", f"YAML parse error: {exc}")


def check_init_script(r: Reporter, scripts_dir: Path):
    """Verify init_<agent>.py exists and has no import-time syntax errors."""
    init = scripts_dir / f"init_{r.agent}.py"
    if not init.exists():
        r.fail("init_script", f"init_{r.agent}.py not found in scripts/")
        return

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(init)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        r.fail("init_script", result.stderr.strip())
    else:
        r.ok("init_script", f"init_{r.agent}.py compiles cleanly")


def check_shared_skills(r: Reporter, repo_root: Path):
    """Verify the shared/skills directory exists and skills have SKILL.md."""
    shared = repo_root / "dotfiles-ai" / "shared" / "skills"
    if not shared.exists():
        r.fail("shared_skills", "dotfiles-ai/shared/skills/ directory missing")
        return

    skill_dirs = [d for d in shared.iterdir() if d.is_dir() and not d.name.startswith(".")]
    if not skill_dirs:
        r.fail("shared_skills", "no skill sub-directories found")
        return

    missing_md = [d.name for d in skill_dirs if not (d / "SKILL.md").exists()]
    if missing_md:
        r.fail("shared_skills/SKILL.md", f"missing in: {missing_md}")
    else:
        r.ok("shared_skills/SKILL.md", f"{len(skill_dirs)} skills all have SKILL.md")


def check_skills_registry(r: Reporter, repo_root: Path):
    """Ensure skills/registry.json is valid and skills_count matches actual entries."""
    reg = repo_root / "dotfiles-ai" / "skills" / "registry.json"
    if not reg.exists():
        r.fail("skills_registry", "dotfiles-ai/skills/registry.json not found")
        return

    try:
        data = json.loads(reg.read_text())
    except json.JSONDecodeError as exc:
        r.fail("skills_registry", f"JSON parse error: {exc}")
        return

    declared = data.get("skills_count", -1)
    actual   = len(data.get("skills", []))
    if declared != actual:
        r.fail("skills_registry",
               f"skills_count={declared} but {actual} entries in 'skills' array")
    else:
        r.ok("skills_registry", f"{actual} skills, count matches")


def check_tool_configs(r: Reporter, tools_dir: Path):
    """Validate any JSON/YAML tool config files present for this agent."""
    patterns = [f"{r.agent}.json", f"{r.agent}.yaml", f"{r.agent}.yml"]
    found = False

    for pat in patterns:
        f = tools_dir / pat
        if not f.exists():
            continue
        found = True
        try:
            if f.suffix == ".json":
                json.loads(f.read_text())
            else:
                import yaml
                yaml.safe_load(f.read_text())
            r.ok("tool_config", f"{f.name} parses")
        except Exception as exc:
            r.fail("tool_config", f"{f.name}: {exc}")

    if not found:
        r.skip("tool_config", f"no tool config found for {r.agent} in tools/")


def check_windows_configs(r: Reporter, repo_root: Path):
    """Validate chezmoi private_dot_config entries relevant to this agent."""
    mapping = {
        "kilocode":  "private_dot_config/private_kilocode/config.json",
        "opencode":  "private_dot_config/private_opencode/config.yaml",
        "windsurf":  "private_dot_config/private_codeium/private_windsurf/global_rules.md",
    }
    path_str = mapping.get(r.agent)
    if not path_str:
        r.skip("windows_config", "no chezmoi config for this agent")
        return

    f = repo_root / path_str
    if not f.exists():
        r.fail("windows_config", f"{path_str} not found")
        return

    ext = f.suffix.lower()
    try:
        if ext == ".json":
            json.loads(f.read_text())
            r.ok("windows_config", f"{f.name} parses")
        elif ext in (".yaml", ".yml"):
            import yaml
            yaml.safe_load(f.read_text())
            r.ok("windows_config", f"{f.name} parses")
        else:
            # .md or other text — just check non-empty
            if f.stat().st_size > 0:
                r.ok("windows_config", f"{f.name} is non-empty")
            else:
                r.fail("windows_config", f"{f.name} is empty")
    except Exception as exc:
        r.fail("windows_config", f"{f.name}: {exc}")


# ──────────────────────────────── main ───────────────────────────────────────

def run_agent_checks(agent: str, repo_root: Path) -> Reporter:
    r = Reporter(agent)
    print(f"\n{'='*56}")
    print(f"  Validating: {agent.upper()}")
    print(f"{'='*56}")

    base_dir    = repo_root / "dotfiles-ai"
    agent_dir   = base_dir / "agents" / agent
    scripts_dir = base_dir / "scripts"
    tools_dir   = base_dir / "tools"

    if not agent_dir.exists():
        r.fail("agent_dir", f"dotfiles-ai/agents/{agent}/ directory missing")
        return r

    check_config_yaml(r, agent_dir)
    check_agent_yaml(r, agent_dir)
    check_init_script(r, scripts_dir)
    check_shared_skills(r, repo_root)
    check_skills_registry(r, repo_root)
    check_tool_configs(r, tools_dir)
    check_windows_configs(r, repo_root)

    return r


def main():
    parser = argparse.ArgumentParser(description="Validate AI agent skills")
    parser.add_argument("--agent",       required=True, help="Agent name to test")
    parser.add_argument("--repo-root",   default=".",   help="Path to repo root")
    parser.add_argument("--output-json", default=None,  help="Write JSON result to file")
    args = parser.parse_args()

    if args.agent not in AGENTS:
        print(f"Unknown agent '{args.agent}'. Valid: {AGENTS}", file=sys.stderr)
        sys.exit(2)

    start     = time.monotonic()
    repo_root = Path(args.repo_root).resolve()
    reporter  = run_agent_checks(args.agent, repo_root)
    elapsed   = time.monotonic() - start

    result = reporter.as_dict()
    result["elapsed_s"] = round(elapsed, 2)

    # Summary
    print(f"\n{'─'*56}")
    total = len(reporter.passed) + len(reporter.failed)
    print(
        f"  {reporter.agent}: "
        f"{len(reporter.passed)}/{total} checks passed "
        f"({len(reporter.skipped)} skipped) in {elapsed:.2f}s"
    )
    print(f"{'─'*56}")

    if args.output_json:
        Path(args.output_json).write_text(json.dumps(result, indent=2))
        print(f"\n  Results written to {args.output_json}")

    sys.exit(0 if reporter.success else 1)


if __name__ == "__main__":
    main()

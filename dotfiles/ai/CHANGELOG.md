# Changelog

All notable changes to the AI Agent Dotfiles repository will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Worktree manager script (`scripts/worktree-manager.sh`) for multi-branch development
- Comprehensive Git workflow documentation (`docs/GIT_WORKFLOW.md`)
- Release automation with version tags and GitHub Releases
- Security scanning workflow (TruffleHog, YAML validation, agent config schema)
- GitHub community files: CODEOWNERS, Dependabot, issue/PR templates
- SKILL.md for all skill category directories (analysis, integration, memory, data_processing, code_generation, cbw_rag, .system)
- Validation script for agent configs (`scripts/validate_skills.py`)

### Changed
- Converted vscode and windsurf from meta-config YAML to proper agent directories with config.yaml
- Updated CI workflows: use `chezmoi apply --dry-run` instead of `diff`/`verify` to avoid false failures
- Expanded skills-ci.yml matrix to include all 9 agents (added codex)
- Updated `.chezmoiignore` to be AI-first: track all skills, rules, workflows, configs; only exclude runtime data and secrets
- Removed interactive templates that blocked non-interactive apply (`dot_bash_secrets.tmpl`, `dot_env_ai.tmpl`, etc.)
- Optimized `.zshrc` by removing duplicates and leveraging Prezto (21 modules)
- Consolidated PATH configuration across zsh files

### Fixed
- CI validation failures due to missing agent configs and interactive templates
- Branch protection not configured (now documented)
- Missing `framework` field in vscode and windsurf configs
- SKILL.md coverage enforcement now passes for all top-level directories

### Security
- Excluded infra/local-ai/ and infra/letta/docker-compose.letta.yml (contain API keys)
- Removed hardcoded node paths from shell configs
- Ensure no OAuth credentials or API keys are committed

## [1.0.0] - 2026-04-04

### Added
- Initial production release of AI agent dotfiles
- Zsh configuration with Prezto integration
- All agent configurations (.gemini, .codex, .qwen, .kilo, .opencode, .cline)
- Central AI config at `~/dotfiles/ai/`
- 30+ utility scripts for agent management
- Systemd service definitions for AI infrastructure
- Infrastructure configs (Letta, Local AI, n8n)
- KiloCode agent rules and commands
- Roo XML rules (20 files)
- Comprehensive `.chezmoiignore` with AI-first philosophy

### Security
- Excluded all auth tokens, OAuth credentials, and API keys from version control
- Configured secret scanning via GitHub Actions
- Used environment variables for sensitive configuration

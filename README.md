# Dotfiles

AI-first dotfiles managed with [chezmoi](https://chezmoi.io).

## Quick Start

```bash
# Install chezmoi
curl -sfL https://get.chezmoi.io | sh

# Initialize and apply (one command restore)
~/bin/chezmoi init --apply https://github.com/cbwinslow/dotfiles.git
```

## What's Included

| Category | Contents |
|----------|----------|
| **Shell** | Bash/Zsh configs, aliases, functions, Starship prompt |
| **AI Agents** | 19 skills, 12 agent configs, workflows, memory system |
| **Docker** | Compose stacks (Traefik, PostgreSQL, monitoring, AI services) |
| **Infrastructure** | Ansible, Terraform, K8s, monitoring configs |
| **Editors** | LunarVim, code-server |
| **Services** | Systemd units, crontabs, Cloudflare tunnels |
| **Security** | SSH config, firewall rules, gitleaks |

## Structure

```
├── .chezmoi.toml.tmpl       # Machine-specific config generator
├── .chezmoiignore           # Files excluded from management
├── .chezmoidata.toml        # Shared data (package lists, versions)
├── .chezmoiversion          # Pinned chezmoi version
├── .gitleaks.toml           # Secret scanning config
├── dot_bashrc               # → ~/.bashrc
├── dot_zshrc                # → ~/.zshrc
├── dot_bash_aliases         # → ~/.bash_aliases
├── dot_bash_functions       # → ~/.bash_functions
├── dot_bash_secrets.tmpl    # → ~/.bash_secrets (secrets templated)
├── dot_env_ai.tmpl          # → ~/.env.ai (API keys templated)
├── dot_gitconfig            # → ~/.gitconfig
├── private_dot_ssh/         # → ~/.ssh/ (mode 0700)
├── private_dot_config/      # → ~/.config/
├── dotfiles-ai/             # → ~/dotfiles/ai/ (agent system)
├── infra/                   # → ~/infra/ (IaC)
├── docker/                  # → ~/docker/ (compose stacks)
├── scripts/                 # → ~/scripts/ (utilities)
├── procedures/              # → ~/procedures/ (runbooks)
├── systemd/                 # → ~/.config/systemd/user/
├── .chezmoiscripts/         # Bootstrap & lifecycle scripts
└── crontab.txt              # Crontab entries
```

## Restoration Flow

Running `chezmoi init --apply` triggers:

1. System package installation (apt)
2. Docker setup
3. AI model pulls (Ollama)
4. All dotfiles applied to ~/
5. CLI tools installed (starship, atuin, nvm, cargo)
6. Directory structure created
7. SSH key generation
8. Docker networks and image pulls
9. Crontab restoration
10. Systemd services enabled
11. AI agent symlinks and skill setup
12. Monitoring configuration

## Daily Use

```bash
# Edit a managed file
chezmoi edit ~/.bashrc

# See what would change
chezmoi diff

# Apply pending changes
chezmoi apply

# Add a new file to management
chezmoi add ~/.config/new-tool/config.yml

# Commit and push changes
cd ~/.local/share/chezmoi
git add -A && git commit -m "Update config" && git push
```

## Secrets

Secrets are managed via chezmoi templates with `promptStringOnce`:
- API keys (OpenRouter, Gemini, etc.) → prompted on init
- Database passwords → prompted on init
- SSH keys → generated on each machine, never stored in repo
- GitHub token → configured via `gh auth login`

## Machine Differences

The `.chezmoi.toml.tmpl` file prompts for machine-specific values:
- Hostname
- GPU availability
- Git email
- Username

Templates use `{{ if .has_gpu }}` blocks to conditionally include GPU-dependent configs.

## License

Personal dotfiles. Use at your own risk.

#!/usr/bin/env bash
# run_once_07-setup-ai-agents.sh
# Set up AI agent symlinks, skills, and configurations
set -euo pipefail

DOTFILES_AI="${HOME}/dotfiles/ai"

echo "==> Setting up AI agent ecosystem..."

# Ensure dotfiles/ai directory exists (should be applied by chezmoi first)
if [[ ! -d "$DOTFILES_AI" ]]; then
    echo "==> WARNING: ${DOTFILES_AI} not found. Run chezmoi apply first."
    exit 1
fi

# Create symlinks for AI skills (shared across agents)
SKILL_SYMLINKS=(
    "${HOME}/.openclaw/skills:${DOTFILES_AI}/skills"
    "${HOME}/.codex/skills:${DOTFILES_AI}/skills"
    "${HOME}/.gemini/skills:${DOTFILES_AI}/skills"
    "${HOME}/.config/opencode/skills:${DOTFILES_AI}/skills"
    "${HOME}/.config/ai:${DOTFILES_AI}"
)

for entry in "${SKILL_SYMLINKS[@]}"; do
    src="${entry%%:*}"
    dst="${entry##*:}"
    dir="$(dirname "$src")"

    mkdir -p "$dir"
    if [[ ! -L "$src" && ! -e "$src" ]]; then
        ln -s "$dst" "$src"
        echo "==> Created symlink: ${src} -> ${dst}"
    elif [[ -L "$src" ]]; then
        # Update existing symlink if target changed
        current_target="$(readlink "$src")"
        if [[ "$current_target" != "$dst" ]]; then
            ln -sf "$dst" "$src"
            echo "==> Updated symlink: ${src} -> ${dst}"
        fi
    fi
done

# Framework symlinks
FRAMEWORK_SYMLINKS=(
    "${HOME}/.cline:${DOTFILES_AI}/.cline"
    "${HOME}/.crewai:${DOTFILES_AI}/frameworks/crewai/config.yaml"
    "${HOME}/.langchain:${DOTFILES_AI}/frameworks/langchain/config.yaml"
    "${HOME}/.epstein_memory:${DOTFILES_AI}/packages/epstein_memory/config.yaml"
)

for entry in "${FRAMEWORK_SYMLINKS[@]}"; do
    src="${entry%%:*}"
    dst="${entry##*:}"
    if [[ ! -e "$src" && -e "$dst" ]]; then
        ln -s "$dst" "$src"
        echo "==> Created symlink: ${src} -> ${dst}"
    fi
done

# Run AI setup script if present
if [[ -f "${DOTFILES_AI}/setup.sh" ]]; then
    echo "==> Running AI setup script..."
    bash "${DOTFILES_AI}/setup.sh" || echo "==> WARNING: AI setup script had errors (non-fatal)"
fi

echo "==> AI agent ecosystem configured."

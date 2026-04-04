#!/bin/bash
set -euo pipefail

# AI Dotfiles Setup Script
# Bootstraps Gemini, Letta, and other AI tools from ~/dotfiles/ai

echo "[*] Setting up AI environment..."

# 1. Gemini Configuration
echo "[*] Configuring Gemini CLI..."
mkdir -p ~/.gemini
ln -sf ~/dotfiles/ai/gemini/GEMINI.md ~/.gemini/GEMINI.md
ln -sf ~/dotfiles/ai/gemini/settings.json ~/.gemini/settings.json

# 2. Letta Memory Skill
echo "[*] Installing Letta Memory skill..."
SKILL_SRC="$HOME/dotfiles/ai/gemini/skills/letta-memory"
SKILL_PKG="$HOME/dotfiles/ai/gemini/skills/letta-memory.skill"

if [ -d "$SKILL_SRC" ]; then
    if command -v zip >/dev/null 2>&1; then
        cd "$SKILL_SRC" && zip -r "$SKILL_PKG" . >/dev/null
        gemini skills install "$SKILL_PKG" --scope user || echo "[!] Failed to install skill (is Gemini CLI installed?)"
    else
        echo "[!] 'zip' command not found. Skipping skill packaging."
    fi
else
    echo "[!] Skill source not found at $SKILL_SRC"
fi

# 3. Universal Mandates (Optional: copy to other agents if needed)
# cp ~/dotfiles/ai/shared/CORE_MANDATES.md ~/.cline/rules.md
# cp ~/dotfiles/ai/shared/CORE_MANDATES.md ~/.opencode/instructions.md

echo "[*] AI setup complete. Don't forget to run '/skills reload' in Gemini!"

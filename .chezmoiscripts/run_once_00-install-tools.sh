#!/usr/bin/env bash
# run_once_00-install-tools.sh
# Install CLI tools not available via apt
set -euo pipefail

BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"

# --- Starship prompt ---
if ! command -v starship &>/dev/null; then
    echo "==> Installing Starship prompt..."
    curl -sS https://starship.rs/install.sh | sh -s -- -y -b "$BIN_DIR"
fi

# --- Atuin shell history ---
if ! command -v atuin &>/dev/null; then
    echo "==> Installing Atuin..."
    curl --proto '=https' --tlsv1.2 -LsSf https://setup.atuin.sh | sh
fi

# --- NVM (Node Version Manager) ---
if [[ ! -d "${HOME}/.nvm" ]]; then
    echo "==> Installing NVM..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    export NVM_DIR="${HOME}/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    nvm install --lts
fi

# --- Rust/Cargo ---
if ! command -v cargo &>/dev/null; then
    echo "==> Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "${HOME}/.cargo/env"
fi

# --- pipx ---
if ! command -v pipx &>/dev/null; then
    echo "==> Installing pipx..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
fi

# --- Homebrew (Linux) ---
if ! command -v brew &>/dev/null; then
    echo "==> Installing Homebrew..."
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" 2>/dev/null || true
fi

echo "==> CLI tools installed."

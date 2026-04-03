#!/usr/bin/env bash
# run_once_02-setup-ssh.sh
# Generate SSH key if missing and set permissions
set -euo pipefail

SSH_DIR="${HOME}/.ssh"
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

# Generate ed25519 key if missing
if [[ ! -f "${SSH_DIR}/id_ed25519" ]]; then
    echo "==> Generating SSH key pair..."
    ssh-keygen -t ed25519 -C "{{ .email | default "cbwinslow@$(hostname)" }}" -f "${SSH_DIR}/id_ed25519" -N ""
    echo "==> SSH public key:"
    cat "${SSH_DIR}/id_ed25519.pub"
else
    echo "==> SSH key already exists."
fi

# Ensure correct permissions
chmod 600 "${SSH_DIR}/id_ed25519" 2>/dev/null || true
chmod 644 "${SSH_DIR}/id_ed25519.pub" 2>/dev/null || true
chmod 600 "${SSH_DIR}/authorized_keys" 2>/dev/null || true
chmod 644 "${SSH_DIR}/known_hosts" 2>/dev/null || true

echo "==> SSH setup complete."

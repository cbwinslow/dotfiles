#!/usr/bin/env bash
# run_once_06-setup-systemd.sh
# Enable user systemd services
set -euo pipefail

SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"

echo "==> Enabling user systemd services..."

# Reload systemd user daemon
systemctl --user daemon-reload 2>/dev/null || true

# Enable and start all user services
for service_file in "${SYSTEMD_USER_DIR}"/*.service; do
    if [[ -f "$service_file" ]]; then
        service_name="$(basename "$service_file")"
        echo "==> Enabling ${service_name}..."
        systemctl --user enable "$service_name" 2>/dev/null || true
        systemctl --user start "$service_name" 2>/dev/null || true
    fi
done

# Enable linger so user services start at boot
loginctl enable-linger "$USER" 2>/dev/null || true

echo "==> Systemd user services configured."

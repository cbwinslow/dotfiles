#!/usr/bin/env bash
# run_once_05-setup-crontabs.sh
# Restore crontab entries from crontab.txt
set -euo pipefail

CRONTAB_FILE="${HOME}/.local/share/chezmoi/crontab.txt"

if [[ -f "$CRONTAB_FILE" ]]; then
    echo "==> Restoring crontab entries..."
    # Merge with existing crontab (non-destructive)
    (crontab -l 2>/dev/null || true; cat "$CRONTAB_FILE") | sort -u | crontab -
    echo "==> Crontab restored."
else
    echo "==> No crontab.txt found, skipping."
fi

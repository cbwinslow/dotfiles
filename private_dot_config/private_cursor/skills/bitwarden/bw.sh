#!/bin/bash
# Bitwarden CLI Wrapper for AI Agents
# Integrates with bitwarden_secrets skill
# Supports non-interactive unlock via ~/dotfiles/secrets/.bw_master_password

SKILL_DIR="$HOME/dotfiles/ai/skills/bitwarden_secrets"
PASS_FILE="$HOME/dotfiles/secrets/.bw_master_password"

# Check if system bw is available (snap/npm)
if command -v bw &> /dev/null; then
    SYSTEM_BW="bw"
elif [ -x /snap/bin/bw ]; then
    SYSTEM_BW="/snap/bin/bw"
elif [ -x /usr/local/bin/bw ]; then
    SYSTEM_BW="/usr/local/bin/bw"
else
    echo "Error: Bitwarden CLI not found. Install with:"
    echo "  sudo snap install bw"
    exit 1
fi

# Non-interactive unlock using stored password file
auto_unlock() {
    if [ -f "$PASS_FILE" ]; then
        chmod 600 "$PASS_FILE" 2>/dev/null || true
        export BW_SESSION=$($SYSTEM_BW unlock --raw < "$PASS_FILE" 2>/dev/null)
        return $?
    fi
    return 1
}

# Function to ensure vault is unlocked
ensure_unlocked() {
    if ! $SYSTEM_BW status | grep -q '"status":"unlocked"'; then
        if [ -z "$BW_SESSION" ]; then
            # Try non-interactive unlock first
            if auto_unlock; then
                return 0
            fi
            echo "Vault locked. Setting BW_SESSION..."
            export BW_SESSION=$($SYSTEM_BW unlock --raw)
        fi
    fi
}

# Main command handler
case "${1:-}" in
    unlock)
        # Try non-interactive first
        if [ -f "$PASS_FILE" ]; then
            chmod 600 "$PASS_FILE" 2>/dev/null || true
            export BW_SESSION=$($SYSTEM_BW unlock --raw < "$PASS_FILE" 2>/dev/null)
        else
            export BW_SESSION=$($SYSTEM_BW unlock --raw)
        fi
        echo "Vault unlocked. BW_SESSION set."
        ;;
    lock)
        $SYSTEM_BW lock
        unset BW_SESSION
        echo "Vault locked."
        ;;
    status)
        $SYSTEM_BW status
        ;;
    get)
        ensure_unlocked
        $SYSTEM_BW get "${2:-password}" "${3:-}"
        ;;
    list)
        ensure_unlocked
        $SYSTEM_BW list items --search "${2:-}"
        ;;
    search)
        ensure_unlocked
        $SYSTEM_BW list items --search "${2:-}"
        ;;
    env|setup)
        ensure_unlocked
        # Source the shell loader for AI agents
        if [ -f "$SKILL_DIR/shell_loader.sh" ]; then
            source "$SKILL_DIR/shell_loader.sh"
            load_api_keys
        else
            echo "Error: shell_loader.sh not found"
            exit 1
        fi
        ;;
    session)
        ensure_unlocked
        echo "export BW_SESSION='$BW_SESSION'"
        ;;
    interactive)
        ensure_unlocked
        echo "Bitwarden Interactive Mode"
        echo "Available commands: unlock, lock, status, get, list, search, env, session"
        ;;
    *)
        # Pass through to system bw
        $SYSTEM_BW "$@"
        ;;
esac

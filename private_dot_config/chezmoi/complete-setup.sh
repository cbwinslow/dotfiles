#!/bin/bash
# Complete chezmoi setup script
# Run this on a new machine after: chezmoi init https://github.com/cbwinslow/dotfiles

set -e

echo "========================================="
echo "  Chezmoi Complete Setup"
echo "========================================="
echo ""

# 1. Apply chezmoi config
echo "1. Applying chezmoi configuration..."
chezmoi apply --verbose
echo "✓ Chezmoi applied"
echo ""

# 2. Set up age encryption
echo "2. Setting up age encryption..."
if [ ! -f "$HOME/.config/chezmoi/key.txt" ]; then
    echo "⚠ Age key not found! Restore from Bitwarden:"
    echo "   1. bw login"
    echo "   2. bw get item 'chezmoi-age-key-$(hostname)'"
    echo "   3. Save the key to ~/.config/chezmoi/key.txt"
    echo "   4. chmod 600 ~/.config/chezmoi/key.txt"
else
    echo "✓ Age key found"
fi
echo ""

# 3. Restore GPG keys
echo "3. Restoring GPG keys..."
if [ -f "$HOME/.config/chezmoi/restore-gpg-keys.sh" ]; then
    bash "$HOME/.config/chezmoi/restore-gpg-keys.sh"
else
    echo "⚠ GPG restore script not found, skipping"
fi
echo ""

# 4. Set up Bitwarden
echo "4. Setting up Bitwarden..."
if command -v bw &> /dev/null; then
    if ! bw status 2>/dev/null | grep -q '"status":"unlocked"'; then
        echo "Please unlock Bitwarden: bw login"
    else
        echo "✓ Bitwarden unlocked"
    fi
else
    echo "⚠ Bitwarden CLI not installed"
fi
echo ""

# 5. Set up SSH
echo "5. Setting up SSH..."
if [ -f "$HOME/.ssh/id_ed25519" ]; then
    echo "✓ SSH key exists"
else
    echo "⚠ SSH key not found, restore from Bitwarden or generate new"
fi
echo ""

# 6. Verify everything
echo "6. Verification..."
echo "   GPG keys: $(gpg --list-secret-keys 2>/dev/null | grep -c 'sec' || echo 0)"
echo "   SSH keys: $(ls ~/.ssh/id_* 2>/dev/null | wc -l || echo 0)"
echo "   Age key: $(test -f ~/.config/chezmoi/key.txt && echo '✓' || echo '✗')"
echo "   Bitwarden: $(bw status 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin)["status"])' 2>/dev/null || echo 'unknown')"
echo ""

echo "========================================="
echo "  Setup Complete!"
echo "========================================="

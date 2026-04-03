#!/bin/bash
# Restore GPG keys from encrypted chezmoi files
# Run this on a new machine after chezmoi apply

set -e

GPG_DIR="$HOME/.gnupg"
ENCRYPTED_DIR="$HOME/.local/share/chezmoi/private_dot_gnupg"
AGE_KEY="$HOME/.config/chezmoi/key.txt"

echo "=== Restoring GPG keys ==="

if [ ! -f "$AGE_KEY" ]; then
    echo "✗ Age key not found at $AGE_KEY"
    echo "  Restore it from Bitwarden first (item: chezmoi-age-key-<hostname>)"
    exit 1
fi

# Create .gnupg directory
mkdir -p "$GPG_DIR/openpgp-revocs.d"
chmod 700 "$GPG_DIR"

# Decrypt and restore
echo "Decrypting secret keys..."
age -d -i "$AGE_KEY" "$ENCRYPTED_DIR/encrypted_secret_keys.age" | gpg --import 2>&1

echo "Decrypting public keys..."
age -d -i "$AGE_KEY" "$ENCRYPTED_DIR/encrypted_public_keys.age" | gpg --import 2>&1

echo "Decrypting revocation certificate..."
age -d -i "$AGE_KEY" "$ENCRYPTED_DIR/private_openpgp-revocs.d/encrypted_revocation_cert.age" > "$GPG_DIR/openpgp-revocs.d/$(gpg --list-keys --with-colons 2>/dev/null | grep '^fpr' | head -1 | cut -d: -f10).rev" 2>/dev/null

echo "Decrypting trust database..."
age -d -i "$AGE_KEY" "$ENCRYPTED_DIR/encrypted_trustdb.age" > "$GPG_DIR/trustdb.gpg" 2>/dev/null

echo ""
echo "=== GPG keys restored ==="
gpg --list-secret-keys --keyid-format long 2>/dev/null

echo ""
echo "=== Configure git to use GPG key ==="
GPG_FINGERPRINT=$(gpg --list-secret-keys --with-colons 2>/dev/null | grep '^fpr' | head -1 | cut -d: -f10)
git config --global user.signingkey "$GPG_FINGERPRINT"
git config --global commit.gpgsign true
echo "Git configured with GPG key: $GPG_FINGERPRINT"

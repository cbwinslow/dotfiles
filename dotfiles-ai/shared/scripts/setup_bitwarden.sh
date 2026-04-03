#!/bin/bash
# Bitwarden Setup Script for AI Agents
# Location: ~/dotfiles/ai/scripts/setup_bitwarden.sh

set -e

echo "=============================================="
echo "  Bitwarden Setup for AI Agents"
echo "=============================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Step 1: Check Bitwarden CLI installation
echo "Step 1: Checking Bitwarden CLI..."
echo "-------------------------------------------"
if command -v bw &>/dev/null; then
    BW_VERSION=$(bw --version 2>&1)
    log_info "Bitwarden CLI installed: $BW_VERSION"
else
    log_error "Bitwarden CLI not found"
    echo "Install with:"
    echo "  curl -Ls https://github.com/bitwarden/clients/releases/download/cli-v2025.9.0/bw-linux-2025.9.0.zip -o /tmp/bw.zip"
    echo "  unzip /tmp/bw.zip -d /tmp/bw-extract"
    echo "  sudo cp /tmp/bw-extract/bw /usr/local/bin/bw"
    exit 1
fi

# Step 2: Check authentication
echo ""
echo "Step 2: Checking authentication..."
echo "-------------------------------------------"
BW_STATUS=$(bw status 2>&1 | jq -r '.status' 2>/dev/null || echo "unauthenticated")

case $BW_STATUS in
    "unauthenticated")
        log_warn "Not authenticated with Bitwarden"
        echo ""
        echo "Choose authentication method:"
        echo "  1. User API Key (bypasses 2FA, requires unlock)"
        echo "  2. Machine Account Access Token (bypasses 2FA, NO unlock!)"
        echo "  3. Email + Password (interactive, requires 2FA)"
        echo ""
        read -p "Choose option (1, 2, or 3): " auth_choice
        
        case $auth_choice in
            1)
                log_info "User API Key authentication"
                echo ""
                echo "Get your API key from: https://vault.bitwarden.com/#/settings/api-key"
                echo ""
                read -p "Enter Client ID: " BW_CLIENTID
                read -s -p "Enter Client Secret: " BW_CLIENTSECRET
                echo ""
                
                export BW_CLIENTID
                export BW_CLIENTSECRET
                
                bw login --apikey
                log_info "Logged in with API key. You'll need to unlock the vault."
                ;;
            2)
                log_info "Machine Account Access Token"
                echo ""
                echo "Create a machine account at: https://vault.bitwarden.com/#/secrets"
                echo "1. Go to Secrets Manager"
                echo "2. Navigate to Machine Accounts"
                echo "3. Create new account"
                echo "4. Generate access token"
                echo ""
                read -p "Enter Access Token: " BW_ACCESS_TOKEN
                echo ""
                
                export BW_ACCESS_TOKEN
                
                bw login --accesstoken
                log_info "Logged in with access token. No unlock required!"
                ;;
            3)
                log_info "Starting interactive login..."
                bw login
                ;;
            *)
                log_error "Invalid option"
                exit 1
                ;;
        esac
        ;;
    "locked")
        log_info "Authenticated but vault is locked"
        ;;
    "unlocked")
        log_info "Vault is unlocked and ready"
        ;;
    *)
        log_warn "Unknown status: $BW_STATUS"
        ;;
esac

# Step 3: Unlock vault
echo ""
echo "Step 3: Unlocking vault..."
echo "-------------------------------------------"
BW_STATUS=$(bw status 2>&1 | jq -r '.status' 2>/dev/null || echo "unauthenticated")

if [ "$BW_STATUS" != "unlocked" ]; then
    echo ""
    echo "Enter your master password to unlock the vault:"
    read -s -p "Master Password: " BW_PASSWORD
    echo ""
    
    export BW_PASSWORD
    eval $(bw unlock --passwordenv BW_PASSWORD --raw)
    export BW_SESSION
    
    log_info "Vault unlocked successfully"
else
    log_info "Vault already unlocked"
fi

# Step 4: Test access
echo ""
echo "Step 4: Testing access..."
echo "-------------------------------------------"
ITEM_COUNT=$(bw list items --session "$BW_SESSION" 2>/dev/null | jq 'length' || echo "0")
log_info "Found $ITEM_COUNT items in vault"

if [ "$ITEM_COUNT" -gt 0 ]; then
    echo ""
    echo "Sample items:"
    bw list items --session "$BW_SESSION" | jq -r '.[:5] | .[].name' | while read -r item; do
        echo "  - $item"
    done
fi

# Step 5: Add shell integration
echo ""
echo "Step 5: Setting up shell integration..."
echo "-------------------------------------------"
RC_FILE="$HOME/.zshrc"
if [ ! -f "$RC_FILE" ]; then
    RC_FILE="$HOME/.bashrc"
fi

if grep -q "bw-unlock" "$RC_FILE" 2>/dev/null; then
    log_warn "Bitwarden shortcuts already in $RC_FILE"
else
    echo "" >> "$RC_FILE"
    cat >> "$RC_FILE" << 'EOF'

# Bitwarden shortcuts
alias bw-unlock='eval $(bw unlock --raw) && export BW_SESSION && echo "Vault unlocked"'
alias bw-lock='bw lock && unset BW_SESSION && echo "Vault locked"'
alias bw-status='bw status | jq .'
bw-get() { bw get item "$1" --session "$BW_SESSION" | jq -r '.login.password // .fields[0].value // empty'; }
bw-list() { bw list items --session "$BW_SESSION" | jq -r '.[].name'; }
bw-env() {
    local env_file="${1:-.env}"; shift
    $HOME/dotfiles/ai/skills/bitwarden/bitwarden.sh populate-env --env-file "$env_file" --secrets "$@"
}
EOF
    log_info "Added Bitwarden shortcuts to $RC_FILE"
    log_info "Run 'source $RC_FILE' to load them"
fi

# Step 6: Create example .env template
echo ""
echo "Step 6: Creating example .env template..."
echo "-------------------------------------------"
EXAMPLE_ENV="$HOME/dotfiles/ai/.env.example"
cat > "$EXAMPLE_ENV" << 'EOF'
# Example .env file - populate from Bitwarden
# Run: bw-env .env "OpenRouter API Key" "Letta API Key" "Database Password"

OPENROUTER_API_KEY=
LETTA_API_KEY=
LETTA_SERVER_URL=http://localhost:8283
DATABASE_URL=
EOF
log_info "Created example at $EXAMPLE_ENV"

# Summary
echo ""
echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "Quick Reference:"
echo "  bw-unlock              - Unlock vault"
echo "  bw-lock                - Lock vault"
echo "  bw-list                - List secrets"
echo "  bw-get <name>          - Get secret by name"
echo "  bw-env .env <secrets>  - Populate .env file"
echo ""
echo "Example usage:"
echo "  bw-unlock"
echo "  bw-env .env \"OpenRouter API Key\" \"Letta API Key\""
echo "  cat .env"
echo "  bw-lock"
echo ""
echo "Documentation: ~/dotfiles/ai/skills/bitwarden/README.md"
echo ""

log_info "Bitwarden integration ready!"

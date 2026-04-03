#!/bin/bash
# Complete System Setup Script
# Sets up the entire Agent AI Skills System
# Location: ~/dotfiles/ai/scripts/setup_complete_system.py

set -e

AI_ROOT="$HOME/dotfiles/ai"
SCRIPTS_DIR="$AI_ROOT/scripts"

echo "=============================================="
echo "  Agent AI Skills System - Complete Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Install Letta Integration Package
echo ""
echo "Step 1: Installing Letta Integration Package..."
echo "-------------------------------------------"
cd "$AI_ROOT/packages/letta_integration"
pip install -e .
log_info "Letta Integration Package installed"

# Step 2: Create Symlinks
echo ""
echo "Step 2: Creating Symlinks..."
echo "-------------------------------------------"
bash "$SCRIPTS_DIR/create_symlinks.sh"

# Step 3: Setup Shell Integration
echo ""
echo "Step 3: Setting Up Shell Integration..."
echo "-------------------------------------------"

# Check if shell integration is already in rc file
RC_FILE="$HOME/.zshrc"
if [ ! -f "$RC_FILE" ]; then
    RC_FILE="$HOME/.bashrc"
fi

if grep -q "AI_SKILLS_ROOT" "$RC_FILE" 2>/dev/null; then
    log_warn "Shell integration already exists in $RC_FILE"
else
    echo "" >> "$RC_FILE"
    echo "# AI Skills System Integration (added $(date))" >> "$RC_FILE"
    echo "source \$HOME/dotfiles/ai/scripts/shell_integration.sh" >> "$RC_FILE"
    log_info "Shell integration added to $RC_FILE"
    log_info "Restart your shell or run: source $RC_FILE"
fi

# Step 4: Set Environment Variables
echo ""
echo "Step 4: Environment Variables..."
echo "-------------------------------------------"

# Create .env file if it doesn't exist
ENV_FILE="$AI_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << EOF
# AI Skills System Environment Variables
# Copy these to your shell profile or use with direnv

export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_API_KEY="your-letta-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"

# PostgreSQL (for Agent Memory backup)
export PG_HOST="localhost"
export PG_PORT="5432"
export PG_DATABASE="letta"
export PG_USER="cbwinslow"
export PG_PASSWORD="your-password"
EOF
    log_info "Created .env file at $ENV_FILE"
    log_warn "Please update the .env file with your actual API keys"
else
    log_warn ".env file already exists at $ENV_FILE"
fi

# Step 5: Validate Configuration
echo ""
echo "Step 5: Validating Configuration..."
echo "-------------------------------------------"
python3 "$SCRIPTS_DIR/validate_configs.py" --verbose || true

# Step 6: Create Required Directories
echo ""
echo "Step 6: Creating Required Directories..."
echo "-------------------------------------------"
mkdir -p "$AI_ROOT/backups/letta"
mkdir -p "$AI_ROOT/.cline/data"
mkdir -p "$AI_ROOT/logs"
log_info "Directories created"

# Summary
echo ""
echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "Next Steps:"
echo "  1. Update ~/.dotfiles/ai/.env with your API keys"
echo "  2. Restart your shell or run: source $RC_FILE"
echo "  3. Start Letta server: letta server"
echo "  4. Test with: letta-health"
echo ""
echo "Quick Reference:"
echo "  ai-help      - Show all commands"
echo "  ai-validate  - Validate configurations"
echo "  ai-health    - Full system health check"
echo ""

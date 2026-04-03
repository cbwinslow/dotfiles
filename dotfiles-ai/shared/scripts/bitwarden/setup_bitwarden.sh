#!/bin/bash
#
# Bitwarden Setup Script
# Sets up Bitwarden CLI and configures environment for AI agents
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BITWARDEN_CLI_VERSION="1.28.1"
BITWARDEN_INSTALL_DIR="/usr/local/bin"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root. Running as root may cause permission issues."
   exit 1
fi

# Check if Bitwarden CLI is already installed
check_bitwarden_cli() {
    if command -v bw &> /dev/null; then
        local version=$(bw --version)
        log_info "Bitwarden CLI is already installed: $version"
        return 0
    else
        log_info "Bitwarden CLI is not installed. Installing..."
        return 1
    fi
}

# Install Bitwarden CLI
install_bitwarden_cli() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Installing Bitwarden CLI for Linux..."
        
        # Check if we have sudo access
        if ! command -v sudo &> /dev/null; then
            log_error "sudo is required to install Bitwarden CLI"
            exit 1
        fi
        
        # Install using package manager
        if command -v apt-get &> /dev/null; then
            log_info "Using apt-get for installation..."
            sudo apt-get update
            sudo apt-get install -y bitwarden-cli
        elif command -v yum &> /dev/null; then
            log_info "Using yum for installation..."
            sudo yum install -y bitwarden-cli
        elif command -v dnf &> /dev/null; then
            log_info "Using dnf for installation..."
            sudo dnf install -y bitwarden-cli
        else
            log_warning "No supported package manager found. Installing manually..."
            install_manually
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Installing Bitwarden CLI for macOS..."
        
        if ! command -v brew &> /dev/null; then
            log_error "Homebrew is required to install Bitwarden CLI on macOS"
            exit 1
        fi
        
        brew install bitwarden-cli
    else
        log_warning "Unsupported OS. Installing manually..."
        install_manually
    fi
}

# Manual installation
install_manually() {
    log_info "Downloading Bitwarden CLI manually..."
    
    # Create temporary directory
    local tmp_dir=$(mktemp -d)
    cd "$tmp_dir"
    
    # Download the latest release
    local download_url="https://github.com/bitwarden/cli/releases/latest/download/bw-linux-amd64"
    local output_file="bw"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        download_url="https://github.com/bitwarden/cli/releases/latest/download/bw-darwin-amd64"
    fi
    
    curl -L -o "$output_file" "$download_url"
    
    # Make executable and move to install directory
    chmod +x "$output_file"
    sudo mv "$output_file" "$BITWARDEN_INSTALL_DIR/bw"
    
    # Clean up
    cd -
    rm -rf "$tmp_dir"
    
    log_success "Bitwarden CLI installed manually"
}

# Configure Bitwarden
configure_bitwarden() {
    log_info "Configuring Bitwarden for AI agents..."
    
    # Check if we have a Bitwarden session
    if [[ -z "${BW_SESSION}" ]]; then
        log_warning "BW_SESSION environment variable is not set."
        log_info "You need to authenticate with Bitwarden first:"
        log_info "  bw login"
        log_info "  bw unlock"
        log_info "Then set the BW_SESSION variable:"
        log_info "  export BW_SESSION=$(bw unlock --raw)"
    else
        log_info "BW_SESSION is set. Bitwarden is ready to use."
    fi
    
    # Create configuration directory
    local config_dir="$HOME/.config/bitwarden"
    mkdir -p "$config_dir"
    
    # Create example configuration
    cat > "$config_dir/ai-agents-config.json" << EOF
{
    "ai_agents": {
        "enabled": true,
        "auto_populate_env": true,
        "vaults": {
            "personal": "Personal",
            "work": "Work",
            "shared": "Shared"
        },
        "credentials": {
            "api_keys": ["OpenAI API Key", "Anthropic API Key", "Google AI API Key"],
            "database": ["Database Password", "DB Connection String"],
            "services": ["Service A Credentials", "Service B Token"]
        }
    }
}
EOF
    
    log_success "Bitwarden configuration created"
}

# Create helper functions
create_helper_functions() {
    log_info "Creating Bitwarden helper functions..."
    
    cat > "$HOME/.bitwarden_helpers.sh" << 'EOF'
# Bitwarden Helper Functions for AI Agents
# Source this file in your shell configuration

# Get API key from Bitwarden
bw_get_api_key() {
    local key_name=$1
    local vault_name=${2:-"Personal"}
    
    if ! command -v bw &> /dev/null; then
        echo "Error: Bitwarden CLI not found" >&2
        return 1
    fi
    
    # Try to get the key
    local result=$(bw get password "$key_name" --vault "$vault_name" 2>/dev/null)
    
    if [[ $? -ne 0 ]]; then
        echo "Error: Could not find API key '$key_name' in vault '$vault_name'" >&2
        return 1
    fi
    
    echo "$result"
}

# Populate .env file with credentials
bw_populate_env() {
    local env_file=$1
    local credentials_file=$2
    
    if ! command -v bw &> /dev/null; then
        echo "Error: Bitwarden CLI not found" >&2
        return 1
    fi
    
    if [[ ! -f "$credentials_file" ]]; then
        echo "Error: Credentials file not found: $credentials_file" >&2
        return 1
    fi
    
    # Read credentials file (JSON format)
    local credentials
    credentials=$(jq -c '.[]' "$credentials_file")
    
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to parse credentials file" >&2
        return 1
    fi
    
    # Process each credential
    while IFS= read -r cred; do
        local name=$(echo "$cred" | jq -r '.name')
        local vault=$(echo "$cred" | jq -r '.vault // "Personal"')
        local env_var=$(echo "$cred" | jq -r '.env_var // ""')
        
        if [[ -z "$env_var" ]]; then
            # Generate env var name from credential name
            env_var=$(echo "$name" | tr '[:lower:]-' '[:upper:]_' | sed 's/[^A-Z0-9_]/_/g')
        fi
        
        # Get the credential
        local value=$(bw get password "$name" --vault "$vault" 2>/dev/null)
        
        if [[ $? -eq 0 ]]; then
            # Add to .env file
            echo "$env_var=$value" >> "$env_file"
            echo "Added: $env_var"
        else
            echo "Warning: Could not find $name" >&2
        fi
    done <<< "$credentials"
    
    echo "Successfully populated $env_file"
}

# Search credentials
bw_search() {
    local query=$1
    local search_type=${2:-"all"}
    
    if ! command -v bw &> /dev/null; then
        echo "Error: Bitwarden CLI not found" >&2
        return 1
    fi
    
    # Perform search
    local result=$(bw search "$query" 2>/dev/null)
    
    if [[ $? -ne 0 ]]; then
        echo "Error: Search failed" >&2
        return 1
    fi
    
    echo "$result"
}

# List vaults
bw_list_vaults() {
    if ! command -v bw &> /dev/null; then
        echo "Error: Bitwarden CLI not found" >&2
        return 1
    fi
    
    # Bitwarden CLI doesn't have a direct vault listing command
    # Return common vault names
    echo "Personal"
    echo "Work"
    echo "Shared"
    echo "Custom"
}
EOF
    
    log_success "Helper functions created"
    log_info "To use these functions, add this to your shell configuration:"
    log_info "  source ~/.bitwarden_helpers.sh"
}

# Create example credentials file
create_example_credentials() {
    log_info "Creating example credentials file..."
    
    cat > "$HOME/.bitwarden_credentials.json" << EOF
[
    {
        "name": "OpenAI API Key",
        "vault": "Personal",
        "env_var": "OPENAI_API_KEY"
    },
    {
        "name": "Anthropic API Key",
        "vault": "Personal",
        "env_var": "ANTHROPIC_API_KEY"
    },
    {
        "name": "Google AI API Key",
        "vault": "Personal",
        "env_var": "GOOGLE_AI_API_KEY"
    },
    {
        "name": "Database Password",
        "vault": "Work",
        "env_var": "DB_PASSWORD"
    }
]
EOF
    
    log_success "Example credentials file created"
    log_info "Edit this file to match your Bitwarden credentials:"
    log_info "  $HOME/.bitwarden_credentials.json"
}

# Create usage documentation
create_documentation() {
    log_info "Creating usage documentation..."
    
    cat > "$HOME/.bitwarden_usage.md" << 'EOF'
# Bitwarden Usage for AI Agents

## Quick Start

1. **Install Bitwarden CLI:**
   ```bash
   ./scripts/bitwarden/setup_bitwarden.sh
   ```

2. **Authenticate with Bitwarden:**
   ```bash
   bw login
   bw unlock
   export BW_SESSION=$(bw unlock --raw)
   ```

3. **Populate .env file:**
   ```bash
   source ~/.bitwarden_helpers.sh
   bw_populate_env .env ~/.bitwarden_credentials.json
   ```

## Available Functions

### bw_get_api_key
Get an API key from Bitwarden.

**Usage:**
```bash
bw_get_api_key "OpenAI API Key" "Personal"
```

**Parameters:**
- `key_name`: Name of the API key
- `vault_name`: Vault name (optional, default: "Personal")

### bw_populate_env
Populate a .env file with credentials.

**Usage:**
```bash
bw_populate_env .env ~/.bitwarden_credentials.json
```

**Parameters:**
- `env_file`: Path to .env file
- `credentials_file`: Path to JSON credentials file

### bw_search
Search for credentials.

**Usage:**
```bash
bw_search "api" "name"
```

**Parameters:**
- `query`: Search query
- `search_type`: "name", "tag", or "all" (optional)

### bw_list_vaults
List available vaults.

**Usage:**
```bash
bw_list_vaults
```

## Example Credentials File

```json
[
    {
        "name": "OpenAI API Key",
        "vault": "Personal",
        "env_var": "OPENAI_API_KEY"
    },
    {
        "name": "Database Password",
        "vault": "Work",
        "env_var": "DB_PASSWORD"
    }
]
```

## Environment Variables

- `BW_SESSION`: Bitwarden session token
- `BW_CLIENT_ID`: Bitwarden client ID (if using OAuth)
- `BW_CLIENT_SECRET`: Bitwarden client secret (if using OAuth)

## Troubleshooting

### Common Issues

1. **Authentication Failed:**
   - Make sure you're logged in: `bw login`
   - Unlock your vault: `bw unlock`
   - Check your session: `bw status`

2. **Credential Not Found:**
   - Verify the credential name in Bitwarden
   - Check the correct vault is being used
   - Ensure the credential exists

3. **Permission Denied:**
   - Check file permissions on .env file
   - Verify Bitwarden CLI has necessary permissions

### Getting Help

- Bitwarden CLI documentation: https://bitwarden.com/help/cli/
- Bitwarden support: https://bitwarden.com/help/

EOF
    
    log_success "Usage documentation created"
}

# Main installation function
main() {
    log_info "Starting Bitwarden setup for AI agents..."
    log_info "This script will install Bitwarden CLI and configure it for use with AI agents."
    
    # Check if Bitwarden CLI is installed
    if ! check_bitwarden_cli; then
        install_bitwarden_cli
    fi
    
    # Configure Bitwarden
    configure_bitwarden
    
    # Create helper functions
    create_helper_functions
    
    # Create example files
    create_example_credentials
    create_documentation
    
    log_success "Bitwarden setup completed successfully!"
    log_info "Next steps:"
    log_info "1. Authenticate with Bitwarden: bw login && bw unlock"
    log_info "2. Set session token: export BW_SESSION=\$(bw unlock --raw)"
    log_info "3. Populate .env file: bw_populate_env .env ~/.bitwarden_credentials.json"
    log_info "4. Add to shell config: source ~/.bitwarden_helpers.sh"
}

# Run main function
main "$@"
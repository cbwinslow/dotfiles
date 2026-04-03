"""
Bitwarden Secrets Helper for AI Agents

Securely retrieves API keys and secrets from Bitwarden vault.
Uses Bitwarden CLI (bw) for secure access.
"""

import subprocess
import os
import json
from typing import Optional, Dict, Any

# Import advanced search capabilities
try:
    from advanced_search import BitwardenAdvancedSearch, find_api_key as advanced_find_key
except ImportError:
    advanced_find_key = None


class BitwardenSecrets:
    """Secure secret retrieval from Bitwarden vault"""
    
    def __init__(self):
        self._session_key = None
        self._check_cli()
    
    def _check_cli(self):
        """Verify Bitwarden CLI is installed"""
        try:
            subprocess.run(["bw", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Bitwarden CLI (bw) not found. Install with:\n"
                "  sudo snap install bw\n"
                "  or visit: https://bitwarden.com/download/"
            )
    
    def _ensure_unlocked(self):
        """Ensure vault is unlocked, get session key if needed"""
        # Check if already unlocked via environment
        if os.environ.get("BW_SESSION"):
            return os.environ.get("BW_SESSION")
        
        # Try to get status
        result = subprocess.run(
            ["bw", "status"],
            capture_output=True,
            text=True
        )
        
        status = json.loads(result.stdout) if result.returncode == 0 else {}
        
        if status.get("status") != "unlocked":
            raise RuntimeError(
                "Bitwarden vault is locked.\n"
                "Run: export BW_SESSION=$(bw unlock --raw)"
            )
        
        return os.environ.get("BW_SESSION")
    
    def get_secret(self, name: str, field: str = "password") -> Optional[str]:
        """
        Retrieve a secret from Bitwarden vault.
        
        Args:
            name: Full name/path of the secret (e.g., "API Keys/OpenAI")
            field: Field to retrieve (password, notes, username, etc.)
        
        Returns:
            Secret value or None if not found
        """
        try:
            self._ensure_unlocked()
            
            result = subprocess.run(
                ["bw", "get", field, name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error = result.stderr.strip()
                if "Not found" in error:
                    print(f"⚠️  Secret '{name}' not found in vault")
                else:
                    print(f"⚠️  Error retrieving '{name}': {error}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"⚠️  Timeout retrieving '{name}'")
            return None
        except Exception as e:
            print(f"⚠️  Failed to retrieve '{name}': {e}")
            return None
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a specific service.
        
        Searches multiple patterns:
        - Standard password field locations
        - Custom fields named PROVIDER_API_KEY
        - Entry names following PROVIDER_API_KEY pattern
        
        Args:
            service: Service name (openai, anthropic, github, etc.)
        
        Returns:
            API key or None
        """
        provider = service.upper()
        
        # Try common naming patterns in password field
        patterns = [
            f"API Keys/{service.title()} API Key",
            f"API Keys/{provider}_API_KEY",
            f"External Services/{service.title()} Token",
            f"{provider}_API_KEY",
            f"{provider}_KEY",
            f"{provider}_TOKEN",
            service.upper(),
        ]
        
        for pattern in patterns:
            secret = self.get_secret(pattern)
            if secret:
                return secret
        
        # Try advanced search for custom fields and entry names
        if advanced_find_key:
            try:
                key = advanced_find_key(service)
                if key:
                    return key
            except Exception:
                pass
        
        # Fallback: search and check first match
        try:
            result = subprocess.run(
                ["bw", "list", "items", "--search", service],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                items = json.loads(result.stdout)
                for item in items:
                    # Check password field
                    login = item.get("login", {})
                    password = login.get("password", "")
                    if password and len(password) > 10:
                        return password
                    
                    # Check custom fields for PROVIDER_API_KEY pattern
                    fields = item.get("fields", [])
                    for field in fields:
                        field_name = field.get("name", "")
                        if provider in field_name and "KEY" in field_name.upper():
                            return field.get("value")
        except:
            pass
        
        return None
    
    def get_database_uri(self, environment: str = "development") -> Optional[str]:
        """
        Get database connection string.
        
        Args:
            environment: dev, development, staging, prod, production
        
        Returns:
            Database URI or None
        """
        patterns = [
            f"Database Credentials/{environment.title()} PostgreSQL",
            f"Database/{environment.upper()}_DATABASE_URL",
            f"Database Credentials/PostgreSQL {environment.title()}",
        ]
        
        for pattern in patterns:
            # Try notes field first (for full URIs)
            uri = self.get_secret(pattern, field="notes")
            if uri:
                return uri
            
            # Try password field
            uri = self.get_secret(pattern, field="password")
            if uri and uri.startswith(("postgresql://", "postgres://", "mysql://")):
                return uri
        
        return None
    
    def list_available_secrets(self, category: str = None) -> list:
        """
        List available secrets in the vault.
        
        Args:
            category: Filter by category ("API Keys", "Database", etc.)
        
        Returns:
            List of secret names
        """
        try:
            self._ensure_unlocked()
            
            search_term = category or ""
            result = subprocess.run(
                ["bw", "list", "items", "--search", search_term],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                items = json.loads(result.stdout)
                return [item["name"] for item in items]
            
            return []
            
        except Exception as e:
            print(f"⚠️  Failed to list secrets: {e}")
            return []
    
    def get_all_api_keys(self) -> Dict[str, Optional[str]]:
        """
        Retrieve all commonly used API keys.
        
        Returns:
            Dictionary of service -> api_key
        """
        services = [
            "openai",
            "anthropic",
            "claude",
            "github",
            "gitlab",
            "stripe",
            "aws",
            "azure",
            "gcp",
            "google",
        ]
        
        return {
            service.upper() + "_API_KEY": self.get_api_key(service)
            for service in services
        }
    
    def inject_into_env(self, secrets: Dict[str, str], prefix: str = ""):
        """
        Inject secrets into environment variables.
        
        Args:
            secrets: Dictionary of secret_name -> value
            prefix: Optional prefix for env var names
        """
        for name, value in secrets.items():
            if value:
                env_name = f"{prefix}{name}" if prefix else name
                os.environ[env_name] = value
                print(f"✓ Set {env_name}")


def quick_get(name: str) -> Optional[str]:
    """Quick helper to get a single secret"""
    try:
        bw = BitwardenSecrets()
        return bw.get_secret(name)
    except Exception as e:
        print(f"Error: {e}")
        return None


def setup_env_for_coding():
    """
    Setup common environment variables for coding sessions.
    Run this before starting AI agent coding.
    """
    try:
        bw = BitwardenSecrets()
        
        print("🔐 Setting up environment from Bitwarden...")
        print()
        
        # Get API keys
        api_keys = bw.get_all_api_keys()
        bw.inject_into_env(api_keys)
        
        # Get database URIs
        for env in ["development", "staging", "production"]:
            uri = bw.get_database_uri(env)
            if uri:
                os.environ[f"{env.upper()}_DATABASE_URL"] = uri
                print(f"✓ Set {env.upper()}_DATABASE_URL")
        
        print()
        print("✅ Environment ready!")
        
    except Exception as e:
        print(f"❌ Failed to setup environment: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python bitwarden_secrets.py <command> [args]")
        print()
        print("Commands:")
        print("  get <secret_name>     - Retrieve a specific secret")
        print("  api <service>          - Get API key for service")
        print("  db [environment]       - Get database URI")
        print("  list [category]        - List available secrets")
        print("  setup                  - Setup all env vars for coding")
        print()
        print("Advanced commands:")
        print("  analyze                - Analyze vault structure for cleanup")
        print("  find-all               - Find all API keys in vault")
        print("  advanced <provider>     - Advanced search for API key")
        print()
        print("Export commands:")
        print("  export                 - Export all API keys to JSON")
        print("  export-flat            - Export flat dictionary to JSON")
        print("  export-env             - Export as .env file format")
        print()
        print("Individual key lookup:")
        print("  get-key <KEY_NAME>     - Get specific API key value")
        print("  list-keys              - List all available API key names")
        print()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "get":
        if len(sys.argv) < 3:
            print("Usage: get <secret_name>")
            sys.exit(1)
        secret = quick_get(sys.argv[2])
        if secret:
            print(secret)
        else:
            sys.exit(1)
    
    elif command == "api":
        if len(sys.argv) < 3:
            print("Usage: api <service_name>")
            sys.exit(1)
        try:
            bw = BitwardenSecrets()
            key = bw.get_api_key(sys.argv[2])
            if key:
                print(key)
            else:
                print(f"API key for '{sys.argv[2]}' not found")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == "db":
        env = sys.argv[2] if len(sys.argv) > 2 else "development"
        try:
            bw = BitwardenSecrets()
            uri = bw.get_database_uri(env)
            if uri:
                print(uri)
            else:
                print(f"Database URI for '{env}' not found")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        try:
            bw = BitwardenSecrets()
            secrets = bw.list_available_secrets(category)
            for s in secrets:
                print(f"  • {s}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == "setup":
        setup_env_for_coding()
    
    elif command == "analyze":
        # Run vault analysis
        try:
            from advanced_search import analyze_vault
            analyze_vault()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == "find-all":
        # Find all API keys
        try:
            from advanced_search import search_all_api_keys
            search_all_api_keys()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == "advanced":
        if len(sys.argv) < 3:
            print("Usage: advanced <provider>")
            sys.exit(1)
        try:
            from advanced_search import find_api_key
            key = find_api_key(sys.argv[2])
            if key:
                print(key)
            else:
                print(f"No API key found for '{sys.argv[2]}'")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == "export":
        # Export all API keys to JSON
        try:
            from export_api_keys import export_all_api_keys, print_summary
            import json
            data = export_all_api_keys()
            if data:
                print_summary(data)
                print(json.dumps(data, indent=2))
            else:
                print("Failed to export API keys")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == "export-flat":
        # Export flat dictionary to JSON
        try:
            from export_api_keys import export_flat_dict
            import json
            data = export_flat_dict()
            if data:
                print(f"Exported {len(data)} keys")
                print(json.dumps(data, indent=2))
            else:
                print("Failed to export API keys")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == "export-env":
        # Export as .env file format
        try:
            from export_api_keys import export_dot_env
            print(export_dot_env())
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == "export-dotenv":
        # Export as shell export commands
        try:
            from export_api_keys import export_flat_dict
            data = export_flat_dict()
            if data:
                for key, value in data.items():
                    print(f'export {key}="{value}"')
            else:
                print("Failed to export API keys")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Bitwarden Integration Examples for AI Agents
Demonstrates various patterns for using Bitwarden in agent workflows.
"""

import subprocess
import json
import os
from typing import Optional, Dict, List

class BitwardenExamples:
    """Example implementations of Bitwarden integration patterns."""
    
    # =========================================================================
    # Example 1: Basic Password Retrieval
    # =========================================================================
    
    @staticmethod
    def get_password(item_name: str) -> Optional[str]:
        """
        Basic password retrieval.
        
        Usage:
            password = BitwardenExamples.get_password("GitHub")
            print(f"Password: {password}")
        """
        result = subprocess.run(
            ['bw', 'get', 'password', item_name],
            capture_output=True, text=True
        )
        return result.stdout.strip() if result.returncode == 0 else None
    
    # =========================================================================
    # Example 2: Get API Key with Fallback
    # =========================================================================
    
    @staticmethod
    def get_api_key(service_name: str) -> Optional[str]:
        """
        Get API key with multiple search patterns.
        
        Usage:
            key = BitwardenExamples.get_api_key("openai")
            key = BitwardenExamples.get_api_key("anthropic")
        """
        patterns = [
            f"API Keys/{service_name.title()} API Key",
            f"API Keys/{service_name.upper()}_API_KEY",
            f"{service_name.upper()}_API_KEY",
            service_name.title(),
        ]
        
        for pattern in patterns:
            result = subprocess.run(
                ['bw', 'get', 'password', pattern],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        
        return None
    
    # =========================================================================
    # Example 3: Custom Field Retrieval
    # =========================================================================
    
    @staticmethod
    def get_custom_field(item_name: str, field_name: str) -> Optional[str]:
        """
        Get custom field value from an item.
        
        Usage:
            api_key = BitwardenExamples.get_custom_field(
                "API Keys", "OPENAI_API_KEY"
            )
        """
        result = subprocess.run(
            ['bw', 'get', 'item', item_name],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            return None
        
        item = json.loads(result.stdout)
        
        for field in item.get('fields', []):
            if field.get('name') == field_name:
                return field.get('value')
        
        return None
    
    # =========================================================================
    # Example 4: Batch Load Environment Variables
    # =========================================================================
    
    @staticmethod
    def load_env_from_bitwarden() -> Dict[str, str]:
        """
        Load multiple secrets into environment variables.
        
        Usage:
            env_vars = BitwardenExamples.load_env_from_bitwarden()
            for key, value in env_vars.items():
                os.environ[key] = value
        """
        secrets = {
            'OPENAI_API_KEY': 'API Keys/OpenAI',
            'ANTHROPIC_API_KEY': 'API Keys/Anthropic',
            'GITHUB_TOKEN': 'API Keys/GitHub',
            'STRIPE_SECRET_KEY': 'API Keys/Stripe',
        }
        
        loaded = {}
        
        for env_var, item_name in secrets.items():
            result = subprocess.run(
                ['bw', 'get', 'password', item_name],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                loaded[env_var] = result.stdout.strip()
        
        return loaded
    
    # =========================================================================
    # Example 5: Database URI Retrieval
    # =========================================================================
    
    @staticmethod
    def get_database_uri(environment: str = "development") -> Optional[str]:
        """
        Get database connection string.
        
        Usage:
            dev_uri = BitwardenExamples.get_database_uri("development")
            prod_uri = BitwardenExamples.get_database_uri("production")
        """
        # Try notes field first (for full URI)
        result = subprocess.run(
            ['bw', 'get', 'notes', f"Database/{environment.title()}"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            uri = result.stdout.strip()
            if uri.startswith(('postgresql://', 'mysql://')):
                return uri
        
        # Try custom field
        result = subprocess.run(
            ['bw', 'get', 'item', f"Database/{environment.title()}"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            item = json.loads(result.stdout)
            for field in item.get('fields', []):
                if 'URI' in field.get('name', '').upper():
                    return field.get('value')
        
        return None
    
    # =========================================================================
    # Example 6: List and Search Items
    # =========================================================================
    
    @staticmethod
    def list_api_keys() -> List[Dict]:
        """
        List all API key items in vault.
        
        Usage:
            keys = BitwardenExamples.list_api_keys()
            for key in keys:
                print(f"  - {key['name']}")
        """
        result = subprocess.run(
            ['bw', 'list', 'items', '--search', 'API'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        
        return []
    
    @staticmethod
    def search_items(query: str) -> List[str]:
        """
        Search vault items.
        
        Usage:
            matches = BitwardenExamples.search_items("production")
            print(f"Found: {', '.join(matches)}")
        """
        result = subprocess.run(
            ['bw', 'list', 'items', '--search', query],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            items = json.loads(result.stdout)
            return [item['name'] for item in items]
        
        return []
    
    # =========================================================================
    # Example 7: TOTP Code Generation
    # =========================================================================
    
    @staticmethod
    def get_totp(item_name: str) -> Optional[str]:
        """
        Get TOTP code for 2FA.
        
        Usage:
            code = BitwardenExamples.get_totp("GitHub")
            print(f"2FA Code: {code}")
        """
        result = subprocess.run(
            ['bw', 'get', 'totp', item_name],
            capture_output=True, text=True
        )
        return result.stdout.strip() if result.returncode == 0 else None
    
    # =========================================================================
    # Example 8: Secure Password Generation
    # =========================================================================
    
    @staticmethod
    def generate_password(length: int = 20, special: bool = True) -> str:
        """
        Generate secure password using Bitwarden.
        
        Usage:
            password = BitwardenExamples.generate_password(32)
            print(f"Generated: {password}")
        """
        cmd = ['bw', 'generate', '--length', str(length)]
        if special:
            cmd.append('--special')
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    
    @staticmethod
    def generate_passphrase(words: int = 4) -> str:
        """
        Generate secure passphrase.
        
        Usage:
            phrase = BitwardenExamples.generate_passphrase(5)
            print(f"Passphrase: {phrase}")
        """
        result = subprocess.run(
            ['bw', 'generate', '--passphrase', '--words', str(words)],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    
    # =========================================================================
    # Example 9: Full Item Retrieval
    # =========================================================================
    
    @staticmethod
    def get_full_item(item_name: str) -> Optional[Dict]:
        """
        Get complete item details.
        
        Usage:
            item = BitwardenExamples.get_full_item("GitHub")
            print(f"Username: {item['login']['username']}")
            print(f"Password: {item['login']['password']}")
            print(f"URL: {item['login']['uris'][0]['uri']}")
        """
        result = subprocess.run(
            ['bw', 'get', 'item', item_name],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        
        return None
    
    # =========================================================================
    # Example 10: Vault Status Check
    # =========================================================================
    
    @staticmethod
    def check_vault_status() -> Dict:
        """
        Check Bitwarden vault status.
        
        Usage:
            status = BitwardenExamples.check_vault_status()
            if status['status'] != 'unlocked':
                print("Please unlock vault first")
        """
        result = subprocess.run(
            ['bw', 'status'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        
        return {'status': 'error', 'message': result.stderr}
    
    # =========================================================================
    # Example 11: Docker Login with Bitwarden
    # =========================================================================
    
    @staticmethod
    def docker_login_from_bitwarden(registry_name: str = "Docker Hub"):
        """
        Login to Docker registry using Bitwarden credentials.
        
        Usage:
            BitwardenExamples.docker_login_from_bitwarden("Docker Hub")
        """
        # Get credentials
        username_result = subprocess.run(
            ['bw', 'get', 'username', registry_name],
            capture_output=True, text=True
        )
        password_result = subprocess.run(
            ['bw', 'get', 'password', registry_name],
            capture_output=True, text=True
        )
        
        if username_result.returncode != 0 or password_result.returncode != 0:
            print(f"❌ Could not find credentials for {registry_name}")
            return False
        
        username = username_result.stdout.strip()
        password = password_result.stdout.strip()
        
        # Login to Docker
        login_result = subprocess.run(
            ['docker', 'login', '-u', username, '--password-stdin'],
            input=password,
            capture_output=True, text=True
        )
        
        if login_result.returncode == 0:
            print(f"✅ Logged into {registry_name}")
            return True
        else:
            print(f"❌ Docker login failed: {login_result.stderr}")
            return False
    
    # =========================================================================
    # Example 12: SSH Key Retrieval
    # =========================================================================
    
    @staticmethod
    def get_ssh_key(key_name: str) -> Optional[str]:
        """
        Get SSH private key from Bitwarden.
        
        Usage:
            private_key = BitwardenExamples.get_ssh_key("SSH/Production")
            with open('~/.ssh/id_rsa', 'w') as f:
                f.write(private_key)
        """
        # Try notes field for key content
        result = subprocess.run(
            ['bw', 'get', 'notes', key_name],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            key = result.stdout.strip()
            if 'BEGIN OPENSSH PRIVATE KEY' in key or 'BEGIN RSA PRIVATE KEY' in key:
                return key
        
        # Try custom field
        result = subprocess.run(
            ['bw', 'get', 'item', key_name],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            item = json.loads(result.stdout)
            for field in item.get('fields', []):
                if 'KEY' in field.get('name', '').upper():
                    return field.get('value')
        
        return None
    
    # =========================================================================
    # Example 13: Create New Item
    # =========================================================================
    
    @staticmethod
    def create_login_item(name: str, username: str, password: str, uri: str = None) -> bool:
        """
        Create new login item in vault.
        
        Usage:
            success = BitwardenExamples.create_login_item(
                "New Service",
                "myusername",
                "mypassword123",
                "https://example.com"
            )
        """
        # Build JSON template
        item_data = {
            "type": 1,  # Login type
            "name": name,
            "login": {
                "username": username,
                "password": password,
            }
        }
        
        if uri:
            item_data["login"]["uris"] = [{"uri": uri}]
        
        # Encode and create
        json_str = json.dumps(item_data)
        encode_result = subprocess.run(
            ['bw', 'encode'],
            input=json_str,
            capture_output=True, text=True
        )
        
        if encode_result.returncode != 0:
            return False
        
        create_result = subprocess.run(
            ['bw', 'create', 'item', encode_result.stdout.strip()],
            capture_output=True, text=True
        )
        
        return create_result.returncode == 0


def run_all_examples():
    """Run all examples and display output."""
    print("=" * 70)
    print("BITWARDEN INTEGRATION EXAMPLES")
    print("=" * 70)
    
    # Check vault status first
    print("\n1. Checking vault status...")
    status = BitwardenExamples.check_vault_status()
    print(f"   Status: {status.get('status', 'unknown')}")
    print(f"   User: {status.get('userEmail', 'N/A')}")
    
    if status.get('status') != 'unlocked':
        print("\n⚠️  Vault not unlocked. Please run:")
        print("   export BW_SESSION=$(bw unlock --raw)")
        return
    
    # Example: Search items
    print("\n2. Searching for API items...")
    items = BitwardenExamples.search_items("API")
    if items:
        print(f"   Found {len(items)} items:")
        for item in items[:5]:
            print(f"     - {item}")
    else:
        print("   No items found")
    
    # Example: Generate password
    print("\n3. Generating secure password...")
    password = BitwardenExamples.generate_password(16)
    print(f"   Generated: {password[:8]}...")
    
    # Example: Generate passphrase
    print("\n4. Generating passphrase...")
    passphrase = BitwardenExamples.generate_passphrase(3)
    print(f"   Passphrase: {passphrase}")
    
    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == '__main__':
    run_all_examples()

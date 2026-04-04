"""
Bitwarden Secrets Skill Implementation

Provides secure access to Bitwarden vault for API keys, passwords, and credentials.
Wraps bitwarden.sh shell script with Python interface.
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

SKILL_DIR = Path(__file__).parent
SCRIPT = str(SKILL_DIR / "bitwarden.sh")
SESSION_DIR = Path.home() / ".config" / "bitwarden-ai"
SESSION_FILE = SESSION_DIR / "session.env"


class BitwardenSecrets:
    """Secure credential management via Bitwarden."""
    
    def __init__(self):
        self.script = SCRIPT
        self.session_dir = SESSION_DIR
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir.chmod(0o700)
    
    def _run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run bitwarden.sh command."""
        cmd = [self.script] + list(args)
        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Bitwarden command failed: {e.stderr}")
            raise
    
    def unlock_vault(self, password: str, totp: Optional[str] = None) -> Dict[str, Any]:
        """
        Unlock the Bitwarden vault.
        
        Args:
            password: Master password
            totp: 2FA code (optional)
        
        Returns:
            Dict with success status
        """
        args = ["unlock", password]
        if totp:
            args.append(totp)
        
        result = self._run(*args, check=False)
        
        if result.returncode == 0:
            return {"success": True, "message": result.stdout.strip()}
        else:
            return {"success": False, "error": result.stderr.strip()}
    
    def lock_vault(self) -> Dict[str, Any]:
        """Lock the Bitwarden vault and clear session."""
        result = self._run("lock", check=False)
        return {"success": result.returncode == 0}
    
    def get_secret(self, name: str, field: str = "password") -> Optional[str]:
        """
        Retrieve a secret from Bitwarden.
        
        Args:
            name: Item name
            field: Field to retrieve (password, username, note, uri, or custom field)
        
        Returns:
            Secret value or None
        """
        args = ["get-secret", "--name", name, "--type", field]
        result = self._run(*args, check=False)
        
        if result.returncode == 0:
            value = result.stdout.strip()
            return value if value else None
        return None
    
    def list_secrets(self, search: Optional[str] = None) -> List[str]:
        """
        List secrets matching a search query.
        
        Args:
            search: Optional search filter
        
        Returns:
            List of item names
        """
        args = ["list-secrets"]
        if search:
            args.extend(["--search", search])
        
        result = self._run(*args, check=False)
        
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
        return []
    
    def populate_env(self, env_file: str, secrets: List[str]) -> Dict[str, Any]:
        """
        Populate a .env file with secrets from Bitwarden.
        
        Args:
            env_file: Path to .env file
            secrets: List of secret names
        
        Returns:
            Dict with success status and populated secrets
        """
        secrets_str = ",".join(secrets)
        result = self._run(
            "populate-env",
            "--env-file", env_file,
            "--secrets", secrets_str,
            check=False
        )
        
        if result.returncode == 0:
            populated = []
            for line in result.stdout.strip().splitlines():
                if line.startswith("Added"):
                    populated.append(line)
            return {"success": True, "populated": populated}
        else:
            return {"success": False, "error": result.stderr.strip()}
    
    def get_login(self, service: str) -> Optional[Dict[str, str]]:
        """
        Get full login credentials for a service.
        
        Args:
            service: Service name
        
        Returns:
            Dict with name, username, password, uri or None
        """
        result = self._run("get-login", "--service", service, check=False)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return None
        return None
    
    def generate_password(self, length: int = 32, uppercase: bool = True,
                          numbers: bool = True, special: bool = True) -> Optional[str]:
        """
        Generate a secure password.
        
        Args:
            length: Password length
            uppercase: Include uppercase
            numbers: Include numbers
            special: Include special characters
        
        Returns:
            Generated password or None
        """
        args = ["generate-password", "--length", str(length)]
        if not uppercase:
            args.append("--no-uppercase")
        if not numbers:
            args.append("--no-numbers")
        if not special:
            args.append("--no-special")
        
        result = self._run(*args, check=False)
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    
    def check_status(self) -> Dict[str, Any]:
        """Check current vault status."""
        result = self._run("status", check=False)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"status": "unknown"}
        return {"status": "locked"}
    
    def is_unlocked(self) -> bool:
        """Check if vault is currently unlocked."""
        status = self.check_status()
        return status.get("status") == "unlocked"


# Global instance
_bitwarden = BitwardenSecrets()

# Export functions for direct use
unlock_vault = _bitwarden.unlock_vault
lock_vault = _bitwarden.lock_vault
get_secret = _bitwarden.get_secret
list_secrets = _bitwarden.list_secrets
populate_env = _bitwarden.populate_env
get_login = _bitwarden.get_login
generate_password = _bitwarden.generate_password
check_status = _bitwarden.check_status
is_unlocked = _bitwarden.is_unlocked


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bitwarden Secrets Skill CLI")
    parser.add_argument("command", choices=[
        "unlock", "lock", "get", "list", "populate", "login", "status", "generate"
    ])
    parser.add_argument("--name", help="Secret name")
    parser.add_argument("--field", default="password", help="Field type")
    parser.add_argument("--search", help="Search query")
    parser.add_argument("--env-file", help=".env file path")
    parser.add_argument("--secrets", help="Comma-separated secrets")
    parser.add_argument("--service", help="Service name")
    parser.add_argument("--length", type=int, default=32, help="Password length")
    
    args = parser.parse_args()
    
    if args.command == "status":
        print(json.dumps(check_status(), indent=2))
    elif args.command == "get":
        if not args.name:
            print("Error: --name required")
            exit(1)
        value = get_secret(args.name, args.field)
        print(value or "")
    elif args.command == "list":
        items = list_secrets(args.search)
        for item in items:
            print(item)
    elif args.command == "populate":
        if not args.env_file or not args.secrets:
            print("Error: --env-file and --secrets required")
            exit(1)
        result = populate_env(args.env_file, args.secrets.split(","))
        print(json.dumps(result, indent=2))
    elif args.command == "generate":
        pwd = generate_password(length=args.length)
        print(pwd or "")
    else:
        print(f"Unknown command: {args.command}")
        exit(1)

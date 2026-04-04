"""
Bitwarden Secrets Skill - Free Password Manager Edition
Version: 2.0

Provides secure access to Bitwarden vault for AI agents using the FREE
Bitwarden Password Manager CLI (bw). Supports mapping files, multiple
write modes, runtime injection, and self-hosted instances.

Workflow:
  1. Configure server (if BW_SERVER_URL set)
  2. Login with API key: bw login --apikey --nointeraction
  3. Unlock with master password from BW_PASSWORD
  4. Use BW_SESSION for all vault reads
  5. Lock or logout when complete

Required environment variables:
  BW_CLIENTID, BW_CLIENTSECRET, BW_PASSWORD
Optional: BW_SERVER_URL
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
DEFAULT_MAP_FILE = "bitwarden-env-map.json"


class BitwardenSecrets:
    """Secure credential management via Bitwarden Password Manager CLI."""

    def __init__(self):
        self.script = SCRIPT
        self.session_dir = SESSION_DIR
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir.chmod(0o700)
        self._check_mode()

    def _check_mode(self) -> str:
        """Verify we're in Password Manager mode."""
        # Must have API credentials
        if os.getenv("BW_CLIENTID") and os.getenv("BW_CLIENTSECRET"):
            self.mode = "password-manager"
        else:
            self.mode = "none"
        return self.mode

    def _run_script(
        self, *args: str, check: bool = True, timeout: int = 30
    ) -> subprocess.CompletedProcess:
        """Run bitwarden.sh command."""
        cmd = [self.script] + list(args)
        try:
            return subprocess.run(
                cmd, capture_output=True, text=True, check=check, timeout=timeout
            )
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Bitwarden script failed: cmd={' '.join(cmd)}, stderr={e.stderr}"
            )
            raise
        except subprocess.TimeoutExpired:
            logger.error(f"Bitwarden script timed out: cmd={' '.join(cmd)}")
            raise

    # ==========================================================================
    # High-Level Operations
    # ==========================================================================

    def populate_from_map(self, map_file: str = DEFAULT_MAP_FILE) -> Dict[str, Any]:
        """
        Populate .env file using mapping configuration.

        Args:
            map_file: Path to bitwarden-env-map.json

        Returns:
            Dict with operation results
        """
        try:
            result = self._run_script(
                "populate-env-from-map", map_file, check=False, timeout=60
            )

            if result.returncode == 0:
                return {"success": True, "message": result.stdout.strip(), "errors": []}
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip(),
                    "errors": [result.stderr.strip()],
                }
        except Exception as e:
            logger.error(f"populate_from_map failed: {e}")
            return {"success": False, "error": str(e), "errors": [str(e)]}

    def inject_env(
        self, map_file: str = DEFAULT_MAP_FILE, command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Inject secrets as environment variables and optionally run a command.

        Args:
            map_file: Path to bitwarden-env-map.json
            command: Optional command to run with injected secrets

        Returns:
            Dict with operation results
        """
        try:
            args = ["inject-env", "--from-map", map_file]
            if command:
                args.extend(["--", command])

            result = self._run_script(*args, check=False, timeout=60)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except Exception as e:
            logger.error(f"inject_env failed: {e}")
            return {"success": False, "error": str(e)}

    # ==========================================================================
    # Direct Secret Access (Lower-level)
    # ==========================================================================

    def get_secret(self, name: str, field: str = "password") -> Optional[str]:
        """
        Get a secret by item name and field.

        Args:
            name: Exact item name in vault
            field: password, username, note, uri, or custom field name

        Returns:
            Secret value or None
        """
        try:
            result = self._run_script(
                "get-secret", "--name", name, "--field", field, check=False
            )
            if result.returncode == 0:
                value = result.stdout.strip()
                return value if value else None
        except:
            pass
        return None

    def list_secrets(self, search: Optional[str] = None) -> List[str]:
        """List secrets with optional search filter."""
        try:
            args = ["list-secrets"]
            if search:
                args.extend(["--search", search])
            result = self._run_script(*args, check=False)
            if result.returncode == 0:
                return [
                    line.strip()
                    for line in result.stdout.strip().splitlines()
                    if line.strip()
                ]
        except:
            pass
        return []

    def get_login(self, service: str) -> Optional[Dict[str, str]]:
        """Get full login credentials (username, password, URI) for a service."""
        try:
            result = self._run_script("get-login", "--service", service, check=False)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return None

    def generate_password(self, length: int = 32) -> Optional[str]:
        """Generate a secure password."""
        try:
            result = self._run_script(
                "generate-password", "--length", str(length), check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    # ==========================================================================
    # Management Operations
    # ==========================================================================

    def login(self) -> Dict[str, Any]:
        """Perform API key login."""
        try:
            result = self._run_script("login", check=False)
            success = result.returncode == 0
            return {
                "success": success,
                "message": result.stdout.strip() if success else result.stderr.strip(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def unlock(self, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Unlock vault. Uses BW_PASSWORD from environment if not provided.
        """
        try:
            # If we have a session already, check if valid
            status = self.check_status()
            if status.get("status") == "unlocked":
                return {"success": True, "message": "Already unlocked"}

            # Need to unlock
            if password:
                # For script use - password as argument
                result = self._run_script("unlock", password, check=False)
            else:
                # Use environment BW_PASSWORD
                result = self._run_script("unlock", check=False)

            if result.returncode == 0:
                return {"success": True, "message": result.stdout.strip()}
            else:
                return {"success": False, "error": result.stderr.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def lock(self) -> Dict[str, Any]:
        """Lock the vault."""
        try:
            result = self._run_script("lock", check=False)
            return {"success": result.returncode == 0}
        except:
            return {"success": False}

    def check_status(self) -> Dict[str, Any]:
        """Check vault status."""
        try:
            result = self._run_script("status", check=False)
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    pass
        except:
            pass
        return {"status": "locked"}

    def is_unlocked(self) -> bool:
        """Check if vault is currently unlocked."""
        status = self.check_status()
        return status.get("status") == "unlocked"

    # ==========================================================================
    # Utility Functions
    # ==========================================================================

    def create_mapping_template(self, output_file: str = DEFAULT_MAP_FILE) -> bool:
        """Create a template mapping file."""
        try:
            template = {
                "env_file": ".env",
                "create_backup": True,
                "write_mode": "merge",
                "secrets": [
                    {
                        "env": "EXAMPLE_KEY",
                        "source": "item_field",
                        "search": "Exact Item Name",
                        "field": "password",
                    }
                ],
            }

            with open(output_file, "w") as f:
                json.dump(template, f, indent=2)

            Path(output_file).chmod(0o600)
            return True
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return False

    def validate_configuration(
        self, map_file: str = DEFAULT_MAP_FILE
    ) -> Dict[str, Any]:
        """
        Validate Bitwarden configuration and mapping file.

        Returns:
            Dict with validation results
        """
        checks = {
            "bw_available": self._is_bw_available(),
            "mode": self.mode,
            "env_vars": {
                "BW_CLIENTID": bool(os.getenv("BW_CLIENTID")),
                "BW_CLIENTSECRET": bool(os.getenv("BW_CLIENTSECRET")),
                "BW_PASSWORD": bool(os.getenv("BW_PASSWORD")),
                "BW_SERVER_URL": bool(os.getenv("BW_SERVER_URL")),
            },
            "map_file_exists": Path(map_file).exists(),
            "map_file_valid": False,
        }

        # Validate mapping file JSON
        if checks["map_file_exists"]:
            try:
                with open(map_file, "r") as f:
                    json.load(f)
                checks["map_file_valid"] = True
            except json.JSONDecodeError:
                pass

        checks["valid"] = (
            checks["bw_available"]
            and checks["mode"] != "none"
            and checks["map_file_exists"]
            and checks["map_file_valid"]
        )

        return checks

    def _is_bw_available(self) -> bool:
        """Check if Bitwarden CLI is available."""
        try:
            subprocess.run(
                ["bw", "--version"], capture_output=True, check=True, timeout=5
            )
            return True
        except:
            return False


# Global instance
_bitwarden = BitwardenSecrets()

# Export functions
unlock_vault = _bitwarden.unlock
lock_vault = _bitwarden.lock
get_secret = _bitwarden.get_secret
list_secrets = _bitwarden.list_secrets
get_login = _bitwarden.get_login
generate_password = _bitwarden.generate_password
populate_from_map = _bitwarden.populate_from_map
inject_env = _bitwarden.inject_env
check_status = _bitwarden.check_status
is_unlocked = _bitwarden.is_unlocked
create_mapping_template = _bitwarden.create_mapping_template
validate_configuration = _bitwarden.validate_configuration


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Bitwarden Secrets Skill - Free Edition v2.0"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Mapping-based operations
    parser_populate_map = subparsers.add_parser(
        "populate-from-map", help="Populate .env from mapping file"
    )
    parser_populate_map.add_argument(
        "--map-file", default=DEFAULT_MAP_FILE, help="Mapping file path"
    )

    parser_inject = subparsers.add_parser(
        "inject", help="Inject secrets and run command"
    )
    parser_inject.add_argument(
        "--map-file", default=DEFAULT_MAP_FILE, help="Mapping file path"
    )
    parser_inject.add_argument("--command", help="Command to run with injected secrets")

    parser_template = subparsers.add_parser(
        "create-template", help="Create mapping file template"
    )
    parser_template.add_argument(
        "--output", default=DEFAULT_MAP_FILE, help="Output file path"
    )

    parser_validate = subparsers.add_parser("validate", help="Validate configuration")
    parser_validate.add_argument(
        "--map-file", default=DEFAULT_MAP_FILE, help="Mapping file to check"
    )

    # Legacy commands
    parser_get = subparsers.add_parser("get", help="Get secret (legacy)")
    parser_get.add_argument("--name", required=True, help="Item name")
    parser_get.add_argument("--field", default="password", help="Field type")

    parser_list = subparsers.add_parser("list", help="List secrets (legacy)")
    parser_list.add_argument("--search", help="Search filter")

    parser_get_login = subparsers.add_parser("get-login", help="Get login credentials")
    parser_get_login.add_argument("--service", required=True, help="Service name")

    parser_gen = subparsers.add_parser("generate", help="Generate password")
    parser_gen.add_argument("--length", type=int, default=32, help="Password length")

    parser_unlock = subparsers.add_parser("unlock", help="Unlock vault")
    parser_lock = subparsers.add_parser("lock", help="Lock vault")
    parser_login = subparsers.add_parser("login", help="Login with API key")
    parser_status = subparsers.add_parser("status", help="Check status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "populate-from-map":
            result = populate_from_map(args.map_file)
            print(json.dumps(result, indent=2))
            sys.exit(0 if result.get("success") else 1)

        elif args.command == "inject":
            result = inject_env(args.map_file, args.command)
            print(result.get("stdout", ""))
            if result.get("stderr"):
                print(result["stderr"], file=sys.stderr)
            sys.exit(result.get("exit_code", 0))

        elif args.command == "create-template":
            success = create_mapping_template(args.output)
            if success:
                print(f"Created template: {args.output}")
                print("NOTE: This skill uses Bitwarden Password Manager (free plan).")
            else:
                print("Failed to create template", file=sys.stderr)
                sys.exit(1)

        elif args.command == "validate":
            result = validate_configuration(args.map_file)
            print(json.dumps(result, indent=2))
            sys.exit(0 if result.get("valid") else 1)

        elif args.command == "get":
            value = get_secret(args.name, args.field)
            if value:
                print(value)
                sys.exit(0)
            else:
                print(f"Secret not found: {args.name}", file=sys.stderr)
                sys.exit(1)

        elif args.command == "list":
            items = list_secrets(args.search)
            for item in items:
                print(item)
            sys.exit(0)

        elif args.command == "get-login":
            creds = get_login(args.service)
            if creds:
                print(json.dumps(creds, indent=2))
                sys.exit(0)
            else:
                print(f"Service not found: {args.service}", file=sys.stderr)
                sys.exit(1)

        elif args.command == "generate":
            pwd = generate_password(args.length)
            if pwd:
                print(pwd)
                sys.exit(0)
            else:
                print("Password generation failed", file=sys.stderr)
                sys.exit(1)

        elif args.command == "unlock":
            result = unlock()
            if result["success"]:
                print(result["message"])
                sys.exit(0)
            else:
                print(f"Unlock failed: {result['error']}", file=sys.stderr)
                sys.exit(1)

        elif args.command == "lock":
            result = lock()
            if result["success"]:
                print("Vault locked")
                sys.exit(0)
            else:
                print("Lock failed", file=sys.stderr)
                sys.exit(1)

        elif args.command == "login":
            result = login()
            if result["success"]:
                print(result["message"])
                print("Next: run 'unlock' to access secrets")
                sys.exit(0)
            else:
                print(f"Login failed: {result['error']}", file=sys.stderr)
                sys.exit(1)

        elif args.command == "status":
            status = check_status()
            print(json.dumps(status, indent=2))
            sys.exit(0)

    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)

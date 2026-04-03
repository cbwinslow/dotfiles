#!/usr/bin/env python3
"""
Bitwarden Client for AI Agents

Provides secure access to Bitwarden credentials and API keys for AI agents.
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Credential:
    """Represents a Bitwarden credential"""
    name: str
    username: str
    password: str
    uri: str
    notes: str
    fields: Dict[str, str]
    created: datetime
    updated: datetime
    vault: str


class BitwardenClient:
    """Bitwarden client for AI agents"""
    
    def __init__(self, session_token: Optional[str] = None):
        """
        Initialize Bitwarden client
        
        Args:
            session_token: Optional session token for authenticated operations
        """
        self.session_token = session_token or os.getenv("BW_SESSION")
        self.cli_path = self._find_bw_cli()
        
        # Check if Bitwarden CLI is available
        if not self.cli_path:
            raise FileNotFoundError("Bitwarden CLI (bw) not found. Please install it first.")
    
    def _find_bw_cli(self) -> Optional[str]:
        """Find Bitwarden CLI executable"""
        # Check common locations
        common_paths = [
            "/usr/local/bin/bw",
            "/usr/bin/bw",
            "/opt/homebrew/bin/bw",
            "/home/linuxbrew/.linuxbrew/bin/bw"
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        # Check if bw is in PATH
        try:
            subprocess.run(["bw", "--version"], capture_output=True, check=True)
            return "bw"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def _run_bw_command(self, *args, check=True, **kwargs) -> subprocess.CompletedProcess:
        """Run Bitwarden CLI command with error handling"""
        command = [self.cli_path] + list(args)
        
        # Add session token if available
        if self.session_token:
            command.extend(["--session", self.session_token])
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check,
                **kwargs
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Bitwarden CLI command failed: {e}")
            logger.error(f"Command: {' '.join(command)}")
            logger.error(f"Error: {e.stderr}")
            raise
    
    def get_api_key(self, key_name: str, vault_name: str = "Personal") -> Dict[str, Any]:
        """
        Retrieve an API key from Bitwarden by name.
        
        Args:
            key_name: The name of the API key to retrieve
            vault_name: The Bitwarden vault name (default: "Personal")
        
        Returns:
            Dictionary containing api_key and metadata
        """
        logger.info(f"Retrieving API key: {key_name} from vault: {vault_name}")
        
        try:
            # Search for the credential
            search_result = self._run_bw_command(
                "search",
                key_name,
                "--vault", vault_name,
                check=False
            )
            
            if search_result.returncode != 0:
                # Try without vault if not found
                search_result = self._run_bw_command(
                    "search",
                    key_name,
                    check=False
                )
            
            if search_result.returncode != 0:
                raise ValueError(f"API key '{key_name}' not found in vault '{vault_name}'")
            
            # Parse search results
            credentials = json.loads(search_result.stdout)
            
            # Find the matching credential
            matching_creds = [
                cred for cred in credentials 
                if cred.get("name", "").lower() == key_name.lower()
            ]
            
            if not matching_creds:
                raise ValueError(f"API key '{key_name}' not found")
            
            if len(matching_creds) > 1:
                logger.warning(f"Multiple credentials found for '{key_name}'. Using first match.")
            
            credential = matching_creds[0]
            
            # Extract API key (usually in password field)
            api_key = credential.get("password")
            
            if not api_key:
                # Check custom fields for API key
                for field in credential.get("fields", []):
                    if field.get("name", "").lower() in ["api key", "api_key", "key"]:
                        api_key = field.get("value")
                        break
            
            if not api_key:
                raise ValueError(f"API key not found in credential '{key_name}'")
            
            # Extract metadata
            metadata = {
                "id": credential.get("id"),
                "name": credential.get("name"),
                "username": credential.get("username"),
                "uri": credential.get("uri"),
                "created": credential.get("createdDate"),
                "updated": credential.get("revisionDate"),
                "vault": vault_name
            }
            
            logger.info(f"Successfully retrieved API key for '{key_name}'")
            return {
                "api_key": api_key,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error retrieving API key: {e}")
            raise
    
    def populate_env_file(self, env_file_path: str, credentials: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Populate a .env file with credentials from Bitwarden.
        
        Args:
            env_file_path: Path to the .env file to populate
            credentials: List of credential objects with name and vault
        
        Returns:
            Dictionary with success status and updated keys
        """
        logger.info(f"Populating .env file: {env_file_path}")
        
        try:
            # Read existing .env file if it exists
            env_path = Path(env_file_path)
            existing_content = {}
            
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                existing_content[key.strip()] = value.strip()
            
            # Retrieve all credentials
            updated_keys = []
            new_content = existing_content.copy()
            
            for cred in credentials:
                key_name = cred.get("name")
                vault_name = cred.get("vault", "Personal")
                
                try:
                    result = self.get_api_key(key_name, vault_name)
                    api_key = result["api_key"]
                    metadata = result["metadata"]
                    
                    # Determine environment variable name
                    env_var_name = key_name.upper().replace(" ", "_").replace("-", "_")
                    
                    # Check if key already exists
                    if env_var_name in new_content:
                        logger.info(f"Updating existing key: {env_var_name}")
                    else:
                        logger.info(f"Adding new key: {env_var_name}")
                    
                    new_content[env_var_name] = api_key
                    updated_keys.append({
                        "key_name": key_name,
                        "env_var": env_var_name,
                        "vault": vault_name,
                        "metadata": metadata
                    })
                
                except Exception as e:
                    logger.warning(f"Failed to retrieve {key_name}: {e}")
                    continue
            
            # Write updated .env file
            with open(env_path, 'w') as f:
                for key, value in new_content.items():
                    f.write(f"{key}={value}\n")
            
            logger.info(f"Successfully populated .env file with {len(updated_keys)} keys")
            return {
                "success": True,
                "updated_keys": updated_keys,
                "total_keys": len(updated_keys)
            }
        
        except Exception as e:
            logger.error(f"Error populating .env file: {e}")
            return {
                "success": False,
                "error": str(e),
                "updated_keys": []
            }
    
    def list_vaults(self, include_folders: bool = False) -> Dict[str, Any]:
        """
        List all available Bitwarden vaults.
        
        Args:
            include_folders: Whether to include folder structure
        
        Returns:
            Dictionary with vault information
        """
        logger.info("Listing Bitwarden vaults")
        
        try:
            if include_folders:
                result = self._run_bw_command("list", "folders")
                folders = json.loads(result.stdout)
                
                return {
                    "vaults": ["Personal", "Work", "Shared", "Custom"],  # Common vault names
                    "folders": folders,
                    "success": True
                }
            else:
                # Bitwarden CLI doesn't have a direct vault listing command
                # Return common vault names
                return {
                    "vaults": ["Personal", "Work", "Shared", "Custom"],
                    "success": True
                }
        
        except Exception as e:
            logger.error(f"Error listing vaults: {e}")
            return {
                "vaults": [],
                "success": False,
                "error": str(e)
            }
    
    def search_credentials(self, query: str, search_type: str = "all") -> Dict[str, Any]:
        """
        Search for credentials by name or tag.
        
        Args:
            query: Search query
            search_type: "name", "tag", or "all" (default: "all")
        
        Returns:
            Dictionary with search results
        """
        logger.info(f"Searching credentials: query='{query}', type='{search_type}'")
        
        try:
            # Perform search
            result = self._run_bw_command("search", query)
            credentials = json.loads(result.stdout)
            
            # Filter by search type if needed
            if search_type != "all":
                filtered_creds = []
                for cred in credentials:
                    if search_type == "name" and query.lower() in cred.get("name", "").lower():
                        filtered_creds.append(cred)
                    elif search_type == "tag":
                        # Check tags (if available)
                        tags = cred.get("tags", [])
                        if any(query.lower() in tag.lower() for tag in tags):
                            filtered_creds.append(cred)
                credentials = filtered_creds
            
            # Format results
            formatted_results = []
            for cred in credentials:
                formatted_results.append({
                    "id": cred.get("id"),
                    "name": cred.get("name"),
                    "username": cred.get("username"),
                    "uri": cred.get("uri"),
                    "created": cred.get("createdDate"),
                    "updated": cred.get("revisionDate"),
                    "vault": cred.get("organizationId", "Personal") or "Personal",
                    "type": cred.get("type")
                })
            
            return {
                "results": formatted_results,
                "total_count": len(formatted_results),
                "success": True
            }
        
        except Exception as e:
            logger.error(f"Error searching credentials: {e}")
            return {
                "results": [],
                "total_count": 0,
                "success": False,
                "error": str(e)
            }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate Bitwarden configuration and connectivity.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating Bitwarden configuration")
        
        try:
            # Check if bw CLI is available
            version_result = self._run_bw_command("--version")
            version_info = version_result.stdout.strip()
            
            # Test authentication
            status_result = self._run_bw_command("status", check=False)
            
            if status_result.returncode == 0:
                status_info = json.loads(status_result.stdout)
                authenticated = status_info.get("status") == "unlocked"
            else:
                authenticated = False
            
            return {
                "valid": True,
                "version": version_info,
                "authenticated": authenticated,
                "cli_path": self.cli_path,
                "session_token": bool(self.session_token)
            }
        
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "valid": False,
                "error": str(e)
            }


# Convenience functions for direct usage
def get_api_key(key_name: str, vault_name: str = "Personal") -> Dict[str, Any]:
    """Convenience function to get API key"""
    client = BitwardenClient()
    return client.get_api_key(key_name, vault_name)


def populate_env_file(env_file_path: str, credentials: List[Dict[str, str]]) -> Dict[str, Any]:
    """Convenience function to populate .env file"""
    client = BitwardenClient()
    return client.populate_env_file(env_file_path, credentials)


def list_vaults(include_folders: bool = False) -> Dict[str, Any]:
    """Convenience function to list vaults"""
    client = BitwardenClient()
    return client.list_vaults(include_folders)


def search_credentials(query: str, search_type: str = "all") -> Dict[str, Any]:
    """Convenience function to search credentials"""
    client = BitwardenClient()
    return client.search_credentials(query, search_type)


def validate_configuration() -> Dict[str, Any]:
    """Convenience function to validate configuration"""
    client = BitwardenClient()
    return client.validate_configuration()


if __name__ == "__main__":
    """Command-line interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bitwarden Client CLI")
    parser.add_argument("--get-key", help="Get API key by name")
    parser.add_argument("--vault", help="Vault name (default: Personal)")
    parser.add_argument("--populate", help="Populate .env file")
    parser.add_argument("--credentials", help="Credentials JSON file", type=str)
    parser.add_argument("--list-vaults", action="store_true", help="List available vaults")
    parser.add_argument("--search", help="Search credentials")
    parser.add_argument("--type", help="Search type: name, tag, or all")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    
    args = parser.parse_args()
    
    if args.get_key:
        result = get_api_key(args.get_key, args.vault or "Personal")
        print(json.dumps(result, indent=2))
    elif args.populate:
        if not args.credentials:
            print("Error: --credentials is required for populate operation")
            sys.exit(1)
        
        try:
            with open(args.credentials, 'r') as f:
                credentials = json.load(f)
        except Exception as e:
            print(f"Error reading credentials file: {e}")
            sys.exit(1)
        
        result = populate_env_file(args.populate, credentials)
        print(json.dumps(result, indent=2))
    elif args.list_vaults:
        result = list_vaults()
        print(json.dumps(result, indent=2))
    elif args.search:
        result = search_credentials(args.search, args.type or "all")
        print(json.dumps(result, indent=2))
    elif args.validate:
        result = validate_configuration()
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
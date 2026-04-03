#!/usr/bin/env python3
"""
Bitwarden Skill Wrapper

Provides a unified interface for AI agents to use Bitwarden functionality.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BitwardenSkillWrapper:
    """Wrapper for Bitwarden skill operations"""
    
    def __init__(self, base_path: str = "/home/cbwinslow/dotfiles/ai"):
        self.base_path = Path(base_path)
        self.skills_dir = self.base_path / "skills" / "integration" / "bitwarden"
        self.tools_dir = self.base_path / "tools" / "api_tools" / "bitwarden"
        self.scripts_dir = self.base_path / "scripts" / "bitwarden"
        
        # Check if Bitwarden is configured
        self.bitwarden_configured = self._check_bitwarden_config()
    
    def _check_bitwarden_config(self) -> bool:
        """Check if Bitwarden is properly configured"""
        try:
            # Check if Bitwarden CLI is available
            if not self._is_bw_available():
                logger.warning("Bitwarden CLI not found")
                return False
            
            # Check if session token is available
            if not os.getenv("BW_SESSION"):
                logger.warning("BW_SESSION not set")
                return False
            
            # Test connection
            try:
                import subprocess
                result = subprocess.run(
                    ["bw", "status"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return True
            except:
                pass
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking Bitwarden config: {e}")
            return False
    
    def _is_bw_available(self) -> bool:
        """Check if Bitwarden CLI is available"""
        try:
            import subprocess
            result = subprocess.run(
                ["bw", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def get_api_key(self, key_name: str, vault_name: str = "Personal") -> Dict[str, Any]:
        """
        Get API key from Bitwarden using the skill interface.
        
        Args:
            key_name: Name of the API key
            vault_name: Vault name (default: "Personal")
        
        Returns:
            Dictionary with API key and metadata
        """
        if not self.bitwarden_configured:
            return {
                "success": False,
                "error": "Bitwarden not configured",
                "api_key": None,
                "metadata": None
            }
        
        try:
            # Use the Bitwarden client from tools
            from bitwarden_client import get_api_key
            
            result = get_api_key(key_name, vault_name)
            
            if result.get("success", True):
                return {
                    "success": True,
                    "api_key": result["api_key"],
                    "metadata": result["metadata"]
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "api_key": None,
                    "metadata": None
                }
        
        except Exception as e:
            logger.error(f"Error getting API key: {e}")
            return {
                "success": False,
                "error": str(e),
                "api_key": None,
                "metadata": None
            }
    
    def populate_env_file(self, env_file_path: str, credentials: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Populate .env file using the skill interface.
        
        Args:
            env_file_path: Path to .env file
            credentials: List of credential objects
        
        Returns:
            Dictionary with operation result
        """
        if not self.bitwarden_configured:
            return {
                "success": False,
                "error": "Bitwarden not configured",
                "updated_keys": [],
                "total_keys": 0
            }
        
        try:
            # Use the Bitwarden client from tools
            from bitwarden_client import populate_env_file
            
            result = populate_env_file(env_file_path, credentials)
            
            return {
                "success": result.get("success", False),
                "error": result.get("error"),
                "updated_keys": result.get("updated_keys", []),
                "total_keys": result.get("total_keys", 0)
            }
        
        except Exception as e:
            logger.error(f"Error populating .env file: {e}")
            return {
                "success": False,
                "error": str(e),
                "updated_keys": [],
                "total_keys": 0
            }
    
    def list_vaults(self, include_folders: bool = False) -> Dict[str, Any]:
        """
        List available vaults using the skill interface.
        
        Args:
            include_folders: Whether to include folder structure
        
        Returns:
            Dictionary with vault information
        """
        if not self.bitwarden_configured:
            return {
                "success": False,
                "error": "Bitwarden not configured",
                "vaults": [],
                "folders": []
            }
        
        try:
            # Use the Bitwarden client from tools
            from bitwarden_client import list_vaults
            
            result = list_vaults(include_folders)
            
            return {
                "success": result.get("success", False),
                "error": result.get("error"),
                "vaults": result.get("vaults", []),
                "folders": result.get("folders", [])
            }
        
        except Exception as e:
            logger.error(f"Error listing vaults: {e}")
            return {
                "success": False,
                "error": str(e),
                "vaults": [],
                "folders": []
            }
    
    def search_credentials(self, query: str, search_type: str = "all") -> Dict[str, Any]:
        """
        Search for credentials using the skill interface.
        
        Args:
            query: Search query
            search_type: "name", "tag", or "all" (default: "all")
        
        Returns:
            Dictionary with search results
        """
        if not self.bitwarden_configured:
            return {
                "success": False,
                "error": "Bitwarden not configured",
                "results": [],
                "total_count": 0
            }
        
        try:
            # Use the Bitwarden client from tools
            from bitwarden_client import search_credentials
            
            result = search_credentials(query, search_type)
            
            return {
                "success": result.get("success", False),
                "error": result.get("error"),
                "results": result.get("results", []),
                "total_count": result.get("total_count", 0)
            }
        
        except Exception as e:
            logger.error(f"Error searching credentials: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "total_count": 0
            }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate Bitwarden configuration using the skill interface.
        
        Returns:
            Dictionary with validation results
        """
        try:
            # Use the Bitwarden client from tools
            from bitwarden_client import validate_configuration
            
            result = validate_configuration()
            
            return {
                "success": result.get("valid", False),
                "error": result.get("error"),
                "version": result.get("version"),
                "authenticated": result.get("authenticated"),
                "cli_path": result.get("cli_path")
            }
        
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return {
                "success": False,
                "error": str(e),
                "version": None,
                "authenticated": False,
                "cli_path": None
            }


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bitwarden Skill Wrapper CLI")
    parser.add_argument("--get-key", help="Get API key by name")
    parser.add_argument("--vault", help="Vault name (default: Personal)")
    parser.add_argument("--populate", help="Populate .env file")
    parser.add_argument("--credentials", help="Credentials JSON file", type=str)
    parser.add_argument("--list-vaults", action="store_true", help="List available vaults")
    parser.add_argument("--search", help="Search credentials")
    parser.add_argument("--type", help="Search type: name, tag, or all")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    
    args = parser.parse_args()
    
    wrapper = BitwardenSkillWrapper()
    
    if args.get_key:
        result = wrapper.get_api_key(args.get_key, args.vault or "Personal")
        print(json.dumps(result, indent=2))
    elif args.populate:
        if not args.credentials:
            print("Error: --credentials is required for populate operation")
            exit(1)
        
        try:
            with open(args.credentials, 'r') as f:
                credentials = json.load(f)
        except Exception as e:
            print(f"Error reading credentials file: {e}")
            exit(1)
        
        result = wrapper.populate_env_file(args.populate, credentials)
        print(json.dumps(result, indent=2))
    elif args.list_vaults:
        result = wrapper.list_vaults()
        print(json.dumps(result, indent=2))
    elif args.search:
        result = wrapper.search_credentials(args.search, args.type or "all")
        print(json.dumps(result, indent=2))
    elif args.validate:
        result = wrapper.validate_configuration()
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
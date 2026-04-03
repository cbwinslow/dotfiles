"""
Advanced Bitwarden Search Routines for AI Agents

Handles multiple API key storage patterns:
- Password field (standard)
- Custom fields named PROVIDER_API_KEY
- Entry names following PROVIDER_API_KEY pattern
"""

import subprocess
import json
import re
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class SecretMatch:
    """Represents a found secret with metadata"""
    name: str
    value: str
    source: str  # 'password', 'custom_field', 'notes', 'username'
    field_name: Optional[str] = None  # For custom fields
    item_id: Optional[str] = None


class BitwardenAdvancedSearch:
    """Advanced search for API keys with multiple pattern support"""
    
    # Common API key patterns in entry names
    API_KEY_PATTERNS = [
        r'^([A-Z_]+)_API_KEY$',           # OPENAI_API_KEY, ANTHROPIC_API_KEY
        r'^([A-Z_]+)_KEY$',                # OPENAI_KEY, GITHUB_KEY
        r'^([A-Z_]+)_TOKEN$',              # GITHUB_TOKEN, GITLAB_TOKEN
        r'^([A-Z_]+)_SECRET$',             # AWS_SECRET, GCP_SECRET
        r'^([A-Z_]+)_ACCESS_KEY$',         # AWS_ACCESS_KEY
        r'^([A-Z_]+)_PRIVATE_KEY$',         # SSH_PRIVATE_KEY
        r'^([A-Z_]+)_API_SECRET$',          # STRIPE_API_SECRET
        r'^API[_-]?KEY[_-]?([A-Z_]+)$',     # APIKEY_OPENAI
        r'^([A-Z_]+)[_-]?API[_-]?KEY$',    # OPENAI-API-KEY
    ]
    
    # Custom field names that typically hold API keys
    CUSTOM_FIELD_PATTERNS = [
        r'^[A-Z_]+_API_KEY$',
        r'^[A-Z_]+_KEY$',
        r'^[A-Z_]+_TOKEN$',
        r'^[A-Z_]+_SECRET$',
        r'^API_KEY$',
        r'^API_SECRET$',
        r'^ACCESS_TOKEN$',
        r'^PRIVATE_KEY$',
    ]
    
    def __init__(self):
        self._session = None
        self._ensure_unlocked()
    
    def _ensure_unlocked(self):
        """Ensure Bitwarden vault is unlocked"""
        import os
        if os.environ.get("BW_SESSION"):
            return
        
        result = subprocess.run(
            ["bw", "status"],
            capture_output=True,
            text=True
        )
        status = json.loads(result.stdout) if result.returncode == 0 else {}
        
        if status.get("status") != "unlocked":
            raise RuntimeError(
                "Bitwarden vault locked. Run: export BW_SESSION=$(bw unlock --raw)"
            )
    
    def _run_bw(self, args: List[str]) -> Tuple[bool, str]:
        """Execute Bitwarden CLI command"""
        result = subprocess.run(
            ["bw"] + args,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout
    
    def _get_item_details(self, item_id: str) -> Optional[Dict]:
        """Get full item details as JSON"""
        success, output = self._run_bw(["get", "item", item_id])
        if success:
            return json.loads(output)
        return None
    
    def search_api_keys(self) -> List[SecretMatch]:
        """
        Comprehensive search for all API keys using multiple strategies.
        
        Strategies:
        1. Search by entry name patterns
        2. Search by custom field patterns
        3. Search common categories (API Keys, Tokens, Secrets)
        4. Full vault scan for credential items
        """
        matches = []
        seen_values = set()  # Avoid duplicates
        
        # Strategy 1: Search common terms and check names
        search_terms = ["API", "KEY", "TOKEN", "SECRET", "PRIVATE", "ACCESS"]
        for term in search_terms:
            items = self._search_items(term)
            for item in items:
                match = self._check_item_for_api_key(item)
                if match and match.value not in seen_values:
                    matches.append(match)
                    seen_values.add(match.value)
        
        # Strategy 2: Scan all items for custom fields
        all_items = self._list_all_items()
        for item in all_items:
            custom_matches = self._check_custom_fields(item)
            for match in custom_matches:
                if match.value not in seen_values:
                    matches.append(match)
                    seen_values.add(match.value)
        
        return matches
    
    def _search_items(self, term: str) -> List[Dict]:
        """Search items by term"""
        success, output = self._run_bw(["list", "items", "--search", term])
        if success:
            return json.loads(output)
        return []
    
    def _list_all_items(self) -> List[Dict]:
        """List all vault items"""
        success, output = self._run_bw(["list", "items"])
        if success:
            return json.loads(output)
        return []
    
    def _check_item_for_api_key(self, item: Dict) -> Optional[SecretMatch]:
        """
        Check if an item contains an API key in standard fields.
        Checks password field and notes.
        """
        name = item.get("name", "")
        login = item.get("login", {})
        
        # Check if name matches API key pattern
        is_api_key_name = any(
            re.match(pattern, name, re.IGNORECASE)
            for pattern in self.API_KEY_PATTERNS
        )
        
        if not is_api_key_name:
            return None
        
        # Try password field first
        password = login.get("password", "")
        if password and len(password) > 10:  # Reasonable API key length
            return SecretMatch(
                name=name,
                value=password,
                source="password",
                item_id=item.get("id")
            )
        
        # Try notes field
        notes = item.get("notes", "")
        if notes and self._looks_like_api_key(notes):
            return SecretMatch(
                name=name,
                value=notes.strip(),
                source="notes",
                item_id=item.get("id")
            )
        
        return None
    
    def _check_custom_fields(self, item: Dict) -> List[SecretMatch]:
        """
        Check custom fields for API key patterns.
        Returns list of matches.
        """
        matches = []
        name = item.get("name", "")
        fields = item.get("fields", [])
        
        for field in fields:
            field_name = field.get("name", "")
            field_value = field.get("value", "")
            field_type = field.get("type", 0)  # 0 = text, 1 = hidden
            
            # Check if field name matches API key pattern
            is_api_field = any(
                re.match(pattern, field_name, re.IGNORECASE)
                for pattern in self.CUSTOM_FIELD_PATTERNS
            )
            
            if is_api_field and field_value:
                # Determine if value looks like an API key
                if self._looks_like_api_key(field_value):
                    matches.append(SecretMatch(
                        name=f"{name}.{field_name}",
                        value=field_value,
                        source="custom_field",
                        field_name=field_name,
                        item_id=item.get("id")
                    ))
        
        return matches
    
    def _looks_like_api_key(self, value: str) -> bool:
        """Heuristic to check if a value looks like an API key"""
        if not value or len(value) < 10:
            return False
        
        # Common API key patterns
        patterns = [
            r'^sk-[a-zA-Z0-9]{20,}',           # OpenAI-style
            r'^sk-ant-[a-zA-Z0-9]{20,}',       # Anthropic-style
            r'^ghp_[a-zA-Z0-9]{20,}',          # GitHub-style
            r'^glpat-[a-zA-Z0-9]{20,}',        # GitLab-style
            r'^AKIA[0-9A-Z]{16}',               # AWS Access Key
            r'^rk_[a-zA-Z0-9]{20,}',           # Stripe restricted key
            r'^sk_[a-zA-Z0-9]{20,}',           # Stripe secret key
            r'^[a-zA-Z0-9_-]{20,}$',           # Generic 20+ chars
        ]
        
        return any(re.match(p, value) for p in patterns)
    
    def find_api_key(self, provider: str) -> Optional[SecretMatch]:
        """
        Find API key for a specific provider.
        
        Searches multiple patterns:
        - PROVIDER_API_KEY (custom field)
        - Entry named PROVIDER_API_KEY
        - Entry containing provider name
        """
        provider_upper = provider.upper()
        
        # Search 1: Direct custom field match
        all_items = self._list_all_items()
        for item in all_items:
            fields = item.get("fields", [])
            for field in fields:
                if field.get("name", "").upper() == f"{provider_upper}_API_KEY":
                    return SecretMatch(
                        name=item.get("name"),
                        value=field.get("value"),
                        source="custom_field",
                        field_name=field.get("name"),
                        item_id=item.get("id")
                    )
        
        # Search 2: Entry name patterns
        patterns = [
            f"{provider_upper}_API_KEY",
            f"{provider_upper}_KEY",
            f"{provider_upper}_TOKEN",
            f"{provider.title()}_API_KEY",
            f"{provider.title()} API Key",
            provider_upper,
        ]
        
        for pattern in patterns:
            items = self._search_items(pattern)
            for item in items:
                match = self._check_item_for_api_key(item)
                if match:
                    return match
        
        return None
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key value for a provider (convenience method)"""
        match = self.find_api_key(provider)
        return match.value if match else None
    
    def analyze_vault_structure(self) -> Dict:
        """
        Analyze vault and report structure for cleanup recommendations.
        """
        all_items = self._list_all_items()
        
        analysis = {
            "total_items": len(all_items),
            "api_key_items": [],
            "inconsistent_entries": [],
            "recommendations": []
        }
        
        for item in all_items:
            name = item.get("name", "")
            fields = item.get("fields", [])
            login = item.get("login", {})
            
            # Check if it's an API key item
            is_api = any(re.match(p, name, re.IGNORECASE) for p in self.API_KEY_PATTERNS)
            
            if is_api:
                has_password = bool(login.get("password"))
                has_custom_fields = len(fields) > 0
                has_notes = bool(item.get("notes"))
                
                analysis["api_key_items"].append({
                    "name": name,
                    "id": item.get("id"),
                    "has_password": has_password,
                    "has_custom_fields": has_custom_fields,
                    "custom_field_names": [f.get("name") for f in fields],
                    "has_notes": has_notes
                })
                
                # Identify inconsistencies
                if has_password and has_custom_fields:
                    # Check if both contain API keys (redundant)
                    custom_api_fields = [
                        f for f in fields
                        if any(re.match(p, f.get("name", ""), re.IGNORECASE) 
                               for p in self.CUSTOM_FIELD_PATTERNS)
                    ]
                    if custom_api_fields:
                        analysis["inconsistent_entries"].append({
                            "name": name,
                            "issue": "API key in both password field and custom fields",
                            "recommendation": "Consolidate to one location"
                        })
                
                if not has_password and not has_custom_fields:
                    analysis["inconsistent_entries"].append({
                        "name": name,
                        "issue": "No API key found in standard fields",
                        "recommendation": "Check notes field or add API key"
                    })
        
        # Generate recommendations
        if analysis["inconsistent_entries"]:
            analysis["recommendations"].append(
                f"Found {len(analysis['inconsistent_entries'])} entries needing cleanup"
            )
        
        # Check naming consistency
        naming_patterns = {}
        for item in analysis["api_key_items"]:
            name = item["name"]
            # Extract pattern type
            if "_API_KEY" in name:
                naming_patterns.setdefault("PROVIDER_API_KEY", []).append(name)
            elif "_KEY" in name:
                naming_patterns.setdefault("PROVIDER_KEY", []).append(name)
            elif "_TOKEN" in name:
                naming_patterns.setdefault("PROVIDER_TOKEN", []).append(name)
        
        if len(naming_patterns) > 1:
            analysis["recommendations"].append(
                f"Inconsistent naming: {list(naming_patterns.keys())}. "
                "Consider standardizing to PROVIDER_API_KEY format"
            )
        
        return analysis
    
    def print_analysis(self):
        """Print vault analysis in readable format"""
        analysis = self.analyze_vault_structure()
        
        print("=" * 60)
        print("BITWARDEN VAULT ANALYSIS")
        print("=" * 60)
        print(f"\nTotal items: {analysis['total_items']}")
        print(f"API key items: {len(analysis['api_key_items'])}")
        
        if analysis["api_key_items"]:
            print("\n--- API Key Entries ---")
            for item in analysis["api_key_items"]:
                print(f"\n📄 {item['name']}")
                print(f"   Password field: {'✓' if item['has_password'] else '✗'}")
                print(f"   Custom fields: {item['custom_field_names'] or 'None'}")
                print(f"   Notes field: {'✓' if item['has_notes'] else '✗'}")
        
        if analysis["inconsistent_entries"]:
            print("\n--- Issues Found ---")
            for issue in analysis["inconsistent_entries"]:
                print(f"\n⚠️  {issue['name']}")
                print(f"   Issue: {issue['issue']}")
                print(f"   → {issue['recommendation']}")
        
        if analysis["recommendations"]:
            print("\n--- Recommendations ---")
            for rec in analysis["recommendations"]:
                print(f"💡 {rec}")
        
        print("\n" + "=" * 60)


# Convenience functions
def find_api_key(provider: str) -> Optional[str]:
    """Quick function to find API key for a provider"""
    try:
        search = BitwardenAdvancedSearch()
        return search.get_api_key(provider)
    except Exception as e:
        print(f"Error: {e}")
        return None


def analyze_vault():
    """Analyze and print vault structure"""
    try:
        search = BitwardenAdvancedSearch()
        search.print_analysis()
    except Exception as e:
        print(f"Error: {e}")


def search_all_api_keys():
    """Search and list all API keys in vault"""
    try:
        search = BitwardenAdvancedSearch()
        matches = search.search_api_keys()
        
        print(f"\nFound {len(matches)} API keys:\n")
        for match in matches:
            masked = match.value[:8] + "..." + match.value[-4:] if len(match.value) > 12 else "***"
            print(f"  📄 {match.name}")
            print(f"     Source: {match.source}" + 
                  (f" ({match.field_name})" if match.field_name else ""))
            print(f"     Value: {masked}")
            print()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python advanced_search.py <command> [args]")
        print()
        print("Commands:")
        print("  find <provider>     - Find API key for provider (e.g., openai)")
        print("  analyze             - Analyze vault structure for cleanup")
        print("  list                - List all API keys found")
        print()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "find":
        if len(sys.argv) < 3:
            print("Usage: find <provider>")
            sys.exit(1)
        key = find_api_key(sys.argv[2])
        if key:
            print(key)
        else:
            print(f"No API key found for '{sys.argv[2]}'")
            sys.exit(1)
    
    elif command == "analyze":
        analyze_vault()
    
    elif command == "list":
        search_all_api_keys()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

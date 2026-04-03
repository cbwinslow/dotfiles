#!/usr/bin/env python3
"""
Export all API keys from Bitwarden vault.
Usage: 
  python3 export_api_keys.py > api_keys.json
  python3 export_api_keys.py --flat > api_keys_flat.json
  python3 export_api_keys.py --env > .env
  python3 export_api_keys.py --get OPENROUTER_API_KEY
"""

import json
import sys
import subprocess
import os


def run_bw(args):
    """Execute Bitwarden CLI command"""
    env = os.environ.copy()
    result = subprocess.run(
        ["bw"] + args,
        capture_output=True,
        text=True,
        env=env
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout


def export_all_api_keys():
    """Export all API keys with full metadata"""
    
    # Get all items
    output = run_bw(["list", "items"])
    if not output:
        return None
    
    items = json.loads(output)
    api_keys = []
    
    for item in items:
        name = item.get('name', 'Unknown')
        item_id = item.get('id', '')
        fields = item.get('fields', [])
        login = item.get('login', {})
        notes = item.get('notes', '')
        
        entry = {
            "item_name": name,
            "item_id": item_id,
            "keys": []
        }
        
        # Check custom fields for API keys
        for field in fields:
            field_name = field.get('name', '')
            field_value = field.get('value', '')
            field_type = field.get('type', 0)
            
            # Check if field looks like an API key
            is_api_field = any(keyword in field_name.upper() 
                             for keyword in ['API', 'KEY', 'TOKEN', 'SECRET'])
            
            if is_api_field and field_value and len(field_value) > 8:
                entry["keys"].append({
                    "field_name": field_name,
                    "value": field_value,
                    "type": "custom_field",
                    "hidden": field_type == 1
                })
        
        # Check password field
        password = login.get('password', '')
        if password and len(password) > 20:
            # Only include if item name suggests it's a credential
            if any(keyword in name.upper() 
                   for keyword in ['API', 'KEY', 'TOKEN', 'SECRET', 'PASSWORD']):
                entry["keys"].append({
                    "field_name": "password",
                    "value": password,
                    "type": "password_field",
                    "hidden": True
                })
        
        # Check notes field for connection strings
        if notes and any(proto in notes for proto in ['postgresql://', 'mysql://', 'mongodb://', 'redis://']):
            entry["keys"].append({
                "field_name": "connection_string",
                "value": notes.strip(),
                "type": "notes",
                "hidden": False
            })
        
        if entry["keys"]:
            api_keys.append(entry)
    
    # Build output structure
    output = {
        "export_date": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
        "total_items": len(api_keys),
        "total_keys": sum(len(e["keys"]) for e in api_keys),
        "api_keys": api_keys
    }
    
    return output


def export_flat_dict():
    """Export as flat dictionary for easy access: {"PROVIDER_API_KEY": "value"}"""
    output = run_bw(["list", "items"])
    if not output:
        return {}
    
    items = json.loads(output)
    flat_keys = {}
    
    for item in items:
        name = item.get('name', '')
        fields = item.get('fields', [])
        login = item.get('login', {})
        notes = item.get('notes', '')
        
        # Custom fields with PROVIDER_API_KEY pattern
        for field in fields:
            field_name = field.get('name', '')
            field_value = field.get('value', '')
            
            if field_value and len(field_value) > 8:
                # Use field name as key
                if 'API' in field_name.upper() or 'KEY' in field_name.upper():
                    flat_keys[field_name] = field_value
        
        # Password fields - use item name
        password = login.get('password', '')
        if password and len(password) > 20:
            if 'API' in name.upper() or 'KEY' in name.upper() or 'TOKEN' in name.upper():
                # Normalize name to PROVIDER_API_KEY format
                key_name = name.upper().replace(' ', '_').replace('-', '_')
                if not key_name.endswith('_KEY') and not key_name.endswith('_TOKEN'):
                    key_name += '_API_KEY'
                flat_keys[key_name] = password
    
    return flat_keys


def export_dot_env():
    """Export as .env file format: PROVIDER_API_KEY=value"""
    flat_keys = export_flat_dict()
    
    lines = [
        "# Bitwarden API Keys Export",
        f"# Generated: {subprocess.run(['date', '-Iseconds'], capture_output=True, text=True).stdout.strip()}",
        "# Source this file: source .env",
        "",
    ]
    
    for key_name, value in sorted(flat_keys.items()):
        # Escape special characters in value
        escaped_value = value.replace('"', '\\"')
        lines.append(f'{key_name}="{escaped_value}"')
    
    return "\n".join(lines)


def get_api_key(key_name):
    """Get a specific API key by name"""
    flat_keys = export_flat_dict()
    
    # Try exact match first
    if key_name in flat_keys:
        return flat_keys[key_name]
    
    # Try case-insensitive match
    key_name_upper = key_name.upper()
    for k, v in flat_keys.items():
        if k.upper() == key_name_upper:
            return v
    
    # Try partial match
    matches = {k: v for k, v in flat_keys.items() if key_name_upper in k.upper()}
    if len(matches) == 1:
        return list(matches.values())[0]
    elif len(matches) > 1:
        print(f"Multiple matches found for '{key_name}':", file=sys.stderr)
        for k in matches.keys():
            print(f"  - {k}", file=sys.stderr)
        return None
    
    return None


def list_api_keys():
    """List all available API key names"""
    flat_keys = export_flat_dict()
    return list(flat_keys.keys())


def print_summary(data):
    """Print human-readable summary"""
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"API KEYS EXPORT SUMMARY", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"Export Date: {data['export_date']}", file=sys.stderr)
    print(f"Total Items: {data['total_items']}", file=sys.stderr)
    print(f"Total Keys: {data['total_keys']}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)
    
    for entry in data['api_keys']:
        print(f"📄 {entry['item_name']}", file=sys.stderr)
        for key in entry['keys']:
            value = key['value']
            masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
            print(f"   • {key['field_name']}: {masked}", file=sys.stderr)
        print(file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: export full structured JSON
        data = export_all_api_keys()
        if data:
            print_summary(data)
            print(json.dumps(data, indent=2))
        else:
            print("Failed to export API keys", file=sys.stderr)
            sys.exit(1)
    elif sys.argv[1] == "--flat":
        # Export flat dictionary
        flat = export_flat_dict()
        print(json.dumps(flat, indent=2))
    elif sys.argv[1] == "--env":
        # Export as .env file format
        print(export_dot_env())
    elif sys.argv[1] == "--get":
        # Get specific API key
        if len(sys.argv) < 3:
            print("Usage: export_api_keys.py --get <KEY_NAME>", file=sys.stderr)
            print("Example: export_api_keys.py --get OPENROUTER_API_KEY", file=sys.stderr)
            sys.exit(1)
        key_name = sys.argv[2]
        value = get_api_key(key_name)
        if value:
            print(value)
        else:
            print(f"Key not found: {key_name}", file=sys.stderr)
            sys.exit(1)
    elif sys.argv[1] == "--list":
        # List all API key names
        keys = list_api_keys()
        print(f"\n{'='*40}", file=sys.stderr)
        print(f"Available API Keys ({len(keys)}):", file=sys.stderr)
        print(f"{'='*40}", file=sys.stderr)
        for key in sorted(keys):
            print(f"  • {key}", file=sys.stderr)
        print(f"{'='*40}\n", file=sys.stderr)
        # Also output as JSON for piping
        print(json.dumps(keys, indent=2))
    else:
        print("Usage: export_api_keys.py [OPTIONS]", file=sys.stderr)
        print("", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  (no args)     Export structured JSON with metadata", file=sys.stderr)
        print("  --flat        Export flat dictionary", file=sys.stderr)
        print("  --env         Export as .env file format", file=sys.stderr)
        print("  --get KEY     Get specific API key value", file=sys.stderr)
        print("  --list        List all available API key names", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  export_api_keys.py --env > .env", file=sys.stderr)
        print("  export_api_keys.py --get OPENROUTER_API_KEY", file=sys.stderr)
        print("  export_api_keys.py --list | jq '.[]'", file=sys.stderr)
        sys.exit(1)

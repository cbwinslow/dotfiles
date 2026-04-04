# Bitwarden Secrets Skill

Secure credential management for AI agents using Bitwarden Password Manager CLI (free plan).

**Location**: `~/dotfiles/ai/shared/skills/bitwarden/`

## Overview

This skill enables AI agents to retrieve secrets from Bitwarden and populate `.env` files or inject secrets at runtime. It uses API key + master password authentication for non-interactive operation.

## Authentication Workflow

1. **Login** with API key (once per session): `bw login --apikey --nointeraction`
2. **Unlock** vault with master password from `BW_PASSWORD` environment variable
3. **Use** `BW_SESSION` for all vault reads
4. **Lock** when finished: `bw lock`

Required environment variables:
- `BW_CLIENTID` – Bitwarden API key client ID
- `BW_CLIENTSECRET` – Bitwarden API key client secret
- `BW_PASSWORD` – Master password for unlock
Optional:
- `BW_SERVER_URL` – Self-hosted Bitwarden server URL

## Core Operations

### `get_status()`
Check Bitwarden configuration and vault status.

**Returns**: dict with `mode`, `configured`, `details`

### `login()`
Perform API key login. Not needed if `BW_SESSION` already valid.

**Returns**: dict with `success`, `message`

### `unlock(password=None)`
Unlock vault. Uses `BW_PASSWORD` from environment if `password` not provided.

**Returns**: dict with `success`, `message`

### `lock()`
Lock vault and clear session.

**Returns**: dict with `success`

### `get_secret(name, field='password')`
Retrieve a secret by exact item name.

**Parameters**:
- `name` (string): Exact item name in vault
- `field` (string): `password`, `username`, `note`, `uri`, or custom field name

**Returns**: dict with `success`, `value` (or `error`)

### `list_secrets(search=None)`
List item names with optional search filter.

**Parameters**:
- `search` (string, optional): Narrow search term

**Returns**: dict with `success`, `secrets` list, `count`

### `get_login(service)`
Get full login credentials (username, password, URI).

**Parameters**:
- `service` (string): Exact item name

**Returns**: dict with `success`, `credentials` or `error`

### `generate_password(length=32)`
Generate a secure password.

**Parameters**:
- `length` (int): Password length (default 32)

**Returns**: dict with `success`, `password`

---

## Mapping File Operations

### `populate_from_map(map_file)`
Populate `.env` file from a JSON mapping configuration.

**Parameters**:
- `map_file` (string): Path to `bitwarden-env-map.json`

**Returns**: dict with `success`, `message`, `errors`

**Mapping file format**:

```json
{
  "env_file": ".env",
  "create_backup": true,
  "write_mode": "merge",
  "secrets": [
    {
      "env": "OPENAI_API_KEY",
      "source": "item_field",
      "id": "optional-uuid",
      "search": "OpenAI API Key",
      "field": "password"
    }
  ]
}
```

- `write_mode`: `merge` (preserve existing), `replace` (rebuild), `ephemeral` (use `inject_env` instead)

### `inject_env(map_file, command=None)`
Inject secrets as environment variables and optionally run a command.

**Parameters**:
- `map_file` (string): Path to mapping file
- `command` (string, optional): Command to run with injected secrets

**Returns**: dict with `success`, `stdout`, `stderr`, `exit_code`

If `command` is `None`, returns export statements as `stdout`.

### `create_mapping_template(output_file, mode='password-manager')`
Create a template mapping file.

**Parameters**:
- `output_file` (string): Output path
- `mode` (string): Currently only `password-manager` supported

**Returns**: `True` if created

### `validate_configuration(map_file)`
Validate Bitwarden CLI availability, environment variables, and mapping file.

**Parameters**:
- `map_file` (string): Mapping file to validate

**Returns**: dict with detailed validation results

---

## Security Notes

- Never print secret values to stdout
- `.env` files created with 600 permissions
- Backups created as `.env.bak.TIMESTAMP` when `create_backup=true`
- Vault auto-locks in `inject_env` via `trap`
- Only narrow item lookups; avoid full vault enumeration
- Prefer `inject_env` over writing `.env` to disk

## Examples

```python
from bitwarden_skill import BitwardenSecrets

bw = BitwardenSecrets()

# Populate .env from mapping
result = bw.populate_from_map("bitwarden-env-map.json")

# Run with injection
result = bw.inject_env("bitwarden-env-map.json", "python app.py")

# Get a secret directly
value = bw.get_secret("OpenAI API Key", field="password")
```

## CLI Usage

```bash
# Create mapping template
bitwarden.sh create-template -o bitwarden-env-map.json

# Populate .env
bitwarden.sh populate-env-from-map

# Run with injected secrets
bitwarden.sh inject-env -- npm start

# Direct secret access
bitwarden.sh get-secret --name "API Key" --field password

# Vault management
bitwarden.sh login
bitwarden.sh unlock
bitwarden.sh status
bitwarden.sh lock
```

## Dependencies

- `bw` (Bitwarden CLI) – https://bitwarden.com/help/article/cli/
- `jq` – JSON processor

## License

MIT

# Bitwarden Secrets Skill - Free Password Manager Edition

**Location**: `~/dotfiles/ai/shared/skills/bitwarden/` (symlinked to `~/dotfiles/ai/skills/bitwarden`)

AI agent skill for automated secret retrieval from Bitwarden using the free Password Manager CLI. Populate `.env` files or inject secrets at runtime without manual copy/paste.

## Features

- Non-interactive authentication using API key (`BW_CLIENTID`, `BW_CLIENTSECRET`) + master password (`BW_PASSWORD`)
- Mapping file-driven secret retrieval (`bitwarden-env-map.json`)
- Multiple write modes: `merge` (preserve existing), `replace` (rebuild), `ephemeral` (inject only)
- Runtime injection: run commands with secrets in environment without writing `.env`
- Self-hosted Bitwarden support via `BW_SERVER_URL`
- Automatic backups of `.env` before modification
- Secure file permissions (600)
- Field support: `login.password`, `login.username`, `notes`, `uri`, custom fields

## Prerequisites

- Bitwarden CLI (`bw`) installed and in PATH
- `jq` installed
- Bitwarden account with API key (Settings → Security → API Key)
- Vault items with predictable names for secret lookup

## Environment Variables

Set these in your agent runner environment or shell profile:

```bash
export BW_CLIENTID="your-client-id"
export BW_CLIENTSECRET="your-client-secret"
export BW_PASSWORD="your-master-password"
# Optional for self-hosted:
export BW_SERVER_URL="https://your-bitwarden.example.com"
```

**Important**: `BW_PASSWORD` is your vault master password. Protect it like a secret. The API key authenticates the CLI, but unlock still requires the master password to decrypt vault data.

## Mapping File

Create `bitwarden-env-map.json` in your project root:

```json
{
  "env_file": ".env",
  "create_backup": true,
  "write_mode": "merge",
  "secrets": [
    {
      "env": "OPENAI_API_KEY",
      "source": "item_field",
      "search": "OpenAI API Key",
      "field": "password"
    },
    {
      "env": "DATABASE_URL",
      "source": "item_field",
      "search": "Production Database",
      "field": "password"
    },
    {
      "env": "GITHUB_USERNAME",
      "source": "item_field",
      "search": "GitHub Account",
      "field": "username"
    },
    {
      "env": "MY_CUSTOM_KEY",
      "source": "item_field",
      "id": "exact-uuid-if-you-have-it",
      "field": "custom_field_name"
    }
  ]
}
```

- `env`: environment variable name to set
- `source`: always `"item_field"` for this skill
- `search`: exact item name in Bitwarden (or use `id` for UUID lookup)
- `field`: `password`, `username`, `note(s)`, `uri`, or custom field name
- `create_backup`: boolean, create `.env.bak.TIMESTAMP` before modify
- `write_mode`: `merge` (default), `replace`, or `ephemeral`

## Usage

### Create a mapping template

```bash
bitwarden.sh create-template -o bitwarden-env-map.json
```

Edit the generated file with your actual item names.

### Populate .env file

```bash
# From project root (auto-detects bitwarden-env-map.json)
bitwarden.sh populate-env-from-map

# Or specify mapping file
bitwarden.sh populate-env-from-map path/to/map.json
```

The script will:
1. Auto-login using API key
2. Unlock vault using `BW_PASSWORD`
3. Retrieve each mapped secret by name/ID
4. Merge into `.env` (preserving unrelated keys)
5. Create timestamped backup if configured
6. Set `.env` permissions to 600
7. Lock vault

### Run commands with injected secrets (no .env written)

```bash
# Inject and run
bitwarden.sh inject-env -- npm run dev

# Or get exports to source
bitwarden.sh inject-env > /tmp/env.exports
source /tmp/env.exports
```

Injection mode automatically locks the vault on exit.

### Legacy direct secret access

```bash
# Get a specific secret
bitwarden.sh get-secret --name "OpenAI API Key" --field password

# List secrets (requires search term for safety)
bitwarden.sh list-secrets --search " OpenAI"

# Get full login credentials
bitwarden.sh get-login --service "GitHub"
```

### Manage vault

```bash
bitwarden.sh login      # API key login (non-interactive)
bitwarden.sh unlock     # Unlock using BW_PASSWORD
bitwarden.sh status     # Show vault status
bitwarden.sh lock       # Lock vault and clear session
```

## Security Best Practices

- Use specific item names; avoid broad searches
- Prefer `inject-env` over writing `.env` to disk
- Set `create_backup: true` to keep rollback points
- `.env` files created with 600 permissions (user read/write only)
- Do not commit `.env` or mapping files containing real item names
- After agent runs, ensure vault is locked (`bitwarden.sh lock`)
- Store `BW_PASSWORD`, `BW_CLIENTID`, `BW_CLIENTSECRET` in a secure runner secret store (e.g., GitHub Secrets, HashiCorp Vault) not in shell history

## Troubleshooting

**"Vault is locked"**: Ensure `BW_PASSWORD` is set and unlock runs before get operations. The skill auto-handles this if `login` and `unlock` have been called.

**"Item not found"**: Check that the `search` string exactly matches the Bitwarden item name. Use `list-secrets --search "<partial>"` to debug.

**"bw: command not found"**: Install Bitwarden CLI: https://bitwarden.com/help/article/cli/#install-the-cli

**"jq: command not found"**: Install jq: `apt-get install jq` or `brew install jq`

**Session persists too long**: Run `bitwarden.sh lock` when done. Injection mode auto-locks.

**Self-hosted server not used**: Set `BW_SERVER_URL` and ensure SSL/TLS is valid or set `NODE_EXTRA_CA_CERTS` if self-signed.

## Python API

For AI agents that embed Python:

```python
from bitwarden_skill import BitwardenSecrets

bw = BitwardenSecrets()

# Populate .env from mapping
result = bw.populate_from_map("bitwarden-env-map.json")
if result["success"]:
    print("OK")
else:
    print("Errors:", result.get("errors"))

# Inject and run command
result = bw.inject_env("bitwarden-env-map.json", "python app.py")
print(result["stdout"])

# Get single secret
value = bw.get_secret("OpenAI API Key", field="password")

# Generate password
pwd = bw.generate_password(length=32)
```

## File Structure

```
~/dotfiles/ai/shared/skills/bitwarden/
├── bitwarden.sh              # Main CLI (requires bw, jq)
├── bitwarden_skill.py        # Python class wrapper
├── bitwarden_skill_wrapper.py  # High-level wrapper for agents
├── .gitignore                # Excludes .env, session files, mappings
├── README.md                 # This file
├── CHANGELOG.md              # Version history
└── SKILL.md                  # Skill definition for agents
```

## .gitignore

The skill directory includes a `.gitignore` that excludes:
- `.env`, `.env.bak.*`
- `session.env`, `~/.config/bitwarden-ai/`
- `*bitwarden-env-map.json` (unless in examples/)
- Python cache, logs, temp files

## Notes

- This skill uses **Bitwarden Password Manager CLI** on the **free plan**. No Secrets Manager or paid features required.
- API key login (`bw login --apikey`) authenticates the CLI session but **does not replace vault unlock**. Unlock with `BW_PASSWORD` is mandatory to decrypt items.
- The agent gains access to the authenticated user's personal vault. Use narrow item lookups and avoid listing entire vault.
- This is a convenience automation pattern, not a least-privilege secrets platform. For production multi-user scenarios, consider Bitwarden Secrets Manager with machine accounts (not covered by this skill).

## License

MIT

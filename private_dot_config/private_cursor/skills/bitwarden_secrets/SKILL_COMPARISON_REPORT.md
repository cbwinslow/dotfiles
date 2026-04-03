# Bitwarden SKILL.md Comparison Report

**Date:** March 29, 2026  
**Analyst:** Cascade AI  
**Scope:** Comparing our Bitwarden Secrets skill with community examples

---

## Sources Analyzed

| Source | URL | Approach |
|--------|-----|----------|
| **OpenClaw Skills (Jimihford)** | `github.com/openclaw/skills` | Raw `bw` CLI with tmux session management |
| **OpenClaw Skills (Asleep123)** | `github.com/openclaw/skills` | `rbw` CLI (unofficial Bitwarden CLI) |
| **Our Skill** | `~/dotfiles/ai/skills/bitwarden_secrets/` | Python wrapper with advanced search |

---

## Executive Summary

| Aspect | OpenClaw (bw CLI) | OpenClaw (rbw) | Our Skill |
|--------|-------------------|----------------|-----------|
| **Architecture** | Shell/tmux based | Shell/agent-based | Python module + CLI |
| **Complexity** | High (tmux management) | Medium (background agent) | Low (direct Python) |
| **AI Integration** | Command orchestration | Command orchestration | Native Python import |
| **API Key Focus** | ❌ General passwords | ❌ General passwords | ✅ **Purpose-built for API keys** |
| **Pattern Matching** | ❌ Manual search | ❌ Manual search | ✅ **Fuzzy pattern matching** |
| **Bulk Export** | ❌ Item-by-item | ❌ Item-by-item | ✅ **JSON/.env export** |
| **Multi-Agent** | ⚠️ Shell dependent | ⚠️ Shell dependent | ✅ **8-agent unified loader** |
| **Vault Analysis** | ❌ | ❌ | ✅ **Cleanup recommendations** |

---

## Detailed Analysis

### 1. OpenClaw Bitwarden Skill (Jimihford) - Raw bw CLI Approach

**File:** `skills/jimihford/openclaw-bitwarden/SKILL.md`

#### Structure
```yaml
---
name: bitwarden
description: Set up and use Bitwarden CLI (bw)
homepage: https://bitwarden.com/help/cli/
metadata:
  openclaw:
    emoji: "🔐"
    requires:
      bins: ["bw", "tmux"]
    install:
      - id: brew-bw
        kind: brew
        formula: bitwarden-cli
---
```

#### Key Features
- **Frontmatter metadata** with OpenClaw-specific schema
- **Emoji tagging** (🔐) for visual identification
- **Dependency tracking** (brew formulas)
- **tmux session management** for BW_SESSION persistence
- **Vaultwarden testing** support with Docker Compose

#### Workflow Steps
1. Check CLI: `bw --version`
2. Check status: `bw status`
3. Login: `bw login`
4. Create tmux session
5. Unlock: `bw unlock` inside tmux
6. Export session: `export BW_SESSION`
7. Verify: `bw sync`

#### tmux Session Management
```bash
SOCKET_DIR="${CLAWDBOT_TMUX_SOCKET_DIR:-${TMPDIR:-/tmp}/openclaw-tmux-sockets}"
SESSION="bw-auth-$(date +%Y%m%d-%H%M%S)"
tmux -S "$SOCKET" new -d -s "$SESSION"
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- 'export BW_SESSION=$(bw unlock --raw)' Enter
```

#### Guardrails
- Never paste secrets into logs
- Always use tmux for BW_SESSION
- Prefer `bw get password` over JSON parsing
- Lock vault when done

#### Strengths
✅ **MCP-ready metadata** - Structured frontmatter for AI agent systems  
✅ **Testing infrastructure** - Vaultwarden Docker Compose setup  
✅ **Security guardrails** - Explicit "never paste secrets" warnings  
✅ **Session persistence** - tmux handles BW_SESSION across commands  

#### Weaknesses
❌ **Overly complex** - tmux management is cumbersome  
❌ **Not API-key focused** - Generic password management  
❌ **No pattern matching** - Manual search required  
❌ **No bulk export** - Item-by-item retrieval  
❌ **Shell-dependent** - Requires tmux socket management  

---

### 2. OpenClaw Bitwarden Skill (Asleep123) - rbw CLI Approach

**File:** `skills/asleep123/bitwarden/SKILL.md`

#### Approach
Uses `rbw` - unofficial Bitwarden CLI that maintains background agent (like ssh-agent)

#### Key Difference from Jimihford's
- **rbw** maintains persistent agent instead of tmux
- **Simpler session management** - agent holds keys in memory
- **Same metadata structure** as Jimihford's skill

#### rbw Advantages
- No environment variable juggling
- Background process maintains session
- Similar to `ssh-agent` or `gpg-agent` pattern

#### rbw Disadvantages
- Unofficial tool (not Bitwarden-maintained)
- Additional dependency
- Less widely adopted

---

### 3. Our Skill - Python Wrapper Approach

**Files:**
- `SKILL.md` - Documentation
- `bitwarden_secrets.py` - Python module
- `export_api_keys.py` - Export functionality
- `advanced_search.py` - Pattern matching
- `shell_loader.sh` - Shell integration

#### Structure
```markdown
# Bitwarden Secrets Management Skill

No YAML frontmatter - Markdown-focused documentation
```

#### Key Features
- **Python-native** - Import directly: `from bitwarden_secrets import BitwardenSecrets`
- **Advanced search** - Pattern matching for `PROVIDER_API_KEY` format
- **Bulk export** - JSON, flat dictionary, and .env formats
- **Vault analysis** - Identify cleanup opportunities
- **Shell integration** - `bw_get_key()`, `bw_export_env()` functions
- **Multi-agent support** - Unified loader for 8 AI agents

#### Usage Pattern
```python
from bitwarden_secrets import BitwardenSecrets

bw = BitwardenSecrets()
api_key = bw.get_api_key("openrouter")  # Fuzzy matching

# Or export all
from export_api_keys import export_dot_env
print(export_dot_env())  # Ready-to-source .env file
```

#### Shell Integration
```bash
source ~/dotfiles/ai/skills/bitwarden_secrets/shell_loader.sh

bw_get_key OPENROUTER_API_KEY
bw_export_env > .env
bw_list_keys
```

#### Strengths
✅ **Purpose-built for API keys** - Pattern matching, bulk export  
✅ **Native Python** - Import and use directly in code  
✅ **Advanced search** - Finds keys in custom fields by pattern  
✅ **Bulk operations** - Export 40+ keys to .env in one command  
✅ **Multi-format export** - JSON, flat dict, .env  
✅ **Vault analysis** - Cleanup recommendations  
✅ **8-agent support** - Unified loader architecture  

#### Weaknesses
❌ **No YAML frontmatter** - Not MCP-ready metadata  
❌ **No tmux/agent pattern** - Relies on BW_SESSION env var  
❌ **No testing infrastructure** - No Vaultwarden Docker setup  
❌ **No security guardrails section** - Missing explicit warnings  

---

## Gap Analysis: What We Should Adopt

### 1. YAML Frontmatter (Priority: HIGH)

**What they have:**
```yaml
---
name: bitwarden
description: Set up and use Bitwarden CLI
description: Use when installing the CLI, unlocking vault, or reading/generating secrets
homepage: https://bitwarden.com/help/cli/
metadata:
  openclaw:
    emoji: "🔐"
    requires:
      bins: ["bw"]
    install:
      - id: brew-bw
        kind: brew
        formula: bitwarden-cli
---
```

**Why it matters:**
- AI agents can parse skill capabilities automatically
- Dependency tracking for installation
- Emoji categorization for visual scanning
- Standardized metadata across skill repositories

**Recommendation:** Add YAML frontmatter to our SKILL.md

---

### 2. Security Guardrails Section (Priority: HIGH)

**What they have:**
```markdown
## Guardrails

- Never paste secrets into logs, chat, or code
- Always use tmux to maintain BW_SESSION across commands
- Prefer `bw get password` over parsing full item JSON
- If command returns "Vault is locked", re-run `bw unlock`
- Do not run authenticated `bw` commands outside tmux
- Lock vault when done: `bw lock`
```

**Why it matters:**
- Explicit security warnings prevent accidents
- Clear guidelines for AI agents
- Standardized "never paste secrets" rule

**Recommendation:** Add Guardrails section to our SKILL.md

---

### 3. Testing Infrastructure (Priority: MEDIUM)

**What they have:**
```markdown
## Testing with Vaultwarden

Docker Compose setup for local testing
- Vaultwarden (self-hosted Bitwarden)
- Caddy reverse proxy
- mkcert for local HTTPS
- Test scripts included
```

**Why it matters:**
- Agents can test skills safely without production vault
- Reproducible testing environment
- Good for CI/CD pipelines

**Recommendation:** Add Vaultwarden Docker setup for testing

---

### 4. CLI Command Reference (Priority: MEDIUM)

**What they have:**
```markdown
## Common Commands

| Command | Description |
|---------|-------------|
| `bw status` | Check login/lock status (JSON) |
| `bw login` | Login with email/password or API key |
| `bw unlock` | Unlock vault, returns session key |
...
```

**Why it matters:**
- Quick reference for developers
- Standardized command documentation
- Easy for AI agents to scan

**Recommendation:** Add comprehensive command reference table

---

## What They Should Adopt From Us

### 1. API-Key Focus
Their skills are generic password managers. Our skill is purpose-built for API key injection into AI agents and development workflows.

### 2. Pattern Matching
We find `OPENROUTER_API_KEY` in custom fields automatically. They require manual search.

### 3. Bulk Export
We export 40+ keys to .env in one command. They do item-by-item retrieval.

### 4. Python Native Integration
We can `import` directly. They require shell command orchestration.

### 5. Vault Analysis
We provide cleanup recommendations. They have no analysis capabilities.

---

## Recommendations for Our Skill

### Immediate (High Priority)

1. **Add YAML frontmatter** with metadata schema
2. **Add Guardrails section** with security warnings
3. **Add emoji** (🔐) for visual categorization

### Short-term (Medium Priority)

4. **Add CLI command reference table**
5. **Add Vaultwarden testing setup**
6. **Add workflow diagrams** (like their tmux example)

### Long-term (Low Priority)

7. **Consider rbw agent approach** as alternative backend
8. **Add more testing scripts**
9. **Create video/gif demonstrations**

---

## Comparison Matrix

| Feature | Jimihford (bw) | Asleep123 (rbw) | Our Skill | Recommendation |
|---------|---------------|-----------------|-----------|----------------|
| **YAML frontmatter** | ✅ | ✅ | ❌ | **Add** |
| **Security guardrails** | ✅ | ? | ❌ | **Add** |
| **Emoji tagging** | ✅ | ✅ | ❌ | **Add** |
| **CLI reference table** | ✅ | ? | ⚠️ Partial | **Expand** |
| **Testing infrastructure** | ✅ | ? | ❌ | **Consider** |
| **API-key focused** | ❌ | ❌ | ✅ | **Keep** |
| **Pattern matching** | ❌ | ❌ | ✅ | **Keep** |
| **Bulk export** | ❌ | ❌ | ✅ | **Keep** |
| **Python native** | ❌ | ❌ | ✅ | **Keep** |
| **Vault analysis** | ❌ | ❌ | ✅ | **Keep** |
| **Multi-agent support** | ❌ | ❌ | ✅ | **Keep** |
| **.env export** | ❌ | ❌ | ✅ | **Keep** |

---

## Conclusion

Our skill is **technically superior** for AI agent API key management but **structurally behind** on documentation standards.

**Action items:**
1. Add YAML frontmatter with OpenClaw-compatible metadata
2. Add explicit Guardrails section
3. Add CLI command reference table
4. Keep our advanced features (pattern matching, bulk export, Python API)

Our skill should be the **reference implementation** for Bitwarden API key management, but we need to adopt their documentation standards for broader compatibility.

---

## Appendix: Skill File Locations

**Our skill:**
- `~/dotfiles/ai/skills/bitwarden_secrets/SKILL.md`
- `~/dotfiles/ai/skills/bitwarden_secrets/bitwarden_secrets.py`
- `~/dotfiles/ai/skills/bitwarden_secrets/export_api_keys.py`
- `~/dotfiles/ai/skills/bitwarden_secrets/advanced_search.py`
- `~/dotfiles/ai/skills/bitwarden_secrets/shell_loader.sh`

**Reference skills:**
- `https://github.com/openclaw/skills/tree/main/skills/jimihford/openclaw-bitwarden`
- `https://github.com/openclaw/skills/tree/main/skills/asleep123/bitwarden`

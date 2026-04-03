# Universal AI Workspace Mandates

## Core Directives (All Agents)

### 1. The Context Mandate
- **Always Search First**: Before starting any task, search the codebase (and memory, if available) for prior context. Do not guess.
- **Reproduce Before Fixing**: Verify bugs with a reproduction script before attempting a fix.
- **Test Your Work**: No code is complete without a passing test case.

### 2. The Memory Mandate (Letta Integration)
- **Recall**: Check long-term memory at session start (`letta archival-search`).
- **Store**: Save key decisions and architectural facts (`letta archival-insert`).
- **Sync**: Update agent personas if roles change (`letta memory-update`).

### 3. The Security Mandate
- **No Secrets**: Never commit API keys, passwords, or .env files.
- **Surgical Edits**: Prefer focused changes over full-file rewrites to preserve context and comments.

### 4. The Tooling Mandate
- **Use Existing Tools**: Prefer `ripgrep` (`rg`), `fd`, and `git` over custom scripts for file operations.
- **Respect Configs**: Adhere to `.editorconfig`, `.prettierrc`, and other linter settings.

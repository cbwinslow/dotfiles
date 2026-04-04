# Gemini CLI Workspace Mandates

## Core Directive: Persistent Memory via Letta

To maintain cross-session intelligence and automate context retrieval, the following workflow is **mandatory** for all non-trivial tasks.

### 1. The Recall Mandate
Before starting any new research, implementation, or debugging task, search the Letta archival database for relevant historical context.
- **Tool**: `letta archival-search <agent-id> "<query>"`
- **Default Agent**: `coder` (agent-2eed95af-8ec1-475d-82f3-7d554cc0c9ed)
- **Goal**: Identify previous decisions, known bugs, or environmental constraints already established in earlier sessions.

### 2. The Decision/Fact Mandate
Any "Ground Truth" discovered or established during a session must be committed to Letta's long-term memory immediately.
- **Tool**: `letta archival-insert <agent-id> "<fact>" "<tags>"`
- **Required Tags**: `decision`, `config`, `discovery`, `project-x`
- **Examples**:
    - "Server IP is 192.168.4.101" (tag: `config,infra`)
    - "Using pgvector for vector search" (tag: `decision,letta`)

### 3. The Automation Strategy
Leverage Letta's multi-agent system to offload specialized queries:
- **Infrastructure**: Use `infra-assistant` for Docker, Postgres, and system-level checks.
- **Operations**: Use `ops-monitor` for health checks and log analysis.
- **Code**: Use `coder` for all implementation and technical research.

### 4. Verification & Validation
A task is not considered "complete" until:
1. The behavioral correctness is verified via tests.
2. A summary of the outcome and final decisions has been `archival-insert`ed into Letta for future recall.

## Dotfile Management
- Strictly adhere to established `.dotfiles` structure.
- Never modify `.letta` or sensitive infrastructure files unless explicitly requested.
- Prioritize surgical updates over full-file rewrites.

# Windsurf AI Asset Import Setup

## Overview
This directory contains AI assets that have been imported from the centralized AI system at `~/dotfiles/ai/` using a symlink-only approach. This setup allows Windsurf to access shared skills while maintaining a single source of truth.

## Directory Structure

### Skills Directory (`./skills/`)
- **Symlinked Shared Skills**: These are symbolic links to the centralized shared skills
  - `cbw_rag` - Semantic search and file indexing
  - `bitwarden` - Secure credential management  
  - `conversation_logging` - Automatic conversation logging
  - `letta_server` - Letta server health monitoring
  - `memory_sync` - Memory synchronization
  - `cli_operations` - Command line operations
- **Copied Windsurf-Specific Tools**: These are local copies of Windsurf-specific tools
  - `.system/` - All Windsurf-specific configurations and tools

### Shared Skills Directory (`./shared_skills`)
- **Symlink**: Points to `~/dotfiles/ai/shared/skills/`
- **Purpose**: Provides access to all shared skills in the centralized system

## Import Process

### Step 1: Create Directory Structure
```bash
mkdir -p ~/.windsurf/ai/skills
mkdir -p ~/.windsurf/ai/shared_skills
```

### Step 2: Create Symlinks for Shared Skills
```bash
ln -s ~/dotfiles/ai/shared/skills/cbw_rag ~/.windsurf/ai/skills/cbw_rag
ln -s ~/dotfiles/ai/shared/skills/bitwarden ~/.windsurf/ai/skills/bitwarden
ln -s ~/dotfiles/ai/shared/skills/conversation_logging ~/.windsurf/ai/skills/conversation_logging
ln -s ~/dotfiles/ai/shared/skills/letta_server ~/.windsurf/ai/skills/letta_server
ln -s ~/dotfiles/ai/shared/skills/memory_sync ~/.windsurf/ai/skills/memory_sync
ln -s ~/dotfiles/ai/shared/skills/cli_operations ~/.windsurf/ai/skills/cli_operations
```

### Step 3: Copy Windsurf-Specific Tools
```bash
cp -r ~/dotfiles/ai/skills/.system ~/.windsurf/ai/skills/
```

### Step 4: Create Shared Skills Symlink
```bash
ln -s ~/dotfiles/ai/shared/skills ~/.windsurf/ai/shared_skills
```

## Key Benefits

1. **Single Source of Truth**: All shared skills maintained in `~/dotfiles/ai/shared/skills/`
2. **Automatic Updates**: New skills added to shared directory automatically available in Windsurf
3. **No Duplication**: Avoids copying files, preventing documentation drift
4. **Flexible Loading**: Windsurf's unified loader can handle symlinks
5. **Complete Integration**: All skills accessible through Windsurf's skill registry

## Maintenance

### Adding New Shared Skills
1. Add the skill to `~/dotfiles/ai/shared/skills/`
2. Create a symlink in `~/.windsurf/ai/skills/` following the naming convention
3. Update the skill registry if needed

### Updating Existing Skills
1. Update the skill in `~/dotfiles/ai/shared/skills/`
2. The changes will automatically be reflected in Windsurf

### Troubleshooting
- **Missing Skills**: Verify symlinks are intact
- **Path Issues**: Check that `~/dotfiles/ai/shared/skills/` exists
- **Loading Problems**: Ensure Windsurf's unified loader can access the symlinked directories

## File Inventory

### Symlinked Files
- `cbw_rag` → `~/dotfiles/ai/shared/skills/cbw_rag`
- `bitwarden` → `~/dotfiles/ai/shared/skills/bitwarden`
- `conversation_logging` → `~/dotfiles/ai/shared/skills/conversation_logging`
- `letta_server` → `~/dotfiles/ai/shared/skills/letta_server`
- `memory_sync` → `~/dotfiles/ai/shared/skills/memory_sync`
- `cli_operations` → `~/dotfiles/ai/shared/skills/cli_operations`

### Copied Files
- `.system/` → Local copy of Windsurf-specific tools

### Symlink Directories
- `shared_skills` → `~/dotfiles/ai/shared/skills`

## Dependencies

- **Letta Server**: Required for memory integration (port 8283)
- **Bitwarden CLI**: Required for credential management
- **Python 3**: Required for skill execution
- **Windsurf Configuration**: Must be configured to recognize the skill locations

## Notes

- This setup uses symlinks to maintain a single source of truth
- Windsurf-specific tools are copied to preserve independence
- The unified loader automatically detects and loads all available skills
- Any changes to shared skills are immediately reflected in Windsurf
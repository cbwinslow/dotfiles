# CBW AI Shared Skills Framework
# Centralized skills accessible by all AI tools (OpenCode, KiloCode, Gemini, Qwen, Claude, etc.)

## Architecture

This folder contains reusable skills that any AI agent can invoke:

- **rag_query**: Query the RAG database for context
- **file_search**: Find files across all indexed directories  
- **code_analysis**: Analyze code patterns and duplicates
- **task_automation**: Run common automation tasks

## Usage

All AI tools should include this folder in their skill path:
- Windsurf: Set `CBW_SHARED_SKILLS=/home/cbwinslow/dotfiles/ai/shared/skills`
- Cline: Reference in mcp_settings.json
- OpenCode: Add to agent skills

## Skills Available

1. **cbw_rag_query** - Semantic search across all indexed files
2. **cbw_find_duplicates** - Find duplicate files to clean up storage
3. **cbw_similar_code** - Find similar code patterns
4. **cbw_index_files** - Index new directories

## Configuration

All skills use the centralized secrets from `~/.bash_secrets`

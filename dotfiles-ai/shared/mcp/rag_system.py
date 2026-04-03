# CBW RAG MCP Server
# Centralized MCP server for all AI tools
# This is a symlink to the actual implementation in projects/ai/rag_system/
# Edit the source at: /home/cbwinslow/projects/ai/rag_system/mcp_server.py

# The actual implementation is kept in the projects folder
# This file exists for backwards compatibility
# All AI tools should reference: /home/cbwinslow/dotfiles/ai/shared/mcp/rag_system.py

import sys
sys.path.insert(0, '/home/cbwinslow/projects/ai/rag_system')
from mcp_server import *

if __name__ == '__main__':
    main()

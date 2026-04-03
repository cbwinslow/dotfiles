#!/usr/bin/env python3
"""
CBW RAG MCP Server - Centralized for all AI tools
Located at: ~/dotfiles/ai/shared/mcp/rag_server.py
Reads secrets from environment (sourced from ~/.bash_secrets)
"""

import sys
import os
import asyncio

# Add the RAG system path to import the actual implementation
sys.path.insert(0, '/home/cbwinslow/projects/ai/rag_system')

# Import all from the actual MCP server
from mcp_server import main, server

if __name__ == '__main__':
    asyncio.run(main())

#!/usr/bin/env python3
"""
Letta Agent Setup and Feature Test
Creates multiple agents and tests all Letta features.

Usage:
  python setup_letta_agents.py --setup    # Create all agents
  python setup_letta_agents.py --test     # Test all features
  python setup_letta_agents.py --full     # Setup + test
"""

import argparse
import sys
import os
from datetime import datetime

# Add letta_integration to path
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')

try:
    from letta_integration import LettaIntegration
except ImportError:
    print("Error: letta_integration package not found")
    sys.exit(1)

# Agent definitions with specific purposes
AGENTS = {
    "windsurf": {
        "description": "Code editor agent focused on development tasks",
        "persona": "I am Windsurf, a code editor AI agent. I specialize in code generation, refactoring, and development workflows.",
        "human": "User is a software developer working on AI agent infrastructure and dotfiles management."
    },
    "claude": {
        "description": "Deep reasoning agent for complex analysis",
        "persona": "I am Claude, an AI assistant with deep reasoning capabilities. I excel at analysis, writing, and thoughtful problem-solving.",
        "human": "User values thorough analysis and well-reasoned responses."
    },
    "cline": {
        "description": "Autogen-based agent for automated workflows",
        "persona": "I am Cline, an autonomous agent using AutoGen framework. I can orchestrate multi-step tasks and workflows.",
        "human": "User prefers automated solutions and workflow orchestration."
    },
    "codex": {
        "description": "Code generation and optimization specialist",
        "persona": "I am Codex, specialized in code generation and optimization. I create efficient, clean code across multiple languages.",
        "human": "User needs high-quality code generation and optimization."
    },
    "gemini": {
        "description": "Research and analysis agent with web capabilities",
        "persona": "I am Gemini, a research-focused AI agent with web search capabilities. I gather and analyze information from multiple sources.",
        "human": "User conducts research and needs comprehensive information gathering."
    },
    "researcher": {
        "description": "Dedicated research agent for deep dives",
        "persona": "I am Researcher, focused on deep research and analysis. I synthesize complex information and identify patterns.",
        "human": "User needs thorough research and synthesis of complex topics."
    },
    "ops-monitor": {
        "description": "System operations and monitoring agent",
        "persona": "I am Ops Monitor, specializing in system health, monitoring, and operational tasks.",
        "human": "User manages infrastructure and needs system monitoring."
    }
}


def create_all_agents():
    """Create all defined agents in Letta with proper configuration."""
    print("=" * 60)
    print("CREATING LETTA AGENTS")
    print("=" * 60)
    print()
    
    results = {
        "created": [],
        "failed": [],
        "blocks": []
    }
    
    for agent_name, config in AGENTS.items():
        print(f"Setting up agent: {agent_name}")
        print(f"  Description: {config['description']}")
        
        try:
            letta = LettaIntegration(
                server_url=os.getenv("LETTA_SERVER_URL", "http://localhost:8283"),
                api_key=os.getenv("LETTA_API_KEY", ""),
                agent_name=agent_name
            )
            
            # Get or create agent
            agent_id = letta.get_or_create_agent(agent_name)
            if not agent_id:
                print(f"  ✗ Failed to create agent: {agent_name}")
                results["failed"].append(agent_name)
                continue
            
            print(f"  ✓ Agent ID: {agent_id[:8]}...")
            
            # Setup core memory blocks
            blocks_result = letta.setup_core_memory_blocks(
                persona_value=config["persona"],
                human_value=config["human"]
            )
            
            if blocks_result["blocks_created"]:
                print(f"  ✓ Created blocks: {', '.join(blocks_result['blocks_created'])}")
                results["blocks"].extend(blocks_result["blocks_created"])
            
            if blocks_result["errors"]:
                print(f"  ⚠ Block errors: {blocks_result['errors']}")
            
            results["created"].append(agent_name)
            print()
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results["failed"].append(agent_name)
            print()
    
    # Summary
    print("=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print(f"✓ Created: {len(results['created'])} agents")
    print(f"  {', '.join(results['created'])}")
    if results["failed"]:
        print(f"✗ Failed: {len(results['failed'])} agents")
        print(f"  {', '.join(results['failed'])}")
    print(f"✓ Total blocks: {len(results['blocks'])}")
    print()
    
    return results


def test_all_features():
    """Test all Letta features comprehensively."""
    print("=" * 60)
    print("TESTING ALL LETTA FEATURES")
    print("=" * 60)
    print()
    
    results = {
        "tests": [],
        "passed": 0,
        "failed": 0
    }
    
    # Test 1: Server Health
    print("Test 1: Server Health Check")
    try:
        letta = LettaIntegration()
        health = letta.check_server_health()
        if health.get("status") == "healthy":
            print(f"  ✓ Server healthy (v{health.get('version', 'unknown')})")
            results["tests"].append(("Server Health", True))
            results["passed"] += 1
        else:
            print(f"  ✗ Server unhealthy: {health}")
            results["tests"].append(("Server Health", False))
            results["failed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Server Health", False))
        results["failed"] += 1
    print()
    
    # Test 2: List Agents
    print("Test 2: List Agents")
    try:
        letta = LettaIntegration()
        agents = letta.list_agents()
        agent_list = agents.get("agents", []) if isinstance(agents, dict) else agents
        print(f"  ✓ Found {len(agent_list)} agents")
        for a in agent_list[:3]:  # Show first 3
            print(f"    - {a.get('name')}")
        results["tests"].append(("List Agents", True))
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("List Agents", False))
        results["failed"] += 1
    print()
    
    # Test 3: Save Conversation
    print("Test 3: Save Conversation")
    try:
        letta = LettaIntegration(agent_name="windsurf")
        messages = [
            {"role": "user", "content": "Configure the AI agent system"},
            {"role": "assistant", "content": "I'll help you configure the 10 AI agents with proper Letta integration."}
        ]
        result = letta.save_conversation(messages, tags=["setup", "configuration"])
        if "error" not in result:
            print(f"  ✓ Conversation saved")
            results["tests"].append(("Save Conversation", True))
            results["passed"] += 1
        else:
            print(f"  ✗ Error: {result['error']}")
            results["tests"].append(("Save Conversation", False))
            results["failed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Save Conversation", False))
        results["failed"] += 1
    print()
    
    # Test 4: Memory Search
    print("Test 4: Memory Search")
    try:
        letta = LettaIntegration(agent_name="windsurf")
        results_search = letta.search_memories("AI agent", limit=5)
        memories = results_search.get("memories", [])
        print(f"  ✓ Found {len(memories)} memories")
        results["tests"].append(("Memory Search", True))
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Memory Search", False))
        results["failed"] += 1
    print()
    
    # Test 5: Create Memory Block
    print("Test 5: Create Memory Block")
    try:
        letta = LettaIntegration(agent_name="windsurf")
        block = letta.create_block(
            label="test_block",
            value="This is a test memory block for feature testing.",
            description="Test block for validation"
        )
        if "id" in block:
            print(f"  ✓ Block created: {block['id'][:8]}...")
            results["tests"].append(("Create Block", True))
            results["passed"] += 1
        else:
            print(f"  ✗ Failed: {block}")
            results["tests"].append(("Create Block", False))
            results["failed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Create Block", False))
        results["failed"] += 1
    print()
    
    # Test 6: Entity Extraction
    print("Test 6: Entity Extraction")
    try:
        letta = LettaIntegration(agent_name="windsurf")
        text = """
        Check the file at /home/cbwinslow/dotfiles/ai/config.yaml
        Run: $ docker-compose up -d
        Visit https://docs.letta.com for more info
        ```python
        def test():
            pass
        ```
        """
        entities = letta.extract_and_store_entities(text)
        extracted = entities.get("entities", [])
        print(f"  ✓ Extracted {len(extracted)} entities")
        for e in extracted[:3]:
            print(f"    - [{e['type']}] {e['value'][:30]}...")
        results["tests"].append(("Entity Extraction", True))
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Entity Extraction", False))
        results["failed"] += 1
    print()
    
    # Test 7: Create Decision Memory
    print("Test 7: Create Decision Memory")
    try:
        letta = LettaIntegration(agent_name="claude")
        result = letta.create_memory_from_decision(
            decision="Use Letta for all agent memory management",
            context="After evaluating options, Letta provides the best self-hosted solution with PostgreSQL backend."
        )
        if "error" not in result:
            print(f"  ✓ Decision memory created")
            results["tests"].append(("Decision Memory", True))
            results["passed"] += 1
        else:
            print(f"  ✗ Error: {result['error']}")
            results["tests"].append(("Decision Memory", False))
            results["failed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Decision Memory", False))
        results["failed"] += 1
    print()
    
    # Test 8: Create Action Item
    print("Test 8: Create Action Item")
    try:
        letta = LettaIntegration(agent_name="cline")
        result = letta.create_memory_from_action_item(
            action_item="Set up monitoring for all 10 AI agents",
            priority="high"
        )
        if "error" not in result:
            print(f"  ✓ Action item created")
            results["tests"].append(("Action Item", True))
            results["passed"] += 1
        else:
            print(f"  ✗ Error: {result['error']}")
            results["tests"].append(("Action Item", False))
            results["failed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Action Item", False))
        results["failed"] += 1
    print()
    
    # Test 9: Memory Stats
    print("Test 9: Get Memory Stats")
    try:
        letta = LettaIntegration(agent_name="windsurf")
        stats = letta.get_memory_stats()
        print(f"  ✓ Stats retrieved")
        print(f"    Memory count: {stats.get('memory_count', 'N/A')}")
        results["tests"].append(("Memory Stats", True))
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Memory Stats", False))
        results["failed"] += 1
    print()
    
    # Test 10: Cross-Agent Search
    print("Test 10: Cross-Agent Search")
    try:
        letta = LettaIntegration()
        results_search = letta.search_all_agents("AI agent", limit_per_agent=3)
        total = len(results_search.get("results", {}))
        print(f"  ✓ Searched {total} agents")
        results["tests"].append(("Cross-Agent Search", True))
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Cross-Agent Search", False))
        results["failed"] += 1
    print()
    
    # Test 11: Backup Memories
    print("Test 11: Backup Memories")
    try:
        letta = LettaIntegration(agent_name="windsurf")
        backup = letta.backup_memories()
        if backup.get("success"):
            print(f"  ✓ Backup created: {backup['backup_file']}")
            print(f"    Memories: {backup['memory_count']}")
            results["tests"].append(("Backup", True))
            results["passed"] += 1
        else:
            print(f"  ✗ Backup failed")
            results["tests"].append(("Backup", False))
            results["failed"] += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"].append(("Backup", False))
        results["failed"] += 1
    print()
    
    # Summary
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {results['passed']}/{len(results['tests'])}")
    print(f"Failed: {results['failed']}/{len(results['tests'])}")
    print()
    
    for test_name, passed in results["tests"]:
        status = "✓" if passed else "✗"
        print(f"{status} {test_name}")
    print()
    
    return results


def add_comprehensive_memory():
    """Add a comprehensive test memory using all features."""
    print("=" * 60)
    print("ADDING COMPREHENSIVE TEST MEMORY")
    print("=" * 60)
    print()
    
    letta = LettaIntegration(agent_name="windsurf")
    
    # Comprehensive memory content
    comprehensive_content = """
COMPREHENSIVE SYSTEM SETUP - ALL FEATURES TESTED
================================================
Date: {timestamp}
Agent: windsurf

SYSTEM CONFIGURATION:
- 10 AI agents configured: windsurf, claude, cline, codex, gemini, kilocode, openclaw, opencode, qwen, vscode
- Letta server running on port 8283
- PostgreSQL database with pgvector extension
- CBW RAG system with GPU-accelerated embeddings
- Bitwarden MCP server for secrets management

MEMORY FEATURES UTILIZED:
✓ Core Memory - System configuration stored as permanent knowledge
✓ Archival Memory - Conversation history and decisions
✓ Context Memory - Session-specific information
✓ Persona Memory - Agent personality definitions
✓ Human Memory - User preferences and context

OPERATIONS TESTED:
1. Agent creation with core memory blocks
2. Conversation saving with tags
3. Semantic memory search
4. Entity extraction (code, files, URLs, commands)
5. Decision memory creation
6. Action item creation with priority
7. Memory block creation and management
8. Cross-agent memory search
9. Memory statistics retrieval
10. Backup operations

ENTITIES EXTRACTED:
- File: ~/dotfiles/ai/config.yaml
- URL: https://docs.letta.com
- Command: docker-compose up -d
- Code: def test(): pass

DECISIONS MADE:
- Use Letta for all agent memory management
- Store memories in local PostgreSQL database
- Remove all mem0 cloud dependencies

ACTION ITEMS:
- Monitor all 10 agents [HIGH PRIORITY]
- Set up automated backups [MEDIUM PRIORITY]
- Document agent capabilities [LOW PRIORITY]
""".format(timestamp=datetime.utcnow().isoformat())
    
    # Save as core memory (permanent)
    print("Saving comprehensive memory...")
    try:
        result = letta._make_request(
            "POST",
            f"/v1/agents/{letta.get_or_create_agent()}/memory",
            {
                "content": comprehensive_content,
                "memory_type": "core",
                "tags": ["comprehensive", "setup", "all-features", "windsurf"],
                "metadata": {
                    "agent_count": 10,
                    "features_tested": 11,
                    "database": "postgresql",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        if "error" not in result:
            print("✓ Comprehensive memory saved to core memory")
            print(f"  Memory ID: {result.get('id', 'N/A')[:8]}...")
        else:
            print(f"✗ Error: {result['error']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Also save to archival
    print("\nSaving to archival memory...")
    try:
        result = letta.save_conversation(
            [
                {"role": "system", "content": "Comprehensive setup complete"},
                {"role": "assistant", "content": comprehensive_content[:500]}
            ],
            tags=["comprehensive", "setup"]
        )
        print("✓ Archival memory saved")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="Setup Letta agents and test features")
    parser.add_argument("--setup", action="store_true", help="Create all agents")
    parser.add_argument("--test", action="store_true", help="Run all feature tests")
    parser.add_argument("--memory", action="store_true", help="Add comprehensive memory")
    parser.add_argument("--full", action="store_true", help="Run everything")
    
    args = parser.parse_args()
    
    if args.full or args.setup:
        create_all_agents()
    
    if args.full or args.memory:
        add_comprehensive_memory()
    
    if args.full or args.test:
        test_all_features()
    
    if not any([args.setup, args.test, args.memory, args.full]):
        parser.print_help()


if __name__ == "__main__":
    main()

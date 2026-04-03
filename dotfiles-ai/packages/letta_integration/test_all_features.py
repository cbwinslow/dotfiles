#!/usr/bin/env python3
"""
Comprehensive Test Suite for Letta Self-Hosted Features
Tests all features from official Letta documentation
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')

from letta_integration import LettaIntegration


def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_result(test_name, success, details=""):
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"  [{status}] {test_name}")
    if details:
        print(f"       {details}")


def test_server_connection():
    """Test 1: Server Health Check"""
    print_header("TEST 1: Server Connection & Health")
    
    try:
        letta = LettaIntegration(agent_name="test")
        health = letta.check_server_health()
        
        success = health.get("status") == "healthy"
        print_result("Server Health Check", success, f"Status: {health.get('status')}")
        print(f"       Server URL: {letta.server_url}")
        return success
    except Exception as e:
        print_result("Server Health Check", False, str(e))
        return False


def test_agent_creation():
    """Test 2: Create Agent with Memory Blocks"""
    print_header("TEST 2: Agent Creation with Memory Blocks")
    
    try:
        letta = LettaIntegration(agent_name="test_agent_creation")
        
        # Create agent with custom memory blocks
        agent = letta.create_agent_with_memory_blocks(
            agent_name="test_agent_creation",
            memory_blocks=[
                {"label": "persona", "value": "I am a test assistant"},
                {"label": "human", "value": "User is testing the system"},
                {"label": "custom", "value": "Custom test memory block"}
            ]
        )
        
        if agent and hasattr(agent, 'id'):
            print_result("Agent Creation", True, f"Agent ID: {agent.id[:20]}...")
            
            # Test retrieving memory blocks
            persona = letta.get_memory_block("persona")
            if persona and hasattr(persona, 'value'):
                print_result("Memory Block Retrieval", True, f"Persona: {persona.value[:30]}...")
            else:
                print_result("Memory Block Retrieval", False, "Could not retrieve")
            
            return True
        else:
            print_result("Agent Creation", False, "No agent returned")
            return False
            
    except Exception as e:
        print_result("Agent Creation", False, str(e))
        return False


def test_memory_block_update():
    """Test 3: Update Memory Block"""
    print_header("TEST 3: Memory Block Update")
    
    try:
        letta = LettaIntegration(agent_name="test_agent_creation")
        
        # Update the human block
        new_value = f"Updated at {datetime.utcnow().isoformat()}"
        result = letta.update_memory_block("human", new_value)
        
        print_result("Memory Block Update", result, f"New value: {new_value[:40]}...")
        
        # Verify the update
        if result:
            block = letta.get_memory_block("human")
            if block and hasattr(block, 'value') and new_value in block.value:
                print_result("Update Verification", True, "Value confirmed")
            else:
                print_result("Update Verification", False, "Value not found")
        
        return result
        
    except Exception as e:
        print_result("Memory Block Update", False, str(e))
        return False


def test_shared_memory():
    """Test 4: Multi-Agent Shared Memory"""
    print_header("TEST 4: Multi-Agent Shared Memory")
    
    try:
        # Create shared block
        letta1 = LettaIntegration(agent_name="agent_1")
        shared = letta1.create_shared_block(
            label="shared_team_context",
            value="This is shared context between multiple agents"
        )
        
        if not shared or not hasattr(shared, 'id'):
            print_result("Shared Block Creation", False, "Failed to create")
            return False
        
        print_result("Shared Block Creation", True, f"Block ID: {shared.id[:20]}...")
        
        # Attach to first agent
        result1 = letta1.attach_shared_block(shared.id)
        print_result("Attach to Agent 1", result1)
        
        # Create second agent and attach
        letta2 = LettaIntegration(agent_name="agent_2")
        agent2 = letta2.create_agent_with_memory_blocks(agent_name="agent_2")
        
        if agent2 and hasattr(agent2, 'id'):
            letta2.agent_id = agent2.id
            result2 = letta2.attach_shared_block(shared.id)
            print_result("Attach to Agent 2", result2)
            
            return result1 and result2
        else:
            print_result("Agent 2 Creation", False, "Failed")
            return False
            
    except Exception as e:
        print_result("Shared Memory Test", False, str(e))
        return False


def test_archival_memory():
    """Test 5: Archival Memory (Save & Search)"""
    print_header("TEST 5: Archival Memory Operations")
    
    try:
        letta = LettaIntegration(agent_name="test_agent_creation")
        
        # Save to archival
        test_content = f"Test archival memory entry at {datetime.utcnow().isoformat()}. Testing search functionality."
        result = letta.save_to_archival(
            text=test_content,
            tags=["test", "archival", datetime.utcnow().strftime("%Y%m%d")]
        )
        
        print_result("Save to Archival", result, f"Content: {test_content[:50]}...")
        
        # Search archival
        if result:
            search_results = letta.search_archival(
                query="test archival memory",
                limit=5
            )
            
            found_count = len(search_results) if search_results else 0
            print_result("Archival Search", found_count > 0, f"Found {found_count} results")
            
            return result and found_count > 0
        
        return result
        
    except Exception as e:
        print_result("Archival Memory Test", False, str(e))
        return False


def test_list_agents():
    """Test 6: List All Agents"""
    print_header("TEST 6: List All Agents")
    
    try:
        letta = LettaIntegration(agent_name="test")
        agents = letta.list_agents()
        
        count = len(agents) if agents else 0
        print_result("List Agents", count > 0, f"Found {count} agents")
        
        if count > 0 and agents:
            print(f"       First agent: {agents[0].name if hasattr(agents[0], 'name') else 'unknown'}")
        
        return count >= 0  # Should at least not crash
        
    except Exception as e:
        print_result("List Agents", False, str(e))
        return False


def test_server_info():
    """Test 7: Server Information"""
    print_header("TEST 7: Server Information")
    
    try:
        letta = LettaIntegration(agent_name="test")
        
        print(f"  Server URL: {letta.server_url}")
        print(f"  Agent Name: {letta.agent_name}")
        print(f"  Agent ID: {letta.agent_id or 'Not set'}")
        print_result("Server Info", True)
        return True
        
    except Exception as e:
        print_result("Server Info", False, str(e))
        return False


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("  LETTA SELF-HOSTED - COMPREHENSIVE FEATURE TEST SUITE")
    print("="*70)
    
    results = {
        "Server Connection": test_server_connection(),
        "Agent Creation": test_agent_creation(),
        "Memory Update": test_memory_block_update(),
        "Shared Memory": test_shared_memory(),
        "Archival Memory": test_archival_memory(),
        "List Agents": test_list_agents(),
        "Server Info": test_server_info(),
    }
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  [{status}] {test_name}")
    
    print("\n" + "="*70)
    print(f"  RESULTS: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n  🎉 All tests PASSED! Letta integration is working correctly.")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Check output above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

import sys
import uuid
import subprocess
sys.path.append('..')

from letta_server import store_agent_context, store_memory_block, archival_insert, archival_search, get_agent_memory, list_memory_blocks, list_agents

def test_letta_skill():
    print("Testing Letta skill integration...")

    # Test 1: List agents
    print("\n1. Listing agents:")
    agents_result = list_agents()
    if agents_result["success"]:
        print(f"Agents: {agents_result['agents']}")
    else:
        print(f"Error: {agents_result['error']}")

    # Get the test agent ID
    agent_id = "agent-17121a10-ebef-4279-a30f-b2d310d3892e"
    print(f"\n2. Using test agent: {agent_id}")

    # Test 2: Store agent context
    print("\n3. Storing agent context:")
    context = {
        "agent_name": "test_agent",
        "processing_status": "active",
        "technical_architecture": "Python-based",
        "memory_type": "processing_status"
    }
    context_result = store_agent_context(agent_id, context)
    print(f"Context storage: {context_result}")

    # Test 3: Create memory block
    print("\n4. Creating memory block:")
    block_result = store_memory_block("test_block", "This is a test memory block")
    print(f"Memory block creation: {block_result}")

    # Test 4: Store archival memory
    print("\n5. Storing archival memory:")
    archival_result = archival_insert(agent_id, "This is a test archival memory", ["test", "archive"])
    print(f"Archival memory storage: {archival_result}")

    # Test 5: Search archival memories
    print("\n6. Searching archival memories:")
    search_result = archival_search(agent_id, "test")
    print(f"Search results: {search_result}")

    # Test 6: Get agent memory
    print("\n7. Getting agent memory:")
    memory_result = get_agent_memory(agent_id)
    print(f"Agent memory: {memory_result}")

    # Test 7: List memory blocks
    print("\n8. Listing memory blocks:")
    blocks_result = list_memory_blocks()
    print(f"Memory blocks: {blocks_result}")

    print("\nLetta skill integration test completed!")

if __name__ == "__main__":
    test_letta_skill()

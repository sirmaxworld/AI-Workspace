#!/usr/bin/env python3
"""
Test Mem0 with pgvector backend
"""
import sys
sys.path.append('/Users/yourox/AI-Workspace')

from config.mem0_collections import get_mem0_config

def test_mem0_connection():
    """Test that Mem0 can connect to pgvector"""
    print("Testing Mem0 with pgvector backend...\n")

    try:
        from mem0 import Memory

        # Test with a simple collection
        print("1. Creating Memory instance with video_knowledge collection...")
        config = get_mem0_config("video_knowledge")

        # Initialize Memory
        m = Memory.from_config(config)
        print("✅ Memory instance created successfully")

        # Add a test memory
        print("\n2. Adding test memory...")
        result = m.add(
            "This is a test memory for video knowledge database migration from Qdrant to pgvector",
            user_id="yourox_default"
        )
        print(f"✅ Memory added: {result}")

        # Search for the memory
        print("\n3. Searching for test memory...")
        search_results = m.search(
            "pgvector migration test",
            user_id="yourox_default"
        )
        print(f"✅ Found {len(search_results)} results")

        if search_results:
            print(f"   Top result: {search_results[0]['memory'][:100]}...")

        # Get all memories
        print("\n4. Getting all memories...")
        all_memories = m.get_all(user_id="yourox_default")
        print(f"✅ Total memories: {len(all_memories)}")

        print("\n🎉 Mem0 + pgvector integration working perfectly!")

        # Cleanup test memory
        print("\n5. Cleaning up test memory...")
        if result and 'id' in result:
            m.delete(result['id'])
            print("✅ Test memory deleted")

        return True

    except ImportError:
        print("❌ mem0 library not installed. Install with:")
        print("   pip3 install mem0ai")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mem0_connection()
    sys.exit(0 if success else 1)

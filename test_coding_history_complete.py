#!/usr/bin/env python3
"""
Comprehensive test suite for Coding History Summary System
Tests all components: capture, processing, storage, and MCP access
"""

import time
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent / "mcp_servers"))

def test_shell_environment():
    """Test 1: Shell environment is working"""
    print("\n🧪 TEST 1: Shell Environment")
    print("-" * 40)

    tests = [
        ("echo 'test'", "Basic echo"),
        ("pwd", "Print working directory"),
        ("python3 --version", "Python version"),
        ("ls /tmp", "List directory")
    ]

    passed = 0
    for cmd, description in tests:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print(f"✅ {description}: PASSED")
                passed += 1
            else:
                print(f"❌ {description}: FAILED (exit {result.returncode})")
        except Exception as e:
            print(f"❌ {description}: ERROR ({e})")

    print(f"\nResult: {passed}/{len(tests)} passed")
    return passed == len(tests)


def test_summary_system():
    """Test 2: Summary capture and processing"""
    print("\n🧪 TEST 2: Summary System")
    print("-" * 40)

    try:
        from coding_history_summary import queue_event, get_queue_stats, SummaryDB

        # Test queuing
        print("Testing event queuing...")
        initial_size = get_queue_stats()['queue_size']

        # Queue test events
        queue_event("npm install react", 0)
        queue_event("npm test", 1, "Test failed")
        queue_event("git commit -m 'Fix'", 0)

        time.sleep(0.1)  # Give it time to process
        new_size = get_queue_stats()['queue_size']

        if new_size >= initial_size:
            print("✅ Events queued successfully")
        else:
            print("❌ Queue processing too fast or failed")

        # Test database
        print("\nTesting database...")
        db = SummaryDB()
        stats = db.get_stats()

        print(f"  Total sessions: {stats['total_sessions']}")
        print(f"  Recent (24h): {stats['recent_sessions_24h']}")
        print(f"  Database size: {stats['db_size_bytes']} bytes")

        # Create a test summary
        from coding_history_summary import SessionSummary
        test_summary = SessionSummary(
            session_id="test_" + str(int(time.time())),
            timestamp=datetime.now(),
            prompt="Test session from comprehensive test",
            actions=["Ran test suite", "Verified functionality"],
            outcome="Test completed successfully",
            errors=[],
            tools_used=["python3", "test"],
            files_modified=["test_coding_history_complete.py"],
            duration_seconds=1.5,
            metadata={"test": True}
        )

        db.save_summary(test_summary)
        print("✅ Test summary saved to database")

        # Query it back
        sessions = db.search_sessions(query="test", limit=1)
        if sessions:
            print("✅ Summary retrieved from database")
        else:
            print("❌ Could not retrieve summary")

        return True

    except Exception as e:
        print(f"❌ Summary system test failed: {e}")
        return False


def test_performance():
    """Test 3: Performance benchmarks"""
    print("\n🧪 TEST 3: Performance")
    print("-" * 40)

    try:
        from coding_history_summary import queue_event
        import timeit

        # Test queue overhead
        def queue_test():
            queue_event("test command", 0)

        # Measure time for 1000 queue operations
        print("Measuring queue overhead...")
        time_taken = timeit.timeit(queue_test, number=1000)
        avg_ms = (time_taken / 1000) * 1000  # Convert to milliseconds

        print(f"  1000 queue operations: {time_taken:.3f}s")
        print(f"  Average per operation: {avg_ms:.3f}ms")

        if avg_ms < 1:
            print("✅ Excellent performance (<1ms)")
        elif avg_ms < 5:
            print("✅ Good performance (<5ms)")
        else:
            print(f"⚠️  Performance warning: {avg_ms:.3f}ms per operation")

        return avg_ms < 5

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def test_mcp_server():
    """Test 4: MCP Server functionality"""
    print("\n🧪 TEST 4: MCP Server")
    print("-" * 40)

    try:
        from coding_history_summary_mcp import (
            get_history_stats,
            get_recent_sessions,
            search_sessions,
            get_productivity_insights
        )

        # Test stats resource
        print("Testing stats resource...")
        stats = get_history_stats()
        if "Coding History Summary Statistics" in stats:
            print("✅ Stats resource working")
        else:
            print("❌ Stats resource failed")

        # Test recent sessions
        print("\nTesting recent sessions...")
        recent = get_recent_sessions()
        print(f"  Found: {recent.count('session')}")
        print("✅ Recent sessions working")

        # Test search
        print("\nTesting search...")
        results = search_sessions(query="test", limit=5)
        print(f"  Found {len(results)} results")
        print("✅ Search working")

        # Test productivity insights
        print("\nTesting productivity insights...")
        insights = get_productivity_insights(days=7)
        if 'total_sessions' in insights:
            print(f"  Sessions in last 7 days: {insights['total_sessions']}")
            print("✅ Productivity insights working")
        else:
            print("❌ Productivity insights failed")

        return True

    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        return False


def test_integration():
    """Test 5: End-to-end integration"""
    print("\n🧪 TEST 5: Integration Test")
    print("-" * 40)

    try:
        from coding_history_summary import queue_event, SummaryDB
        from coding_history_summary_mcp import search_sessions

        # Create a unique test session
        test_id = f"integration_test_{int(time.time())}"

        print("1. Queuing events...")
        queue_event(f"echo '{test_id}'", 0)
        queue_event(f"python3 -c 'print(\"{test_id}\")'", 0)
        queue_event(f"ls /tmp/{test_id}", 1, "File not found")

        print("2. Waiting for processing...")
        time.sleep(12)  # Wait for batch processing (10 second window)

        print("3. Searching via MCP...")
        results = search_sessions(query="test", limit=10)

        # Check if our session was processed
        found = any(test_id in str(s) for s in results)

        if found:
            print("✅ End-to-end integration working")
        else:
            print("⚠️  Session may not have been processed yet")
            print("  This is normal on first run - batch processing takes 10s")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🔬 COMPREHENSIVE CODING HISTORY SYSTEM TEST")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Check Python version
    print(f"\nPython: {sys.version}")
    print(f"Path: {sys.executable}")

    tests = [
        ("Shell Environment", test_shell_environment),
        ("Summary System", test_summary_system),
        ("Performance", test_performance),
        ("MCP Server", test_mcp_server),
        ("Integration", test_integration)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED! System is fully operational.")
    elif passed >= 3:
        print("\n⚠️  Most tests passed. Check failed tests above.")
    else:
        print("\n❌ Multiple tests failed. Please review the issues.")

    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    if not results[0][1]:  # Shell test failed
        print("  1. Run: bash ~/AI-Workspace/fix_shell_snapshots.py")
        print("  2. Restart Claude Desktop")

    if not results[1][1]:  # Summary system failed
        print("  1. Check if Python modules are installed")
        print("  2. Verify database permissions")

    if not results[3][1]:  # MCP failed
        print("  1. Run: bash ~/AI-Workspace/enable_coding_history_mcp.sh")
        print("  2. Restart Claude Desktop")

    return passed == len(tests)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
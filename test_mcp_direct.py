#!/usr/bin/env python3
"""
Direct test of the coding history MCP server
Tests if it can respond to MCP protocol messages
"""

import json
import subprocess
import sys

def test_mcp_server():
    """Test the MCP server with a basic protocol exchange"""

    # Start the server
    cmd = ["/usr/local/bin/python3.11", "/Users/yourox/AI-Workspace/mcp_servers/coding_history_summary_mcp.py"]

    print("Starting MCP server...")
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Send initialize request
    init_request = {
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "jsonrpc": "2.0",
        "id": 1
    }

    print("\nSending initialize request...")
    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()

    # Read response
    response_line = process.stdout.readline()
    if response_line:
        response = json.loads(response_line)
        print("\n✅ Server responded successfully!")
        print(f"Server name: {response['result']['serverInfo']['name']}")
        print(f"Server version: {response['result']['serverInfo']['version']}")

        # Send initialized notification (required by protocol)
        initialized_notification = {
            "method": "notifications/initialized",
            "jsonrpc": "2.0"
        }
        print("\nSending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()

        # Send tools/list request
        tools_request = {
            "method": "tools/list",
            "params": {},
            "jsonrpc": "2.0",
            "id": 2
        }

        print("\nSending tools/list request...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()

        # Read tools response
        tools_line = process.stdout.readline()
        if tools_line:
            tools_response = json.loads(tools_line)
            tools = tools_response.get('result', {}).get('tools', [])
            print(f"\n✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}")

        # Send resources/list request
        resources_request = {
            "method": "resources/list",
            "params": {},
            "jsonrpc": "2.0",
            "id": 3
        }

        print("\nSending resources/list request...")
        process.stdin.write(json.dumps(resources_request) + "\n")
        process.stdin.flush()

        # Read resources response
        resources_line = process.stdout.readline()
        if resources_line:
            resources_response = json.loads(resources_line)
            resources = resources_response.get('result', {}).get('resources', [])
            print(f"\n✅ Found {len(resources)} resources:")
            for resource in resources:
                print(f"  - {resource['name']}: {resource['uri']}")
    else:
        print("❌ No response from server")
        # Check stderr
        stderr = process.stderr.read()
        if stderr:
            print(f"\nServer error output:\n{stderr}")

    # Terminate the process
    process.terminate()
    process.wait(timeout=2)

    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_mcp_server()
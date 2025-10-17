#!/usr/bin/env python3
import urllib.request
import urllib.error
import sys

def check_server(port=8000):
    url = f"http://localhost:{port}"
    try:
        response = urllib.request.urlopen(url, timeout=5)
        print(f"✅ Server is running on port {port}")
        print(f"Status Code: {response.code}")
        print(f"Server: {response.headers.get('Server', 'Unknown')}")

        # Try to read some content
        content = response.read(100).decode('utf-8', errors='ignore')
        if 'TubeDB' in content or 'Next' in content or 'React' in content:
            print("✅ Looks like TubeDB/Next.js is responding!")

        return True
    except urllib.error.URLError as e:
        print(f"❌ Server not accessible on port {port}")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print(f"Checking server on port 8000...")
    print("-" * 40)

    if check_server(8000):
        print("\n🎯 SUCCESS! Server is running on http://localhost:8000")
    else:
        print("\n💡 Trying other common ports...")
        for port in [7000, 4000, 3000, 3001]:
            print(f"\nChecking port {port}...")
            if check_server(port):
                print(f"\n🎯 Found server on port {port}!")
                break
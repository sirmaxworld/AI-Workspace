#!/usr/bin/env python3
import requests
import socket

def check_server(port, name):
    """Check if a server is running on the specified port"""
    print(f"\nChecking {name} on port {port}...")

    # Check if port is open
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('localhost', port))
    sock.close()

    if result == 0:
        print(f"✅ Port {port} is open")

        # Try HTTP request
        try:
            response = requests.get(f'http://localhost:{port}', timeout=3)
            print(f"✅ Server responding with status: {response.status_code}")

            # Check response headers
            if 'x-powered-by' in response.headers:
                print(f"   Powered by: {response.headers['x-powered-by']}")

            return True
        except Exception as e:
            print(f"⚠️  Port open but HTTP request failed: {e}")
            return False
    else:
        print(f"❌ Port {port} is not accessible")
        return False

# Check bi-hub-frontend
if check_server(5173, "bi-hub-frontend"):
    print("\n✅ bi-hub-frontend is running successfully!")
else:
    print("\n❌ bi-hub-frontend is not accessible")

# Check other common ports
for port in [3000, 4000, 7000]:
    check_server(port, f"Service on port {port}")

print("\n" + "="*50)
print("Server check complete!")
#!/usr/bin/env python3
"""
Proxy configuration for YouTube video extraction
Copy this file to proxy-config.py and add your credentials
"""

# Paid proxy service configuration
# Recommended providers for YouTube extraction:
# - SmartProxy: https://smartproxy.com/ (residential proxies)
# - Bright Data: https://brightdata.com/ (formerly Luminati)
# - Oxylabs: https://oxylabs.io/ (premium residential)
# - IPRoyal: https://iproyal.com/ (affordable residential)

# Option 1: Simple HTTP/HTTPS proxy with authentication
PROXY_URL = "http://username:password@proxy.provider.com:port"

# Option 2: SOCKS5 proxy (better for video streaming)
# PROXY_URL = "socks5://username:password@proxy.provider.com:port"

# Option 3: Rotating residential proxies (recommended for YouTube)
# PROXY_URL = "http://username-country-us:password@gate.smartproxy.com:7000"

# Example configurations:

# SmartProxy residential (rotating)
# PROXY_URL = "http://user-username:password@gate.smartproxy.com:7000"

# Bright Data residential
# PROXY_URL = "http://lum-customer-CUSTOMER-zone-ZONE:PASSWORD@zproxy.lum-superproxy.io:22225"

# Oxylabs residential
# PROXY_URL = "http://customer-USERNAME:PASSWORD@pr.oxylabs.io:7777"

# IPRoyal residential (affordable option)
# PROXY_URL = "http://USERNAME:PASSWORD@geo.iproyal.com:12321"

# Test mode: Set to True to test proxy before extraction
TEST_PROXY = True

# Timeout for proxy connections (seconds)
PROXY_TIMEOUT = 30

# Number of retries per proxy
PROXY_RETRIES = 3

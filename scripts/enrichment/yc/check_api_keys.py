#!/usr/bin/env python3
"""
Check which API keys are configured and ready to use
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv('/Users/yourox/AI-Workspace/.env')

print("\n" + "="*70)
print("🔑 API KEY STATUS CHECK")
print("="*70 + "\n")

# Check OpenAI
openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    print("✅ OpenAI API Key: CONFIGURED")
    print(f"   Key prefix: {openai_key[:10]}...")
    print("   Used for: Phase 8 (AI Insights) - $5 total cost")
else:
    print("❌ OpenAI API Key: MISSING")
    print("   Add to .env: OPENAI_API_KEY=sk-...")

print()

# Check Google Maps
google_key = os.getenv('GOOGLE_MAPS_API_KEY')
if google_key:
    print("✅ Google Maps API Key: CONFIGURED")
    print(f"   Key prefix: {google_key[:15]}...")
    print("   Used for: Phase 2 (Geographic Data)")
    print("   Benefits: Ratings, phone, timezone, business hours")
    print("   Cost: FREE (5,490 < 28,000 free tier)")
else:
    print("⚠️  Google Maps API Key: NOT SET (using free fallback)")
    print("   Fallback: Nominatim (OpenStreetMap)")
    print("   Fallback data: Basic lat/lng only")
    print("   To enable: GOOGLE_MAPS_API_KEY=AIza...")
    print("   Setup: https://console.cloud.google.com/google/maps-apis")

print()

# Check GitHub
github_token = os.getenv('GITHUB_TOKEN')
if github_token:
    print("✅ GitHub Token: CONFIGURED")
    print(f"   Token prefix: {github_token[:10]}...")
    print("   Used for: Phase 3 (GitHub/Technical Data)")
    print("   Rate limit: 5,000 requests/hour (completes in ~1 hour)")
    print("   Cost: FREE")
else:
    print("⚠️  GitHub Token: NOT SET (using unauthenticated)")
    print("   Rate limit: 60 requests/hour (will take days!)")
    print("   To enable: GITHUB_TOKEN=ghp_...")
    print("   Setup: https://github.com/settings/tokens")
    print("   Required scopes: public_repo, read:org")

print()

# Summary
print("="*70)
print("📊 SUMMARY")
print("="*70)

configured = sum([bool(openai_key), bool(google_key), bool(github_token)])
total = 3

print(f"\n{configured}/{total} API keys configured\n")

if configured == 3:
    print("✅ ALL API keys configured! Ready for full enrichment.")
elif configured == 1:
    print("⚠️  Minimum configuration (OpenAI only)")
    print("   Recommended: Add Google Maps + GitHub for best results")
else:
    print("⚠️  Partial configuration")
    print("   Some enrichers will use fallback methods")

print("\n" + "="*70)
print("📖 Next Steps:")
print("="*70)
print("\n1. Add missing keys to: /Users/yourox/AI-Workspace/.env")
print("2. Read setup guide: /Users/yourox/AI-Workspace/scripts/enrichment/yc/SETUP.md")
print("3. Test enrichers: python3 enrichment_coordinator.py test-all")
print("4. Run enrichment: python3 enrichment_coordinator.py run-all\n")

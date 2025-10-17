#!/usr/bin/env python3
"""Test if the Business Intelligence database is loading correctly"""

import sys
sys.path.insert(0, '/Users/yourox/AI-Workspace/mcp-servers/business-intelligence')

from server import BusinessIntelligenceDB

# Initialize database
print("Initializing BusinessIntelligenceDB...")
db = BusinessIntelligenceDB()

# Get stats
stats = db.get_stats()

print("\n" + "="*60)
print("BUSINESS INTELLIGENCE DATABASE STATS")
print("="*60)

for key, value in stats.items():
    if key != 'files_loaded':
        print(f"{key:30s}: {value}")

print("\n" + "="*60)
print("SAMPLE QUERIES")
print("="*60)

# Test product search
products = db.search("ai", "products", {})
print(f"\nProducts mentioning 'ai': {len(products)} results")
if products:
    print(f"  Example: {products[0].get('name', 'N/A')}")

# Test problem search
problems = db.search("market", "problems", {})
print(f"\nProblems mentioning 'market': {len(problems)} results")
if problems:
    print(f"  Example: {problems[0].get('problem', 'N/A')[:80]}...")

# Test trends
trends = db.search("", "trends", {})
print(f"\nTotal trends available: {len(trends)} results")
if trends:
    print(f"  Example: {trends[0].get('trend', 'N/A')[:80]}...")

print("\n" + "="*60)
print("DATABASE STATUS: OPERATIONAL" if stats['total_files'] > 0 else "DATABASE STATUS: NO DATA LOADED")
print("="*60)

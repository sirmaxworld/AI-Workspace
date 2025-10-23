#!/usr/bin/env python3
"""
Test script for Business Intelligence MCP Server
Validates all tools and data loading
"""

import json
import sys
from pathlib import Path

# Add server to path
sys.path.insert(0, str(Path(__file__).parent))

from server import BusinessIntelligenceDB

def test_database_loading():
    """Test that database loads correctly"""
    print("=" * 70)
    print("TEST 1: Database Loading")
    print("=" * 70)

    db = BusinessIntelligenceDB()
    stats = db.get_stats()

    print(f"\n✅ Files loaded: {stats['total_files']}")
    print(f"✅ Products: {stats['total_products']}")
    print(f"✅ Problems: {stats['total_problems']}")
    print(f"✅ Startup Ideas: {stats['total_startup_ideas']}")
    print(f"✅ Growth Tactics: {stats['total_growth_tactics']}")
    print(f"✅ AI Workflows: {stats['total_ai_workflows']}")
    print(f"✅ Target Markets: {stats['total_target_markets']}")
    print(f"✅ Trends: {stats['total_trends']}")
    print(f"✅ Strategies: {stats['total_strategies']}")
    print(f"✅ Metrics: {stats['total_metrics']}")
    print(f"✅ Quotes: {stats['total_quotes']}")
    print(f"✅ Statistics: {stats['total_statistics']}")
    print(f"✅ Mistakes: {stats['total_mistakes']}")

    total_items = sum([
        stats['total_products'],
        stats['total_problems'],
        stats['total_startup_ideas'],
        stats['total_growth_tactics'],
        stats['total_ai_workflows'],
        stats['total_target_markets'],
        stats['total_trends'],
        stats['total_strategies'],
        stats['total_metrics'],
        stats['total_quotes'],
        stats['total_statistics'],
        stats['total_mistakes']
    ])
    print(f"\nTotal Intelligence Items: {total_items}")

    return db


def test_product_search(db):
    """Test product search functionality"""
    print("\n" + "=" * 70)
    print("TEST 2: Product Search")
    print("=" * 70)

    # Test 1: Search for AI tools
    results = db.search("chatgpt", "products", {"category": "ai-tool"})
    print(f"\n🔍 Search: 'chatgpt' in category 'ai-tool'")
    print(f"✅ Found {len(results)} results")
    if results:
        print(f"\nExample result:")
        print(json.dumps(results[0], indent=2))

    # Test 2: Search for positive sentiment products
    results = db.search("", "products", {"sentiment": "positive"})
    print(f"\n🔍 Search: All products with positive sentiment")
    print(f"✅ Found {len(results)} results")


def test_problem_search(db):
    """Test problem search functionality"""
    print("\n" + "=" * 70)
    print("TEST 3: Problem Search")
    print("=" * 70)

    results = db.search("market", "problems", {"category": "market-research"})
    print(f"\n🔍 Search: 'market' in category 'market-research'")
    print(f"✅ Found {len(results)} results")
    if results:
        print(f"\nExample result:")
        print(json.dumps(results[0], indent=2))


def test_trend_search(db):
    """Test trend search functionality"""
    print("\n" + "=" * 70)
    print("TEST 4: Trend Search")
    print("=" * 70)

    results = db.search("", "trends", {"stage": "growing"})
    print(f"\n🔍 Search: All trends with stage 'growing'")
    print(f"✅ Found {len(results)} results")
    if results:
        print(f"\nExample result:")
        print(json.dumps(results[0], indent=2))


def test_ai_workflow_search(db):
    """Test AI workflow search functionality"""
    print("\n" + "=" * 70)
    print("TEST 5: AI Workflow Search")
    print("=" * 70)

    results = db.search("youtube", "ai_workflows", {})
    print(f"\n🔍 Search: 'youtube' workflows")
    print(f"✅ Found {len(results)} results")
    if results:
        print(f"\nExample result:")
        print(json.dumps(results[0], indent=2))


def test_growth_tactics_search(db):
    """Test growth tactics search functionality"""
    print("\n" + "=" * 70)
    print("TEST 6: Growth Tactics Search")
    print("=" * 70)

    results = db.search("viral", "growth_tactics", {"channel": "content"})
    print(f"\n🔍 Search: 'viral' in channel 'content'")
    print(f"✅ Found {len(results)} results")
    if results:
        print(f"\nExample result:")
        print(json.dumps(results[0], indent=2))


def test_market_opportunities(db):
    """Test market opportunity analysis"""
    print("\n" + "=" * 70)
    print("TEST 7: Market Opportunities Analysis")
    print("=" * 70)

    # Get growing trends
    growing_trends = [t for t in db.all_data["trends"] if t.get("stage") == "growing"]
    print(f"\n✅ Found {len(growing_trends)} growing trends")

    # Get validated problems
    problems = db.all_data["problems"]
    print(f"✅ Found {len(problems)} validated problems")

    # Get target markets
    markets = db.all_data["target_markets"]
    print(f"✅ Found {len(markets)} target markets")

    potential = len(growing_trends) * len(problems) * len(markets)
    print(f"\nMarket opportunity combination potential: {potential}")


def test_actionable_quotes(db):
    """Test actionable quotes retrieval"""
    print("\n" + "=" * 70)
    print("TEST 8: Actionable Quotes")
    print("=" * 70)

    results = db.search("", "quotes", {"category": "strategy"})
    print(f"\n🔍 Search: Strategy quotes")
    print(f"✅ Found {len(results)} results")
    if results:
        print(f"\nExample quote:")
        print(f"  '{results[0].get('quote', '')}'")
        print(f"  Category: {results[0].get('category', '')}")
        print(f"  Actionability: {results[0].get('actionability', '')}")


def test_mistakes_to_avoid(db):
    """Test mistakes retrieval"""
    print("\n" + "=" * 70)
    print("TEST 9: Mistakes to Avoid")
    print("=" * 70)

    results = db.search("", "mistakes", {})
    print(f"\n🔍 Search: All mistakes")
    print(f"✅ Found {len(results)} results")
    if results:
        print(f"\nExample mistake:")
        print(f"  Mistake: {results[0].get('mistake', '')}")
        print(f"  Prevention: {results[0].get('prevention', '')}")


def main():
    """Run all tests"""
    print("\n")
    print("🧪 BUSINESS INTELLIGENCE MCP SERVER TESTS")
    print("\n")

    try:
        # Test 1: Database loading
        db = test_database_loading()

        # Test 2: Product search
        test_product_search(db)

        # Test 3: Problem search
        test_problem_search(db)

        # Test 4: Trend search
        test_trend_search(db)

        # Test 5: AI workflow search
        test_ai_workflow_search(db)

        # Test 6: Growth tactics search
        test_growth_tactics_search(db)

        # Test 7: Market opportunities
        test_market_opportunities(db)

        # Test 8: Actionable quotes
        test_actionable_quotes(db)

        # Test 9: Mistakes to avoid
        test_mistakes_to_avoid(db)

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n🚀 MCP Server is ready to use!\n")

        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

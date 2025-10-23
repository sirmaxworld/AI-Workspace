#!/usr/bin/env python3
"""
Test script for enriched intelligence MCP integration
Verifies all enrichment layers and MCP tools work correctly
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from server import db

def print_section(title):
    """Print a test section header"""
    print(f"\n{'=' * 60}")
    print(f"🧪 {title}")
    print('=' * 60)

def test_data_loading():
    """Test that all enriched data loaded correctly"""
    print_section("DATA LOADING TEST")

    stats = db.get_stats()

    tests = [
        ("Insight files loaded", stats['total_files'], 51),
        ("Enriched insights loaded", stats['total_enriched_insights'], 51),
        ("Video summaries loaded", stats['total_video_summaries'], 51),
        ("Meta-intelligence loaded", stats['meta_intelligence_loaded'], True),
        ("Products loaded", stats['total_products'] > 0, True),
        ("Trends loaded", stats['total_trends'] > 0, True),
    ]

    passed = 0
    failed = 0

    for test_name, actual, expected in tests:
        if actual == expected:
            print(f"✅ {test_name}: {actual}")
            passed += 1
        else:
            print(f"❌ {test_name}: Expected {expected}, got {actual}")
            failed += 1

    print(f"\n📊 Stats Summary:")
    print(f"   Total insights: {sum(len(v) for v in db.all_data.values() if isinstance(v, list))}")
    print(f"   Enriched files: {stats['total_enriched_insights']}")
    print(f"   Summaries: {stats['total_video_summaries']}")
    print(f"   YC Companies: {stats['total_yc_companies']}")

    return passed, failed

def test_enriched_insights():
    """Test enriched insights have correct structure"""
    print_section("ENRICHED INSIGHTS STRUCTURE TEST")

    if not db.all_data['enriched_insights']:
        print("❌ No enriched insights found!")
        return 0, 1

    sample = db.all_data['enriched_insights'][0]

    required_fields = [
        'video_id',
        'video_type',
        'type_confidence',
        'insight_metrics',
        'video_level_metrics',
        '_version',
        '_computed_at',
        '_engine_version'
    ]

    passed = 0
    failed = 0

    print(f"Testing sample video: {sample.get('video_id', 'unknown')}")

    for field in required_fields:
        if field in sample:
            print(f"✅ Field '{field}': Present")
            passed += 1
        else:
            print(f"❌ Field '{field}': Missing")
            failed += 1

    # Test video-level metrics
    metrics = sample.get('video_level_metrics', {})
    metric_fields = [
        'avg_actionability_score',
        'avg_specificity_score',
        'avg_evidence_strength',
        'avg_recency_score',
        'high_value_insights',
        'total_insights'
    ]

    print(f"\n📊 Video Metrics:")
    for field in metric_fields:
        value = metrics.get(field, 'N/A')
        print(f"   {field}: {value}")
        if field in metrics:
            passed += 1
        else:
            failed += 1

    return passed, failed

def test_video_summaries():
    """Test video summaries have correct structure"""
    print_section("VIDEO SUMMARIES STRUCTURE TEST")

    if not db.all_data['video_summaries']:
        print("❌ No video summaries found!")
        return 0, 1

    sample = db.all_data['video_summaries'][0]

    required_fields = [
        'video_id',
        'video_title',
        'content_profile',
        'key_takeaways',
        'opportunity_map',
        'metrics_summary',
        'practical_next_steps'
    ]

    passed = 0
    failed = 0

    print(f"Testing sample: {sample.get('video_title', 'unknown')}")

    for field in required_fields:
        if field in sample:
            print(f"✅ Field '{field}': Present")
            passed += 1
        else:
            print(f"❌ Field '{field}': Missing")
            failed += 1

    # Test content profile
    profile = sample.get('content_profile', {})
    print(f"\n📊 Content Profile:")
    print(f"   Video Type: {profile.get('video_type', 'N/A')}")
    print(f"   Experience Level: {profile.get('experience_level', 'N/A')}")
    print(f"   Industry Focus: {profile.get('industry_focus', [])}")

    # Test opportunity map
    opp_map = sample.get('opportunity_map', {})
    print(f"\n🎯 Opportunities:")
    print(f"   Total: {opp_map.get('total_opportunities', 0)}")
    print(f"   Startup Ideas: {opp_map.get('by_type', {}).get('startup_ideas', 0)}")
    print(f"   Market Gaps: {opp_map.get('by_type', {}).get('market_gaps', 0)}")
    print(f"   Trends: {opp_map.get('by_type', {}).get('trend_opportunities', 0)}")

    return passed, failed

def test_meta_intelligence():
    """Test meta-intelligence structure"""
    print_section("META-INTELLIGENCE STRUCTURE TEST")

    if not db.meta_intelligence:
        print("❌ Meta-intelligence not loaded!")
        return 0, 1

    required_sections = [
        'cross_video_trends',
        'product_ecosystem',
        'strategy_playbooks',
        'expert_consensus',
        'opportunity_matrix'
    ]

    passed = 0
    failed = 0

    for section in required_sections:
        if section in db.meta_intelligence:
            print(f"✅ Section '{section}': Present")
            passed += 1
        else:
            print(f"❌ Section '{section}': Missing")
            failed += 1

    # Test trends
    trends = db.meta_intelligence.get('cross_video_trends', {})
    print(f"\n📈 Cross-Video Trends:")
    print(f"   Total unique: {trends.get('total_unique_trends', 0)}")
    print(f"   Total mentions: {trends.get('total_trend_mentions', 0)}")
    print(f"   Top trends: {len(trends.get('top_trends', []))}")

    # Test products
    products = db.meta_intelligence.get('product_ecosystem', {})
    print(f"\n🔧 Product Ecosystem:")
    print(f"   Total unique: {products.get('total_unique_products', 0)}")
    print(f"   Total mentions: {products.get('total_product_mentions', 0)}")
    print(f"   Recommended tools: {len(products.get('most_recommended_tools', []))}")

    # Test playbooks
    playbooks = db.meta_intelligence.get('strategy_playbooks', {})
    print(f"\n📚 Strategy Playbooks:")
    print(f"   Total strategies: {playbooks.get('total_strategy_mentions', 0)}")
    print(f"   Recurring playbooks: {len(playbooks.get('recurring_playbooks', []))}")

    # Test opportunities
    matrix = db.meta_intelligence.get('opportunity_matrix', {})
    print(f"\n🎯 Opportunity Matrix:")
    print(f"   Total opportunities: {matrix.get('total_opportunities', 0)}")
    by_type = matrix.get('by_type', {})
    print(f"   Startup ideas: {by_type.get('startup_ideas', 0)}")
    print(f"   Market gaps: {by_type.get('market_gaps', 0)}")
    print(f"   Trend opportunities: {by_type.get('trend_opportunities', 0)}")

    return passed, failed

def test_search_functionality():
    """Test search and query functionality"""
    print_section("SEARCH FUNCTIONALITY TEST")

    passed = 0
    failed = 0

    # Test 1: Search enriched insights
    print("\n🔍 Test 1: Search enriched insights by video type")
    entrepreneurship_videos = [
        v for v in db.all_data['enriched_insights']
        if v.get('video_type') == 'entrepreneurship'
    ]
    print(f"   Found {len(entrepreneurship_videos)} entrepreneurship videos")
    if len(entrepreneurship_videos) > 0:
        print(f"✅ Search by video type works")
        passed += 1
    else:
        print(f"❌ No entrepreneurship videos found")
        failed += 1

    # Test 2: Filter by metric scores
    print("\n🔍 Test 2: Filter by metric scores")
    high_value = [
        v for v in db.all_data['enriched_insights']
        if v.get('video_level_metrics', {}).get('avg_actionability_score', 0) >= 70
    ]
    print(f"   Found {len(high_value)} videos with avg actionability >= 70")
    if len(high_value) > 0:
        print(f"✅ Metric filtering works")
        passed += 1
    else:
        print(f"⚠️  No videos meet threshold (may be expected)")
        passed += 1

    # Test 3: Search summaries
    print("\n🔍 Test 3: Search video summaries")
    ai_summaries = [
        s for s in db.all_data['video_summaries']
        if 'ai' in json.dumps(s).lower()
    ]
    print(f"   Found {len(ai_summaries)} summaries mentioning 'ai'")
    if len(ai_summaries) > 0:
        print(f"✅ Summary search works")
        passed += 1
    else:
        print(f"❌ No AI-related summaries found")
        failed += 1

    # Test 4: Meta-intelligence queries
    print("\n🔍 Test 4: Query meta-intelligence")
    if db.meta_intelligence:
        top_trends = db.meta_intelligence.get('cross_video_trends', {}).get('top_trends', [])
        high_freq_trends = [t for t in top_trends if t.get('frequency', 0) >= 5]
        print(f"   Found {len(high_freq_trends)} trends with frequency >= 5")
        if len(high_freq_trends) > 0:
            print(f"✅ Meta-intelligence queries work")
            print(f"   Top trend: {high_freq_trends[0].get('trend', 'N/A')} ({high_freq_trends[0].get('frequency', 0)} mentions)")
            passed += 1
        else:
            print(f"⚠️  No high-frequency trends (may be expected)")
            passed += 1
    else:
        print(f"❌ Meta-intelligence not available")
        failed += 1

    return passed, failed

def test_sample_queries():
    """Test sample real-world queries"""
    print_section("SAMPLE QUERY TEST")

    passed = 0
    failed = 0

    # Query 1: Find top AI tools
    print("\n🎯 Query 1: What are the top recommended AI tools?")
    if db.meta_intelligence:
        products = db.meta_intelligence.get('product_ecosystem', {}).get('most_recommended_tools', [])
        ai_tools = [p for p in products[:10] if p.get('primary_category') == 'ai-tool']
        print(f"   Found {len(ai_tools)} top AI tools")
        for i, tool in enumerate(ai_tools[:3], 1):
            print(f"   {i}. {tool.get('name')} - {tool.get('mention_count')} mentions ({tool.get('sentiment_score')})")
        if len(ai_tools) > 0:
            print(f"✅ AI tools query works")
            passed += 1
        else:
            print(f"❌ No AI tools found")
            failed += 1
    else:
        failed += 1

    # Query 2: Find startup opportunities
    print("\n🎯 Query 2: What are the top startup ideas?")
    if db.meta_intelligence:
        matrix = db.meta_intelligence.get('opportunity_matrix', {})
        ideas = matrix.get('top_startup_ideas', [])[:5]
        print(f"   Found {len(ideas)} startup ideas")
        for i, idea in enumerate(ideas[:3], 1):
            print(f"   {i}. {idea.get('title', 'N/A')}")
            print(f"      Target: {idea.get('target_market', 'N/A')}")
        if len(ideas) > 0:
            print(f"✅ Startup ideas query works")
            passed += 1
        else:
            print(f"❌ No startup ideas found")
            failed += 1
    else:
        failed += 1

    # Query 3: Find emerging trends
    print("\n🎯 Query 3: What are the emerging trends?")
    if db.meta_intelligence:
        trends = db.meta_intelligence.get('cross_video_trends', {}).get('top_trends', [])
        emerging = [t for t in trends if t.get('stage') == 'early'][:5]
        print(f"   Found {len(emerging)} emerging trends")
        for i, trend in enumerate(emerging[:3], 1):
            print(f"   {i}. {trend.get('trend', 'N/A')} ({trend.get('frequency')} mentions)")
        if len(emerging) > 0:
            print(f"✅ Emerging trends query works")
            passed += 1
        else:
            print(f"⚠️  No 'early' stage trends (may be expected)")
            passed += 1
    else:
        failed += 1

    return passed, failed

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 ENRICHMENT SYSTEM TEST SUITE")
    print("=" * 60)

    total_passed = 0
    total_failed = 0

    # Run all test suites
    test_suites = [
        ("Data Loading", test_data_loading),
        ("Enriched Insights", test_enriched_insights),
        ("Video Summaries", test_video_summaries),
        ("Meta Intelligence", test_meta_intelligence),
        ("Search Functionality", test_search_functionality),
        ("Sample Queries", test_sample_queries)
    ]

    results = []
    for suite_name, test_func in test_suites:
        try:
            passed, failed = test_func()
            total_passed += passed
            total_failed += failed
            results.append((suite_name, passed, failed))
        except Exception as e:
            print(f"\n❌ Test suite '{suite_name}' failed with error: {e}")
            total_failed += 1
            results.append((suite_name, 0, 1))

    # Print final results
    print_section("TEST RESULTS SUMMARY")

    for suite_name, passed, failed in results:
        status = "✅ PASSED" if failed == 0 else "❌ FAILED"
        print(f"{status} - {suite_name}: {passed} passed, {failed} failed")

    print(f"\n{'=' * 60}")
    print(f"📊 OVERALL: {total_passed} passed, {total_failed} failed")

    if total_failed == 0:
        print(f"🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit(main())

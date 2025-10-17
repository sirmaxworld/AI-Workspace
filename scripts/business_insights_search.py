#!/usr/bin/env python3
"""
Business Insights Search Engine
Query structured business intelligence across all videos
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict


class BusinessInsightsSearch:
    """Search and filter business insights"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.insights_dir = self.workspace_dir / "data" / "business_insights"
        self.insights_cache = []
        self.load_all_insights()

    def load_all_insights(self):
        """Load all insights files into memory"""
        insight_files = list(self.insights_dir.glob("*_insights.json"))

        for file in insight_files:
            with open(file, 'r') as f:
                insights = json.load(f)
                self.insights_cache.append(insights)

        print(f"✅ Loaded {len(self.insights_cache)} insights files")

    def search_products(self, query: str = None, category: str = None,
                       sentiment: str = None) -> List[Dict]:
        """Search for products/tools"""
        results = []

        for insights in self.insights_cache:
            products = insights.get('products_tools', [])
            for product in products:
                if query and query.lower() not in product.get('name', '').lower() and \
                   query.lower() not in product.get('use_case', '').lower():
                    continue
                if category and product.get('category') != category:
                    continue
                if sentiment and product.get('sentiment') != sentiment:
                    continue

                result = product.copy()
                result['source_video'] = insights['meta']['title']
                result['video_id'] = insights['meta']['video_id']
                results.append(result)

        return results

    def search_problems(self, query: str = None, category: str = None) -> List[Dict]:
        """Search for problems and solutions"""
        results = []

        for insights in self.insights_cache:
            problems = insights.get('problems_solutions', [])
            for problem in problems:
                if query and query.lower() not in problem.get('problem', '').lower() and \
                   query.lower() not in problem.get('solution', '').lower():
                    continue
                if category and problem.get('category') != category:
                    continue

                result = problem.copy()
                result['source_video'] = insights['meta']['title']
                result['video_id'] = insights['meta']['video_id']
                results.append(result)

        return results

    def search_startup_ideas(self, query: str = None) -> List[Dict]:
        """Search for startup ideas"""
        results = []

        for insights in self.insights_cache:
            ideas = insights.get('startup_ideas', [])
            for idea in ideas:
                if query and query.lower() not in json.dumps(idea).lower():
                    continue

                result = idea.copy()
                result['source_video'] = insights['meta']['title']
                result['video_id'] = insights['meta']['video_id']
                results.append(result)

        return results

    def search_growth_tactics(self, channel: str = None) -> List[Dict]:
        """Search for growth tactics by channel"""
        results = []

        for insights in self.insights_cache:
            tactics = insights.get('growth_tactics', [])
            for tactic in tactics:
                if channel and tactic.get('channel') != channel:
                    continue

                result = tactic.copy()
                result['source_video'] = insights['meta']['title']
                result['video_id'] = insights['meta']['video_id']
                results.append(result)

        return results

    def search_ai_workflows(self, query: str = None) -> List[Dict]:
        """Search for AI workflows"""
        results = []

        for insights in self.insights_cache:
            workflows = insights.get('ai_workflows', [])
            for workflow in workflows:
                if query and query.lower() not in json.dumps(workflow).lower():
                    continue

                result = workflow.copy()
                result['source_video'] = insights['meta']['title']
                result['video_id'] = insights['meta']['video_id']
                results.append(result)

        return results

    def get_target_markets(self) -> List[Dict]:
        """Get all target markets identified"""
        markets = []

        for insights in self.insights_cache:
            market_data = insights.get('market_intelligence', {}).get('target_markets', [])
            for market in market_data:
                market['source_video'] = insights['meta']['title']
                market['video_id'] = insights['meta']['video_id']
                markets.append(market)

        return markets

    def get_metrics_benchmarks(self) -> List[Dict]:
        """Get all metrics and benchmarks"""
        metrics = []

        for insights in self.insights_cache:
            metric_data = insights.get('metrics_kpis', [])
            for metric in metric_data:
                metric['source_video'] = insights['meta']['title']
                metric['video_id'] = insights['meta']['video_id']
                metrics.append(metric)

        return metrics

    def get_trends(self, stage: str = None) -> List[Dict]:
        """Get emerging trends"""
        trends = []

        for insights in self.insights_cache:
            trend_data = insights.get('trends_signals', [])
            for trend in trend_data:
                if stage and trend.get('stage') != stage:
                    continue

                trend['source_video'] = insights['meta']['title']
                trend['video_id'] = insights['meta']['video_id']
                trends.append(trend)

        return trends

    def get_statistics(self) -> Dict:
        """Get summary statistics"""
        stats = {
            'total_videos': len(self.insights_cache),
            'total_products': 0,
            'total_problems': 0,
            'total_startup_ideas': 0,
            'total_growth_tactics': 0,
            'total_ai_workflows': 0,
            'total_markets': 0,
            'total_trends': 0
        }

        for insights in self.insights_cache:
            stats['total_products'] += len(insights.get('products_tools', []))
            stats['total_problems'] += len(insights.get('problems_solutions', []))
            stats['total_startup_ideas'] += len(insights.get('startup_ideas', []))
            stats['total_growth_tactics'] += len(insights.get('growth_tactics', []))
            stats['total_ai_workflows'] += len(insights.get('ai_workflows', []))
            stats['total_markets'] += len(insights.get('market_intelligence', {}).get('target_markets', []))
            stats['total_trends'] += len(insights.get('trends_signals', []))

        return stats

    def analyze_market_opportunities(self) -> Dict:
        """Analyze market opportunities across all videos"""
        opportunities = defaultdict(list)

        for insights in self.insights_cache:
            problems = insights.get('market_intelligence', {}).get('problems_validated', [])
            for problem in problems:
                market_gap = problem.get('market_gap', '')
                if market_gap:
                    opportunities[market_gap].append({
                        'problem': problem.get('problem'),
                        'severity': problem.get('severity'),
                        'video': insights['meta']['title']
                    })

        return dict(opportunities)


def main():
    import sys

    search = BusinessInsightsSearch()

    if len(sys.argv) < 2:
        print("\nBusiness Insights Search Engine")
        print("="*70)
        print("\nCommands:")
        print("  stats                        - Show database statistics")
        print("  products [query]             - Search products/tools")
        print("  problems [query]             - Search problems/solutions")
        print("  ideas [query]                - Search startup ideas")
        print("  growth [channel]             - Search growth tactics")
        print("  ai-workflows [query]         - Search AI workflows")
        print("  markets                      - Show target markets")
        print("  metrics                      - Show metrics/KPIs")
        print("  trends [stage]               - Show trends")
        print("  opportunities                - Analyze market opportunities")
        return

    command = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "stats":
        stats = search.get_statistics()
        print("\n📊 Business Intelligence Database Statistics")
        print("="*70)
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        print("="*70)

    elif command == "products":
        results = search.search_products(query)
        print(f"\n🛠️  Found {len(results)} products")
        print("="*70)
        for i, product in enumerate(results[:10], 1):
            print(f"\n{i}. {product['name']} ({product['category']})")
            print(f"   Use Case: {product['use_case']}")
            print(f"   Sentiment: {product['sentiment']}")
            if product.get('metrics'):
                print(f"   Metrics: {product['metrics']}")
            print(f"   Source: {product['source_video']}")

    elif command == "problems":
        results = search.search_problems(query)
        print(f"\n🎯 Found {len(results)} problems/solutions")
        print("="*70)
        for i, item in enumerate(results[:10], 1):
            print(f"\n{i}. {item['problem']}")
            print(f"   Solution: {item['solution']}")
            print(f"   Difficulty: {item.get('difficulty', 'N/A')}")
            if item.get('tools_needed'):
                print(f"   Tools: {', '.join(item['tools_needed'])}")
            print(f"   Source: {item['source_video']}")

    elif command == "ideas":
        results = search.search_startup_ideas(query)
        print(f"\n💡 Found {len(results)} startup ideas")
        print("="*70)
        for i, idea in enumerate(results[:10], 1):
            print(f"\n{i}. {idea['idea']}")
            print(f"   Target Market: {idea['target_market']}")
            print(f"   Problem Solved: {idea['problem_solved']}")
            print(f"   Business Model: {idea['business_model']}")
            print(f"   Source: {idea['source_video']}")

    elif command == "growth":
        results = search.search_growth_tactics(query)
        print(f"\n📈 Found {len(results)} growth tactics")
        print("="*70)
        for i, tactic in enumerate(results[:10], 1):
            print(f"\n{i}. {tactic['channel']}: {tactic['tactic']}")
            if tactic.get('cost_estimate'):
                print(f"   Cost: {tactic['cost_estimate']}")
            if tactic.get('results_expected'):
                print(f"   Results: {tactic['results_expected']}")
            print(f"   Source: {tactic['source_video']}")

    elif command == "ai-workflows":
        results = search.search_ai_workflows(query)
        print(f"\n🤖 Found {len(results)} AI workflows")
        print("="*70)
        for i, workflow in enumerate(results[:10], 1):
            print(f"\n{i}. {workflow['workflow_name']}")
            print(f"   Tools: {', '.join(workflow.get('tools_used', []))}")
            print(f"   Automation: {workflow.get('automation_level', 'N/A')}")
            print(f"   Source: {workflow['source_video']}")

    elif command == "markets":
        markets = search.get_target_markets()
        print(f"\n🎯 Found {len(markets)} target markets")
        print("="*70)
        for i, market in enumerate(markets[:15], 1):
            print(f"\n{i}. {market['market_description']}")
            print(f"   Pain Points: {', '.join(market.get('pain_points', []))}")
            print(f"   Source: {market['source_video']}")

    elif command == "metrics":
        metrics = search.get_metrics_benchmarks()
        print(f"\n📊 Found {len(metrics)} metrics/KPIs")
        print("="*70)
        for i, metric in enumerate(metrics[:15], 1):
            print(f"\n{i}. {metric['metric']}")
            print(f"   Benchmark: {metric.get('benchmark', 'N/A')}")
            if metric.get('optimization_tip'):
                print(f"   Tip: {metric['optimization_tip']}")
            print(f"   Source: {metric['source_video']}")

    elif command == "trends":
        trends = search.get_trends(query)
        print(f"\n🚀 Found {len(trends)} trends")
        print("="*70)
        for i, trend in enumerate(trends[:15], 1):
            print(f"\n{i}. {trend['trend']}")
            print(f"   Stage: {trend.get('stage', 'N/A')}")
            print(f"   Opportunity: {trend.get('opportunity', 'N/A')}")
            print(f"   Source: {trend['source_video']}")

    elif command == "opportunities":
        opps = search.analyze_market_opportunities()
        print(f"\n💰 Found {len(opps)} market opportunities")
        print("="*70)
        for gap, problems in list(opps.items())[:10]:
            print(f"\n• {gap}")
            for problem in problems[:3]:
                print(f"    - {problem['problem']} ({problem['severity']})")


if __name__ == "__main__":
    main()

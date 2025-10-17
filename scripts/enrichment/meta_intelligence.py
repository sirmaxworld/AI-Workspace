#!/usr/bin/env python3
"""
Meta-Intelligence Analyzer - Cross-video pattern analysis
Analyzes trends, consensus, and patterns across all videos
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetaIntelligenceEngine:
    """Analyze patterns across all videos"""

    VERSION = "1.0.0"

    def __init__(self, workspace_dir: Path = None):
        if workspace_dir is None:
            workspace_dir = Path("/Users/yourox/AI-Workspace")

        self.workspace_dir = workspace_dir
        self.insights_dir = workspace_dir / "data" / "business_insights"
        self.enriched_dir = workspace_dir / "data" / "enriched_insights"
        self.summaries_dir = workspace_dir / "data" / "video_summaries"
        self.meta_dir = workspace_dir / "data" / "meta_intelligence"
        self.meta_dir.mkdir(parents=True, exist_ok=True)

    def load_all_data(self) -> Dict[str, Dict]:
        """Load all insights, enriched data, and summaries"""

        all_data = {
            'insights': {},
            'enriched': {},
            'summaries': {}
        }

        # Load insights
        for file in self.insights_dir.glob("*_insights.json"):
            video_id = file.stem.replace("_insights", "")
            try:
                with open(file, 'r') as f:
                    all_data['insights'][video_id] = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading insight {video_id}: {e}")

        # Load enriched
        for file in self.enriched_dir.glob("*_enriched.json"):
            video_id = file.stem.replace("_enriched", "")
            try:
                with open(file, 'r') as f:
                    all_data['enriched'][video_id] = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading enriched {video_id}: {e}")

        # Load summaries
        for file in self.summaries_dir.glob("*_summary.json"):
            video_id = file.stem.replace("_summary", "")
            try:
                with open(file, 'r') as f:
                    all_data['summaries'][video_id] = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading summary {video_id}: {e}")

        return all_data

    def analyze_trends(self, all_data: Dict) -> Dict:
        """Analyze trends across all videos"""

        print("\n📈 Analyzing cross-video trends...")

        trend_mentions = defaultdict(lambda: {
            'count': 0,
            'videos': [],
            'stages': Counter(),
            'categories': Counter(),
            'opportunities': []
        })

        # Collect all trends
        for video_id, insights in all_data['insights'].items():
            video_title = insights.get('meta', {}).get('title', 'Unknown')

            for trend in insights.get('trends_signals', []):
                trend_text = trend.get('trend', '').lower()
                if not trend_text or len(trend_text) < 10:
                    continue

                # Normalize similar trends
                trend_key = self._normalize_trend(trend_text)

                trend_mentions[trend_key]['count'] += 1
                trend_mentions[trend_key]['videos'].append({
                    'video_id': video_id,
                    'title': video_title[:60]
                })

                stage = trend.get('stage', 'unknown')
                category = trend.get('category', 'unknown')
                opportunity = trend.get('opportunity', '')

                trend_mentions[trend_key]['stages'][stage] += 1
                trend_mentions[trend_key]['categories'][category] += 1

                if opportunity:
                    trend_mentions[trend_key]['opportunities'].append(opportunity)

        # Sort by frequency
        sorted_trends = sorted(
            trend_mentions.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        # Format top trends
        top_trends = []
        for trend_key, data in sorted_trends[:20]:
            most_common_stage = data['stages'].most_common(1)
            most_common_category = data['categories'].most_common(1)

            top_trends.append({
                'trend': trend_key,
                'frequency': data['count'],
                'mentioned_in_videos': data['count'],
                'stage': most_common_stage[0][0] if most_common_stage else 'unknown',
                'category': most_common_category[0][0] if most_common_category else 'unknown',
                'video_examples': data['videos'][:3],
                'opportunities': list(set(data['opportunities']))[:3]
            })

        return {
            'total_unique_trends': len(trend_mentions),
            'total_trend_mentions': sum(d['count'] for d in trend_mentions.values()),
            'top_trends': top_trends,
            'trend_categories': self._count_categories(trend_mentions)
        }

    def _normalize_trend(self, trend_text: str) -> str:
        """Normalize trend text for grouping"""
        # Simple normalization - can be enhanced with NLP
        trend_lower = trend_text.lower()

        # Common patterns
        if 'ai' in trend_lower or 'artificial intelligence' in trend_lower:
            if 'agent' in trend_lower:
                return 'ai_agents'
            elif 'automation' in trend_lower:
                return 'ai_automation'
            elif 'tool' in trend_lower or 'software' in trend_lower:
                return 'ai_tools'
            else:
                return 'ai_general'

        if 'saas' in trend_lower or 'software as a service' in trend_lower:
            if 'micro' in trend_lower:
                return 'microsaas'
            else:
                return 'saas'

        # Return first 50 chars as key
        return trend_text[:50]

    def _count_categories(self, trend_mentions: Dict) -> Dict:
        """Count trend categories"""
        category_counts = Counter()

        for data in trend_mentions.values():
            for category, count in data['categories'].items():
                category_counts[category] += count

        return dict(category_counts.most_common())

    def analyze_product_ecosystem(self, all_data: Dict) -> Dict:
        """Analyze product/tool ecosystem"""

        print("\n🔧 Analyzing product ecosystem...")

        product_mentions = defaultdict(lambda: {
            'count': 0,
            'categories': Counter(),
            'sentiments': Counter(),
            'use_cases': [],
            'videos': [],
            'pricing_mentions': [],
            'metrics': []
        })

        # Collect all products
        for video_id, insights in all_data['insights'].items():
            video_title = insights.get('meta', {}).get('title', 'Unknown')

            for product in insights.get('products_tools', []):
                name = product.get('name', '').strip()
                if not name or len(name) < 2:
                    continue

                # Normalize product name
                name_key = name.lower()

                product_mentions[name_key]['count'] += 1
                product_mentions[name_key]['categories'][product.get('category', 'unknown')] += 1
                product_mentions[name_key]['sentiments'][product.get('sentiment', 'neutral')] += 1

                use_case = product.get('use_case', '')
                if use_case:
                    product_mentions[name_key]['use_cases'].append(use_case)

                product_mentions[name_key]['videos'].append({
                    'video_id': video_id,
                    'title': video_title[:60]
                })

                pricing = product.get('pricing', '')
                if pricing and pricing != 'not specified':
                    product_mentions[name_key]['pricing_mentions'].append(pricing)

                metrics = product.get('metrics', '')
                if metrics:
                    product_mentions[name_key]['metrics'].append(metrics)

        # Sort by frequency
        sorted_products = sorted(
            product_mentions.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        # Format top products
        top_products = []
        for name, data in sorted_products[:30]:
            most_common_category = data['categories'].most_common(1)
            sentiment_score = self._calculate_sentiment_score(data['sentiments'])

            top_products.append({
                'name': name.title(),
                'mention_count': data['count'],
                'primary_category': most_common_category[0][0] if most_common_category else 'unknown',
                'sentiment_score': sentiment_score,
                'sentiment_distribution': dict(data['sentiments']),
                'common_use_cases': self._get_top_items(data['use_cases'], 3),
                'pricing_info': self._get_top_items(data['pricing_mentions'], 2),
                'metrics_mentioned': self._get_top_items(data['metrics'], 2),
                'video_examples': data['videos'][:3]
            })

        return {
            'total_unique_products': len(product_mentions),
            'total_product_mentions': sum(d['count'] for d in product_mentions.values()),
            'most_recommended_tools': top_products,
            'category_distribution': self._get_category_distribution(product_mentions)
        }

    def _calculate_sentiment_score(self, sentiments: Counter) -> str:
        """Calculate overall sentiment"""
        total = sum(sentiments.values())
        if total == 0:
            return 'neutral'

        positive_count = sentiments.get('positive', 0) + sentiments.get('recommended', 0) + sentiments.get('highly-recommended', 0)
        negative_count = sentiments.get('negative', 0)

        if positive_count > negative_count * 2:
            return 'highly_positive'
        elif positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _get_top_items(self, items: List[str], limit: int) -> List[str]:
        """Get most common items"""
        if not items:
            return []

        counter = Counter(items)
        return [item for item, count in counter.most_common(limit)]

    def _get_category_distribution(self, mentions: Dict) -> Dict:
        """Get product category distribution"""
        category_counts = Counter()

        for data in mentions.values():
            for category, count in data['categories'].items():
                category_counts[category] += count

        return dict(category_counts.most_common())

    def identify_strategy_playbooks(self, all_data: Dict) -> Dict:
        """Identify recurring strategy patterns"""

        print("\n📚 Identifying strategy playbooks...")

        strategy_patterns = defaultdict(lambda: {
            'count': 0,
            'type': '',
            'examples': [],
            'case_studies': [],
            'expected_results': []
        })

        # Collect strategies
        for video_id, insights in all_data['insights'].items():
            video_title = insights.get('meta', {}).get('title', 'Unknown')

            for strategy in insights.get('business_strategies', []):
                strategy_text = strategy.get('strategy', '').lower()
                if not strategy_text or len(strategy_text) < 15:
                    continue

                # Group similar strategies
                strategy_key = self._normalize_strategy(strategy_text)

                strategy_patterns[strategy_key]['count'] += 1
                strategy_patterns[strategy_key]['type'] = strategy.get('strategy_type', 'general')
                strategy_patterns[strategy_key]['examples'].append({
                    'video_id': video_id,
                    'title': video_title[:60],
                    'strategy': strategy.get('strategy', '')[:100],
                    'implementation': strategy.get('implementation', '')[:100]
                })

                case_study = strategy.get('case_study', '')
                if case_study:
                    strategy_patterns[strategy_key]['case_studies'].append(case_study)

                results = strategy.get('expected_results', '')
                if results:
                    strategy_patterns[strategy_key]['expected_results'].append(results)

        # Sort by frequency
        sorted_strategies = sorted(
            strategy_patterns.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        # Format playbooks
        playbooks = []
        for strategy_key, data in sorted_strategies[:15]:
            if data['count'] >= 2:  # Only patterns mentioned 2+ times
                playbooks.append({
                    'playbook_name': strategy_key.replace('_', ' ').title(),
                    'frequency': data['count'],
                    'strategy_type': data['type'],
                    'examples': data['examples'][:3],
                    'case_studies': list(set(data['case_studies']))[:3],
                    'expected_outcomes': list(set(data['expected_results']))[:3]
                })

        return {
            'total_strategy_mentions': sum(d['count'] for d in strategy_patterns.values()),
            'recurring_playbooks': playbooks,
            'strategy_type_distribution': self._get_strategy_type_dist(strategy_patterns)
        }

    def _normalize_strategy(self, strategy_text: str) -> str:
        """Normalize strategy for grouping"""
        strategy_lower = strategy_text.lower()

        # Common patterns
        if 'audience' in strategy_lower and ('first' in strategy_lower or 'build' in strategy_lower):
            return 'audience_first_approach'
        elif 'freemium' in strategy_lower:
            return 'freemium_model'
        elif 'community' in strategy_lower:
            return 'community_building'
        elif 'content' in strategy_lower and 'marketing' in strategy_lower:
            return 'content_marketing'
        elif 'viral' in strategy_lower or 'word of mouth' in strategy_lower:
            return 'viral_growth'
        elif 'paid' in strategy_lower and 'ads' in strategy_lower:
            return 'paid_advertising'
        elif 'seo' in strategy_lower:
            return 'seo_strategy'
        elif 'partnership' in strategy_lower or 'collab' in strategy_lower:
            return 'partnerships'

        return strategy_text[:40]

    def _get_strategy_type_dist(self, patterns: Dict) -> Dict:
        """Get strategy type distribution"""
        type_counts = Counter()

        for data in patterns.values():
            type_counts[data['type']] += data['count']

        return dict(type_counts.most_common())

    def analyze_expert_consensus(self, all_data: Dict) -> Dict:
        """Analyze agreement/disagreement on topics"""

        print("\n🤝 Analyzing expert consensus...")

        # Topics to analyze
        topics = {
            'ai_tools': ['ai', 'chatgpt', 'gpt', 'claude', 'llm'],
            'paid_ads': ['paid ads', 'advertising', 'facebook ads', 'google ads'],
            'content_marketing': ['content', 'seo', 'blog'],
            'saas_business': ['saas', 'software', 'subscription'],
            'community_building': ['community', 'audience', 'following']
        }

        consensus = {}

        for topic_name, keywords in topics.items():
            mentions = []

            # Find mentions in strategies and quotes
            for video_id, insights in all_data['insights'].items():
                video_title = insights.get('meta', {}).get('title', 'Unknown')

                # Check strategies
                for strategy in insights.get('business_strategies', []):
                    strategy_text = json.dumps(strategy).lower()
                    if any(keyword in strategy_text for keyword in keywords):
                        mentions.append({
                            'video_id': video_id,
                            'video_title': video_title[:60],
                            'type': 'strategy',
                            'content': strategy.get('strategy', '')[:150],
                            'sentiment': self._extract_sentiment(strategy_text)
                        })

                # Check quotes
                for quote in insights.get('actionable_quotes', []):
                    quote_text = json.dumps(quote).lower()
                    if any(keyword in quote_text for keyword in keywords):
                        mentions.append({
                            'video_id': video_id,
                            'video_title': video_title[:60],
                            'type': 'quote',
                            'content': quote.get('quote', '')[:150],
                            'sentiment': self._extract_sentiment(quote_text)
                        })

            # Calculate consensus
            if mentions:
                sentiment_counts = Counter(m['sentiment'] for m in mentions)
                total = len(mentions)

                consensus_level = 'high' if max(sentiment_counts.values()) / total > 0.7 else \
                                 'medium' if max(sentiment_counts.values()) / total > 0.5 else 'low'

                consensus[topic_name] = {
                    'total_mentions': total,
                    'consensus_level': consensus_level,
                    'sentiment_distribution': dict(sentiment_counts),
                    'examples': mentions[:5]
                }

        return consensus

    def _extract_sentiment(self, text: str) -> str:
        """Extract sentiment from text"""
        positive_words = ['good', 'great', 'excellent', 'recommend', 'effective', 'success', 'best']
        negative_words = ['avoid', 'bad', 'waste', 'fail', 'difficult', 'problem', 'issue']

        text_lower = text.lower()

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def create_opportunity_matrix(self, all_data: Dict) -> Dict:
        """Create comprehensive opportunity matrix"""

        print("\n🎯 Creating opportunity matrix...")

        all_opportunities = []

        # Collect from summaries
        for video_id, summary in all_data['summaries'].items():
            opp_map = summary.get('opportunity_map', {})

            for opp_type, opportunities in opp_map.get('opportunities', {}).items():
                for opp in opportunities:
                    all_opportunities.append({
                        **opp,
                        'source_video': video_id,
                        'video_title': summary.get('video_title', 'Unknown')[:60]
                    })

        # Categorize and rank
        startup_ideas = [o for o in all_opportunities if o.get('type') == 'startup_idea']
        market_gaps = [o for o in all_opportunities if o.get('type') == 'market_gap']
        trend_opps = [o for o in all_opportunities if o.get('type') == 'trend_opportunity']

        return {
            'total_opportunities': len(all_opportunities),
            'by_type': {
                'startup_ideas': len(startup_ideas),
                'market_gaps': len(market_gaps),
                'trend_opportunities': len(trend_opps)
            },
            'top_startup_ideas': startup_ideas[:20],
            'top_market_gaps': market_gaps[:20],
            'top_trend_opportunities': trend_opps[:20]
        }

    def generate_meta_intelligence(self) -> Dict:
        """Generate complete meta-intelligence report"""

        print(f"\n{'='*70}")
        print(f"🧠 META-INTELLIGENCE ANALYZER v{self.VERSION}")
        print(f"{'='*70}")

        # Load all data
        print("\n📂 Loading all data...")
        all_data = self.load_all_data()

        print(f"   Loaded {len(all_data['insights'])} insights")
        print(f"   Loaded {len(all_data['enriched'])} enriched files")
        print(f"   Loaded {len(all_data['summaries'])} summaries")

        # Run analyses
        trends = self.analyze_trends(all_data)
        products = self.analyze_product_ecosystem(all_data)
        playbooks = self.identify_strategy_playbooks(all_data)
        consensus = self.analyze_expert_consensus(all_data)
        opportunities = self.create_opportunity_matrix(all_data)

        # Compile report
        report = {
            'meta_intelligence_version': self.VERSION,
            'generated_at': datetime.now().isoformat(),
            'data_scope': {
                'total_videos': len(all_data['insights']),
                'total_insights': sum(
                    sum(len(v) if isinstance(v, list) else 0
                        for k, v in insights.items() if k != 'meta')
                    for insights in all_data['insights'].values()
                )
            },

            'cross_video_trends': trends,
            'product_ecosystem': products,
            'strategy_playbooks': playbooks,
            'expert_consensus': consensus,
            'opportunity_matrix': opportunities
        }

        # Save report
        report_file = self.meta_dir / 'meta_intelligence_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✅ Meta-intelligence report saved: {report_file}")
        print(f"{'='*70}\n")

        return report


def main():
    """CLI interface"""
    engine = MetaIntelligenceEngine()
    report = engine.generate_meta_intelligence()

    # Print summary
    print("\n📊 META-INTELLIGENCE SUMMARY")
    print("="*70)
    print(f"Videos Analyzed: {report['data_scope']['total_videos']}")
    print(f"Total Insights: {report['data_scope']['total_insights']}")
    print(f"\nTop Trends: {len(report['cross_video_trends']['top_trends'])}")
    print(f"Top Products: {len(report['product_ecosystem']['most_recommended_tools'])}")
    print(f"Strategy Playbooks: {len(report['strategy_playbooks']['recurring_playbooks'])}")
    print(f"Total Opportunities: {report['opportunity_matrix']['total_opportunities']}")
    print("="*70)


if __name__ == "__main__":
    main()

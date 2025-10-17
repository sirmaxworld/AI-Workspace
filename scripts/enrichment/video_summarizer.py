#!/usr/bin/env python3
"""
Video Summarizer - Generate comprehensive video-level summaries
Creates key takeaways, content profiles, and opportunity maps
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoSummarizer:
    """Generate comprehensive video-level summaries from enriched data"""

    VERSION = "1.0.0"

    def __init__(self, workspace_dir: Path = None):
        if workspace_dir is None:
            workspace_dir = Path("/Users/yourox/AI-Workspace")

        self.workspace_dir = workspace_dir
        self.insights_dir = workspace_dir / "data" / "business_insights"
        self.enriched_dir = workspace_dir / "data" / "enriched_insights"
        self.summaries_dir = workspace_dir / "data" / "video_summaries"
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

    def load_insight(self, video_id: str) -> Optional[Dict]:
        """Load original insight data"""
        insight_file = self.insights_dir / f"{video_id}_insights.json"
        if not insight_file.exists():
            return None

        try:
            with open(insight_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading insight for {video_id}: {e}")
            return None

    def load_enriched(self, video_id: str) -> Optional[Dict]:
        """Load enriched data"""
        enriched_file = self.enriched_dir / f"{video_id}_enriched.json"
        if not enriched_file.exists():
            return None

        try:
            with open(enriched_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading enriched data for {video_id}: {e}")
            return None

    def generate_content_profile(self, insights: Dict, enriched: Dict) -> Dict:
        """Generate content profile for video"""

        # Extract themes from title and content
        title = insights.get('meta', {}).get('title', '')

        # Count category distribution
        category_counts = {}
        for key in ['products_tools', 'business_strategies', 'problems_solutions',
                   'startup_ideas', 'growth_tactics', 'ai_workflows', 'trends_signals']:
            if key in insights:
                items = insights[key]
                if isinstance(items, list):
                    category_counts[key] = len(items)

        # Determine primary themes
        primary_themes = []
        if category_counts.get('startup_ideas', 0) > 3:
            primary_themes.append('startup_ideas')
        if category_counts.get('ai_workflows', 0) > 3:
            primary_themes.append('ai_automation')
        if category_counts.get('growth_tactics', 0) > 3:
            primary_themes.append('growth_strategies')
        if category_counts.get('trends_signals', 0) > 5:
            primary_themes.append('market_trends')

        # Determine experience level from avg scores
        vm = enriched.get('video_level_metrics', {})
        avg_complexity = (
            (100 - vm.get('avg_actionability_score', 50)) +
            (100 - vm.get('avg_specificity_score', 50))
        ) / 2

        if avg_complexity < 40:
            experience_level = 'beginner'
        elif avg_complexity < 60:
            experience_level = 'intermediate'
        else:
            experience_level = 'advanced'

        # Extract industries/domains mentioned
        industries = set()
        for product in insights.get('products_tools', []):
            category = product.get('category', '').lower()
            if 'saas' in category:
                industries.add('SaaS')
            if 'ai' in category:
                industries.add('AI')
            if 'mobile' in category:
                industries.add('Mobile')

        return {
            'title': title,
            'video_type': enriched.get('video_type', 'general'),
            'type_confidence': enriched.get('type_confidence', 0),
            'primary_themes': primary_themes,
            'experience_level': experience_level,
            'industry_focus': list(industries) if industries else ['general'],
            'content_density': len(category_counts),
            'category_distribution': category_counts
        }

    def generate_key_takeaways(self, insights: Dict, enriched: Dict) -> List[str]:
        """Generate top 3-5 key takeaways from video"""

        takeaways = []

        # Get insight metrics
        insight_metrics = enriched.get('insight_metrics', {})

        # Find highest scoring insights across all categories
        all_insights = []

        for category_key, category_name in [
            ('ideas', 'startup_ideas'),
            ('strategies', 'business_strategies'),
            ('problems', 'problems_solutions'),
            ('tactics', 'growth_tactics'),
            ('workflows', 'ai_workflows')
        ]:
            if category_key in insight_metrics and category_name in insights:
                metrics = insight_metrics[category_key]
                items = insights[category_name]

                for idx, (metric, item) in enumerate(zip(metrics, items)):
                    score = (
                        metric.get('actionability_score', 0) * 0.4 +
                        metric.get('specificity_score', 0) * 0.3 +
                        metric.get('evidence_strength', 0) * 0.3
                    )

                    all_insights.append({
                        'score': score,
                        'category': category_name,
                        'item': item,
                        'metrics': metric
                    })

        # Sort by score
        all_insights.sort(key=lambda x: x['score'], reverse=True)

        # Generate takeaways from top insights
        for insight in all_insights[:5]:
            item = insight['item']
            category = insight['category']

            if category == 'startup_ideas':
                takeaway = f"Startup Opportunity: {item.get('idea', 'N/A')[:100]}"
                if item.get('target_market'):
                    takeaway += f" (Target: {item.get('target_market')[:50]})"
                takeaways.append(takeaway)

            elif category == 'business_strategies':
                takeaway = f"Strategy: {item.get('strategy', 'N/A')[:100]}"
                takeaways.append(takeaway)

            elif category == 'problems_solutions':
                takeaway = f"Solution: {item.get('solution', 'N/A')[:100]}"
                if item.get('difficulty'):
                    takeaway += f" (Difficulty: {item.get('difficulty')})"
                takeaways.append(takeaway)

            elif category == 'growth_tactics':
                takeaway = f"Growth Tactic: {item.get('tactic', 'N/A')[:100]}"
                if item.get('channel'):
                    takeaway += f" (Channel: {item.get('channel')})"
                takeaways.append(takeaway)

            elif category == 'ai_workflows':
                takeaway = f"AI Workflow: {item.get('workflow_name', 'N/A')[:100]}"
                takeaways.append(takeaway)

        return takeaways[:5]  # Top 5

    def identify_standout_insights(self, enriched: Dict, insights: Dict) -> List[Dict]:
        """Identify top insights by combined score"""

        standouts = []
        insight_metrics = enriched.get('insight_metrics', {})

        category_map = {
            'products': 'products_tools',
            'strategies': 'business_strategies',
            'problems': 'problems_solutions',
            'ideas': 'startup_ideas',
            'tactics': 'growth_tactics',
            'workflows': 'ai_workflows',
            'trends': 'trends_signals',
            'quotes': 'actionable_quotes'
        }

        for short_key, full_key in category_map.items():
            if short_key not in insight_metrics or full_key not in insights:
                continue

            metrics = insight_metrics[short_key]
            items = insights[full_key]

            for idx, (metric, item) in enumerate(zip(metrics, items)):
                # Combined score
                combined = (
                    metric.get('actionability_score', 0) * 0.35 +
                    metric.get('specificity_score', 0) * 0.25 +
                    metric.get('evidence_strength', 0) * 0.25 +
                    (metric.get('recency_score', 70) - 70) * 0.15  # Bonus for recency
                )

                if combined > 60:  # Only high scoring
                    standouts.append({
                        'category': full_key,
                        'index': idx,
                        'combined_score': round(combined, 1),
                        'metrics': metric,
                        'content': item
                    })

        # Sort by score and return top 10
        standouts.sort(key=lambda x: x['combined_score'], reverse=True)
        return standouts[:10]

    def create_opportunity_map(self, insights: Dict, enriched: Dict) -> Dict:
        """Create opportunity map from insights"""

        opportunities = []

        # Startup ideas
        for idea in insights.get('startup_ideas', []):
            opportunities.append({
                'type': 'startup_idea',
                'title': idea.get('idea', 'N/A')[:80],
                'target_market': idea.get('target_market', 'N/A'),
                'problem_solved': idea.get('problem_solved', 'N/A'),
                'business_model': idea.get('business_model', 'N/A'),
                'validation': idea.get('validation', 'N/A'),
                'estimated_investment': idea.get('investment_needed', 'Unknown')
            })

        # Market gaps (from problems/solutions)
        for problem in insights.get('problems_solutions', []):
            if problem.get('category') == 'business' or problem.get('category') == 'market-research':
                opportunities.append({
                    'type': 'market_gap',
                    'title': problem.get('problem', 'N/A')[:80],
                    'solution_approach': problem.get('solution', 'N/A')[:100],
                    'difficulty': problem.get('difficulty', 'unknown'),
                    'tools_needed': problem.get('tools_needed', [])
                })

        # Trends with opportunity
        for trend in insights.get('trends_signals', []):
            if trend.get('stage') in ['early', 'emerging', 'growing']:
                opportunities.append({
                    'type': 'trend_opportunity',
                    'title': trend.get('trend', 'N/A')[:80],
                    'stage': trend.get('stage', 'unknown'),
                    'category': trend.get('category', 'general'),
                    'opportunity': trend.get('opportunity', 'N/A')
                })

        # Categorize opportunities
        categorized = {
            'startup_ideas': [o for o in opportunities if o['type'] == 'startup_idea'],
            'market_gaps': [o for o in opportunities if o['type'] == 'market_gap'],
            'trend_opportunities': [o for o in opportunities if o['type'] == 'trend_opportunity']
        }

        return {
            'total_opportunities': len(opportunities),
            'by_type': {
                'startup_ideas': len(categorized['startup_ideas']),
                'market_gaps': len(categorized['market_gaps']),
                'trend_opportunities': len(categorized['trend_opportunities'])
            },
            'opportunities': categorized
        }

    def analyze_comment_intelligence(self, insights: Dict) -> Dict:
        """Analyze comment-derived insights if present"""

        comment_insights = insights.get('comment_insights', [])
        top_comments = insights.get('top_validated_comments', [])
        comment_trends = insights.get('comment_derived_trends', [])

        if not (comment_insights or top_comments or comment_trends):
            return {
                'available': False,
                'message': 'No comment data available for this video'
            }

        # Categorize comment insights
        insight_types = Counter(ci.get('type', 'unknown') for ci in comment_insights)

        # Get highest engagement comments
        high_engagement = sorted(
            [c for c in top_comments if c.get('likes', 0) > 1000],
            key=lambda x: x.get('likes', 0),
            reverse=True
        )[:5]

        return {
            'available': True,
            'total_comment_insights': len(comment_insights),
            'total_validated_comments': len(top_comments),
            'total_comment_trends': len(comment_trends),
            'insight_types': dict(insight_types),
            'top_high_engagement_comments': high_engagement,
            'comment_derived_trends': comment_trends
        }

    def generate_summary(self, video_id: str) -> Optional[Dict]:
        """Generate complete video summary"""

        # Load data
        insights = self.load_insight(video_id)
        enriched = self.load_enriched(video_id)

        if not insights or not enriched:
            logger.error(f"Missing data for {video_id}")
            return None

        # Generate all components
        content_profile = self.generate_content_profile(insights, enriched)
        key_takeaways = self.generate_key_takeaways(insights, enriched)
        standout_insights = self.identify_standout_insights(enriched, insights)
        opportunity_map = self.create_opportunity_map(insights, enriched)
        comment_intelligence = self.analyze_comment_intelligence(insights)

        # Video-level metrics from enriched
        vm = enriched.get('video_level_metrics', {})

        summary = {
            'video_id': video_id,
            'video_title': insights.get('meta', {}).get('title', 'Unknown'),
            'summary_version': self.VERSION,
            'generated_at': enriched.get('_computed_at', ''),

            'content_profile': content_profile,
            'key_takeaways': key_takeaways,
            'standout_insights': standout_insights,
            'opportunity_map': opportunity_map,
            'comment_intelligence': comment_intelligence,

            'metrics_summary': {
                'total_insights': vm.get('total_insights', 0),
                'high_value_insights': vm.get('high_value_insights', 0),
                'avg_actionability': vm.get('avg_actionability_score', 0),
                'avg_specificity': vm.get('avg_specificity_score', 0),
                'avg_evidence': vm.get('avg_evidence_strength', 0),
                'avg_recency': vm.get('avg_recency_score', 0)
            },

            'practical_next_steps': self._generate_next_steps(insights, standout_insights),
            'related_videos_keywords': self._extract_keywords(insights, enriched)
        }

        return summary

    def _generate_next_steps(self, insights: Dict, standouts: List[Dict]) -> List[str]:
        """Generate practical next steps based on content"""

        next_steps = []

        # From startup ideas
        if insights.get('startup_ideas'):
            next_steps.append("Validate one of the startup ideas with target market interviews")

        # From growth tactics
        if len(insights.get('growth_tactics', [])) > 2:
            next_steps.append("Implement the highest-scoring growth tactic this week")

        # From AI workflows
        if insights.get('ai_workflows'):
            next_steps.append("Set up one AI workflow to automate a business process")

        # From mistakes
        if insights.get('mistakes_to_avoid'):
            next_steps.append("Review mistakes to avoid and create prevention checklist")

        # From products
        if len(insights.get('products_tools', [])) > 3:
            next_steps.append("Evaluate recommended tools for your tech stack")

        return next_steps[:5]

    def _extract_keywords(self, insights: Dict, enriched: Dict) -> List[str]:
        """Extract keywords for finding related videos"""

        keywords = set()

        # From content profile themes
        profile = self.generate_content_profile(insights, enriched)
        keywords.update(profile.get('primary_themes', []))
        keywords.update(profile.get('industry_focus', []))

        # From product categories
        for product in insights.get('products_tools', [])[:5]:
            if product.get('category'):
                keywords.add(product['category'])

        # From strategy types
        for strategy in insights.get('business_strategies', [])[:5]:
            if strategy.get('strategy_type'):
                keywords.add(strategy['strategy_type'])

        return list(keywords)[:10]

    def save_summary(self, video_id: str, summary: Dict):
        """Save video summary to file"""
        summary_file = self.summaries_dir / f"{video_id}_summary.json"

        try:
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Saved summary for {video_id}")
        except Exception as e:
            logger.error(f"Error saving summary for {video_id}: {e}")
            raise

    def summarize_all_videos(self, limit: int = None):
        """Generate summaries for all videos"""
        print(f"\n{'='*70}")
        print(f"📝 VIDEO SUMMARY GENERATOR v{self.VERSION}")
        print(f"{'='*70}\n")

        enriched_files = list(self.enriched_dir.glob("*_enriched.json"))

        if limit:
            enriched_files = enriched_files[:limit]

        total = len(enriched_files)
        print(f"📹 Found {total} enriched videos")

        # Check existing
        existing = len(list(self.summaries_dir.glob("*_summary.json")))
        print(f"✅ Already summarized: {existing}")
        print(f"🔄 To process: {total - existing}\n")

        stats = {'success': 0, 'errors': 0, 'cached': 0}

        for i, enriched_file in enumerate(enriched_files, 1):
            video_id = enriched_file.stem.replace("_enriched", "")

            # Check if already done
            summary_file = self.summaries_dir / f"{video_id}_summary.json"
            if summary_file.exists():
                print(f"[{i}/{total}] {video_id} ⚡ cached")
                stats['cached'] += 1
                continue

            print(f"[{i}/{total}] {video_id} ", end="", flush=True)

            try:
                summary = self.generate_summary(video_id)
                if summary:
                    self.save_summary(video_id, summary)
                    print("✅ summarized")
                    stats['success'] += 1
                else:
                    print("❌ failed")
                    stats['errors'] += 1
            except Exception as e:
                print(f"❌ error: {e}")
                stats['errors'] += 1
                logger.exception(f"Error processing {video_id}")

        print(f"\n{'='*70}")
        print(f"✅ SUMMARY GENERATION COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Successfully generated: {stats['success']}")
        print(f"⚡ Cached (skipped): {stats['cached']}")
        print(f"❌ Errors: {stats['errors']}")
        print(f"{'='*70}\n")

        return stats


def main():
    """CLI interface"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Video Summary Generator")
    parser.add_argument('command', nargs='?', default='summarize-all',
                       choices=['summarize', 'summarize-all'],
                       help='Command to run')
    parser.add_argument('--video-id', help='Video ID to summarize')
    parser.add_argument('--limit', type=int, help='Limit number of videos')

    args = parser.parse_args()

    summarizer = VideoSummarizer()

    if args.command == 'summarize':
        if not args.video_id:
            print("Error: --video-id required for 'summarize' command")
            sys.exit(1)

        summary = summarizer.generate_summary(args.video_id)
        if summary:
            summarizer.save_summary(args.video_id, summary)
            print(json.dumps(summary, indent=2))

    elif args.command == 'summarize-all':
        summarizer.summarize_all_videos(limit=args.limit)


if __name__ == "__main__":
    main()

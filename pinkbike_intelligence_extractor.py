#!/usr/bin/env python3
"""
Pinkbike Intelligence Extractor
Transform Pinkbike articles into actionable cycling industry insights
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')


class PinkbikeIntelligenceExtractor:
    """Extract structured cycling intelligence from Pinkbike articles"""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.articles_dir = self.workspace_dir / "data" / "pinkbike_articles"
        self.insights_dir = self.workspace_dir / "data" / "pinkbike_insights"
        self.insights_dir.mkdir(parents=True, exist_ok=True)

    def extract_insights(self, article_data: Dict) -> Dict:
        """
        Extract comprehensive cycling intelligence from Pinkbike article

        Returns structured insights following the cycling schema
        """
        article_id = article_data.get('article_id')
        title = article_data.get('title', '')
        article_type = self._detect_article_type(title)

        # Get full content
        content = article_data.get('content', '')

        if not content or len(content) < 200:
            return {"error": "Article content too short for analysis"}

        # Get comments data
        comments_data = article_data.get('comments', {})
        comments = comments_data.get('items', [])
        has_comments = len(comments) > 0

        print(f"  🧠 Analyzing: {title[:60]}...")
        print(f"    📋 Type: {article_type}")
        if has_comments:
            print(f"    💬 Including {len(comments)} comments in analysis")

        # Build comments section for prompt
        comments_section = ""
        if has_comments:
            comments_text = "\n".join([
                f"- [{c['likes']} likes] @{c['author']}: {c['text'][:200]}"
                for c in comments[:20]  # Limit to top 20 for token efficiency
            ])
            comments_section = f"""

COMMUNITY COMMENTS (Sorted by engagement/likes):
{comments_text}
"""

        # Create comprehensive extraction prompt
        prompt = f"""Analyze this Pinkbike article and comments to extract structured cycling industry intelligence.

ARTICLE: {title}
TYPE: {article_type}
URL: {article_data.get('url', 'N/A')}

ARTICLE CONTENT (first 10000 chars):
{content[:10000]}{comments_section}

Extract and structure the following information in JSON format:

{{
  "cycling_products": {{
    "mountain_bikes": [
      {{
        "bike_name": "full product name",
        "brand": "manufacturer",
        "model_year": "2024/2025/etc",
        "category": "xc/trail/enduro/downhill/e-bike",
        "price": "retail price if mentioned",
        "frame_material": "carbon/aluminum/steel/titanium",
        "wheel_size": "26/27.5/29/mullet",
        "travel_front": "mm of travel",
        "travel_rear": "mm of travel",
        "geometry_notes": "standout geometry features",
        "suspension_type": "hardtail/full-suspension",
        "sentiment": "positive/negative/neutral/highly-recommended/best-value/not-recommended",
        "pros": ["pro 1", "pro 2"],
        "cons": ["con 1", "con 2"],
        "best_for": "rider type/use case",
        "field_test_ranking": "if mentioned",
        "editor_rating": "if provided"
      }}
    ],
    "components": [
      {{
        "component_name": "product name",
        "brand": "manufacturer",
        "category": "fork/shock/drivetrain/brakes/wheels/tires/cockpit/seatpost/pedals",
        "price": "retail price",
        "weight": "if mentioned",
        "compatibility": ["standards, mounting options"],
        "tech_features": ["feature 1", "feature 2"],
        "sentiment": "positive/negative/neutral/recommended/cautioned",
        "performance_notes": "how it performs",
        "durability_notes": "reliability mentioned",
        "value_assessment": "value for money"
      }}
    ],
    "apparel_gear": [
      {{
        "product_name": "item name",
        "brand": "manufacturer",
        "category": "helmet/pads/gloves/shoes/jersey/shorts/jacket/accessories",
        "price": "retail price",
        "protection_level": "basic/moderate/high",
        "features": ["feature 1", "feature 2"],
        "sentiment": "positive/negative/neutral/recommended",
        "best_use": "application"
      }}
    ]
  }},

  "cycling_trends": {{
    "technology_trends": [
      {{
        "trend_name": "trend description",
        "category": "suspension/geometry/drivetrain/wheels/e-bike/materials/integration",
        "description": "detailed explanation",
        "adoption_stage": "emerging/growing/mainstream/declining",
        "brands_adopting": ["brand 1", "brand 2"],
        "impact": "revolutionary/significant/incremental",
        "price_impact": "cost implications",
        "predicted_future": "where this is heading"
      }}
    ],
    "market_trends": [
      {{
        "trend_description": "market shift description",
        "category": "pricing/bike-categories/consumer-preferences/sales-channels/market-segments",
        "evidence": "supporting data or observations",
        "implications": "what this means for industry/consumers",
        "opportunity_level": "high/medium/low"
      }}
    ],
    "geometry_trends": [
      {{
        "geometry_change": "what's changing (reach, stack, etc)",
        "category_affected": ["xc", "trail", "enduro"],
        "measurement": "specific numbers if mentioned",
        "direction": "increasing/decreasing/stabilizing",
        "reasoning": "why this change",
        "brands_leading": ["brand 1", "brand 2"]
      }}
    ]
  }},

  "gear_recommendations": {{
    "editor_picks": [
      {{
        "product_name": "recommended product",
        "category": "product category",
        "why_recommended": "reasoning",
        "price": "price point",
        "best_for": "use case/rider type",
        "alternatives": ["alternative 1", "alternative 2"]
      }}
    ],
    "field_test_results": [
      {{
        "test_name": "field test name",
        "year": "2024/2025",
        "category": "test category",
        "winner": "winning product",
        "runner_ups": ["product 2", "product 3"],
        "best_value": "value winner",
        "most_innovative": "innovation winner",
        "test_criteria": ["criteria 1", "criteria 2"],
        "key_findings": "major takeaways"
      }}
    ],
    "value_picks": [
      {{
        "product_name": "value product",
        "category": "category",
        "price": "price point",
        "competes_with": "more expensive alternatives",
        "value_proposition": "what makes it good value",
        "compromises": "trade-offs"
      }}
    ]
  }},

  "cycling_problems": {{
    "reliability_issues": [
      {{
        "product_affected": "product with issues",
        "issue_description": "what's wrong",
        "severity": "critical/major/minor",
        "frequency": "widespread/common/occasional/rare",
        "manufacturer_response": "how brand is responding",
        "solutions_available": "fixes or workarounds",
        "user_impact": "effect on riders"
      }}
    ],
    "compatibility_issues": [
      {{
        "standards_conflict": "incompatibility description",
        "products_affected": ["product 1", "product 2"],
        "workarounds": "solutions",
        "industry_direction": "where standards are heading"
      }}
    ],
    "availability_pricing": [
      {{
        "product": "affected product",
        "issue": "out-of-stock/price-increase/discontinued/limited-availability",
        "impact_on_consumers": "effect on buyers",
        "alternatives": ["alternative 1", "alternative 2"]
      }}
    ]
  }},

  "community_insights": {{
    "comment_sentiment": [
      {{
        "topic": "what's being discussed",
        "overall_sentiment": "very-positive/positive/neutral/negative/very-negative",
        "agreement_level": "strong-consensus/general-agreement/mixed/divided",
        "key_opinions": ["opinion 1", "opinion 2"],
        "engagement_level": "high/medium/low"
      }}
    ],
    "user_validation": [
      {{
        "claim_or_review": "what's being validated",
        "community_response": "confirmed/disputed/mixed",
        "supporting_evidence": ["supporting comment 1", "supporting comment 2"],
        "dissenting_opinions": ["dissenting comment 1"],
        "consensus_reached": "community conclusion"
      }}
    ],
    "feature_requests": [
      {{
        "requested_feature": "what riders want",
        "product_category": "where it's wanted",
        "frequency_mentioned": "very-common/common/occasional",
        "user_justification": "why they want it"
      }}
    ],
    "brand_perception": [
      {{
        "brand_name": "brand being discussed",
        "reputation": "excellent/good/mixed/poor",
        "strengths_mentioned": ["strength 1", "strength 2"],
        "weaknesses_mentioned": ["weakness 1", "weakness 2"],
        "customer_service_sentiment": "feedback on service",
        "value_perception": "perceived value",
        "innovation_perception": "innovation reputation"
      }}
    ]
  }},

  "industry_news": {{
    "product_launches": [
      {{
        "product_name": "new product",
        "brand": "manufacturer",
        "launch_date": "when announced",
        "key_features": ["feature 1", "feature 2"],
        "price": "retail price",
        "availability": "when available",
        "significance": "major/moderate/minor"
      }}
    ],
    "brand_news": [
      {{
        "brand_name": "brand",
        "news_type": "acquisition/new-ownership/financial/expansion/recall",
        "description": "what happened",
        "impact": "implications"
      }}
    ]
  }},

  "enriched_metadata": {{
    "test_conditions": {{
      "test_duration_days": "number if mentioned",
      "test_locations": ["location names from article"],
      "terrain_types": ["type of trails tested on"],
      "weather_conditions": "wet/dry/mixed if mentioned",
      "reviewer_specs": {{
        "height_cm": "reviewer height if mentioned",
        "weight_kg": "reviewer weight if mentioned",
        "skill_level": "beginner/intermediate/advanced/expert (infer from article)",
        "riding_style": "aggressive/smooth/technical (infer from description)"
      }}
    }},
    "targeting": {{
      "skill_levels": ["beginner", "intermediate", "advanced", "expert - who this product is for"],
      "ideal_use_cases": ["specific riding applications mentioned"],
      "not_recommended_for": ["use cases the product is NOT good for"],
      "rider_weight_range_kg": ["min", "max if weight limits mentioned"],
      "rider_height_range_cm": ["min", "max if size recommendations given"],
      "fitness_required": "low/moderate/high (based on product demands)"
    }},
    "product_lifecycle": {{
      "model_year": "year if mentioned",
      "lifecycle_stage": "new/current-gen/previous-gen/discontinued (infer from article context)",
      "successor_model": "name of newer model if mentioned",
      "availability": "in-stock/limited/pre-order/discontinued (if mentioned)"
    }},
    "competitive_analysis": {{
      "direct_competitors": [
        {{
          "name": "competitor product mentioned",
          "comparison": "how it compares",
          "price_difference_usd": "number or null"
        }}
      ],
      "category_position": "leader/mid-pack/value-option/underdog (infer from review)",
      "unique_selling_points": ["standout features that differentiate this product"],
      "weaknesses_vs_competition": ["areas where competitors are better"]
    }},
    "quantitative_scores": {{
      "overall_rating": "number/10 if given",
      "category_scores": {{
        "climbing": "score if mentioned",
        "descending": "score if mentioned",
        "value": "score if mentioned",
        "build_quality": "score if mentioned"
      }},
      "field_test_ranking": "placement if mentioned",
      "total_bikes_tested": "number of bikes in comparison",
      "awards": ["editor-choice", "value-winner", etc if awarded"]
    }},
    "pricing_intelligence": {{
      "msrp_usd": "number if mentioned",
      "street_price_usd": "actual price if different from MSRP",
      "price_trend": "increasing/stable/decreasing (infer from context)",
      "price_per_performance_score": "value assessment"
    }},
    "ownership_intelligence": {{
      "common_upgrades": ["parts users typically upgrade based on comments/article"],
      "warranty_issues_reported": ["warranty problems mentioned in comments"],
      "parts_availability": "excellent/good/limited/poor (from comments/article)",
      "service_requirements": "low/standard/high (maintenance needs mentioned)"
    }}
  }},

  "meta": {{
    "article_id": "{article_id}",
    "url": "{article_data.get('url', '')}",
    "title": "{title}",
    "author": "{article_data.get('author', '')}",
    "publish_date": "{article_data.get('publish_date', '')}",
    "article_type": "{article_type}",
    "tags": {article_data.get('tags', [])},
    "total_comments": {len(comments)},
    "high_engagement_comments": {len([c for c in comments if c.get('likes', 0) > 50])}
  }}
}}

IMPORTANT:
- Only include items that are ACTUALLY discussed in the article
- Be specific and detailed - include real model names, prices, measurements
- For reviews, extract all pros/cons and performance details
- For field tests, extract rankings and comparative insights
- COMMENT ANALYSIS: Extract insights from community comments about:
  * User experiences with products mentioned
  * Validation or disputes of claims in the article
  * Brand reputation and perception
  * Feature requests and desires
  * Alternative products suggested
  * Common problems riders are experiencing
- High-engagement comments (>50 likes) indicate strong community agreement
- Return valid JSON only
"""

        try:
            import signal
            import time

            start_time = time.time()

            # Add timeout protection (90 seconds for longer articles)
            def timeout_handler(signum, frame):
                raise TimeoutError("API call exceeded 90 seconds")

            # Set timeout (only works on Unix systems)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(90)
            except:
                pass  # Windows doesn't support SIGALRM

            response = self.client.messages.create(
                model=self.model,
                max_tokens=5000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
                timeout=80.0  # Anthropic client timeout
            )

            # Cancel alarm
            try:
                signal.alarm(0)
            except:
                pass

            elapsed = time.time() - start_time
            print(f"    ⏱️  API call: {elapsed:.1f}s")

            # Parse JSON response
            response_text = response.content[0].text

            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())

                # Update metadata
                if 'meta' not in insights:
                    insights['meta'] = {}

                insights['meta']['extracted_at'] = __import__('datetime').datetime.now().isoformat()
                insights['meta']['model'] = self.model
                insights['meta']['content_length'] = len(content)
                insights['meta']['processing_time_seconds'] = elapsed
                insights['meta']['data_source'] = 'pinkbike'

                return insights
            else:
                return {"error": "Could not parse JSON from response"}

        except TimeoutError as e:
            print(f"    ⏱️  Timeout: {e}")
            return {"error": "API call timed out"}
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return {"error": str(e)}

    def _detect_article_type(self, title: str) -> str:
        """Detect article type from title"""
        title_lower = title.lower()

        if 'review' in title_lower:
            return 'review'
        elif 'field test' in title_lower:
            return 'field_test'
        elif 'tested' in title_lower or 'test:' in title_lower:
            return 'test'
        elif 'news' in title_lower or 'announces' in title_lower or 'launches' in title_lower:
            return 'news'
        elif 'how to' in title_lower or 'guide' in title_lower:
            return 'how_to'
        elif 'tech' in title_lower or 'explained' in title_lower:
            return 'tech_feature'
        elif 'opinion' in title_lower or 'editorial' in title_lower:
            return 'opinion'
        else:
            return 'article'

    def process_article(self, article_id: str) -> Optional[Dict]:
        """Process a single article file"""
        article_file = self.articles_dir / f"{article_id}_full.json"

        if not article_file.exists():
            print(f"  ⚠️  Article not found: {article_id}")
            return None

        # Check if already processed
        insights_file = self.insights_dir / f"{article_id}_insights.json"
        if insights_file.exists():
            print(f"  ⚡ Using cached insights: {article_id}")
            with open(insights_file, 'r') as f:
                return json.load(f)

        # Load article
        with open(article_file, 'r') as f:
            article_data = json.load(f)

        # Extract insights
        insights = self.extract_insights(article_data)

        if 'error' not in insights:
            # Save insights
            with open(insights_file, 'w') as f:
                json.dump(insights, f, indent=2)
            print(f"    ✅ Insights saved")

        return insights

    def process_all_articles(self, limit: Optional[int] = None):
        """Process all articles in the directory"""
        import time

        article_files = list(self.articles_dir.glob("*_full.json"))

        if limit:
            article_files = article_files[:limit]

        print(f"\n{'='*70}")
        print(f"🚴 PINKBIKE INTELLIGENCE EXTRACTION")
        print(f"{'='*70}\n")
        print(f"Total articles: {len(article_files)}\n")

        # Check how many are already cached
        cached_count = sum(1 for af in article_files
                          if (self.insights_dir / f"{af.stem.replace('_full', '')}_insights.json").exists())
        print(f"Already processed (cached): {cached_count}")
        print(f"To process: {len(article_files) - cached_count}\n")
        print(f"⏱️  Estimated time: {(len(article_files) - cached_count) * 20} seconds\n")

        results = {"success": 0, "errors": 0, "cached": 0}
        start_time = time.time()

        for i, article_file in enumerate(article_files, 1):
            article_id = article_file.stem.replace("_full", "")

            # Check if cached
            insights_file = self.insights_dir / f"{article_id}_insights.json"
            is_cached = insights_file.exists()

            elapsed = time.time() - start_time
            avg_time = elapsed / i if i > 0 else 0
            remaining = (len(article_files) - i) * avg_time

            status = "⚡" if is_cached else "🔄"
            print(f"{status} [{i}/{len(article_files)}] {article_id[:50]} (avg: {avg_time:.1f}s, eta: {remaining:.0f}s)")

            try:
                insights = self.process_article(article_id)

                if insights:
                    if 'error' in insights:
                        results['errors'] += 1
                    elif is_cached:
                        results['cached'] += 1
                    else:
                        results['success'] += 1
                else:
                    results['errors'] += 1
            except Exception as e:
                print(f"    ❌ Exception: {e}")
                results['errors'] += 1

        total_time = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"✅ EXTRACTION COMPLETE")
        print(f"{'='*70}")
        print(f"Success: {results['success']}")
        print(f"Cached: {results['cached']}")
        print(f"Errors: {results['errors']}")
        print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"{'='*70}\n")

        return results


def main():
    import sys

    extractor = PinkbikeIntelligenceExtractor()

    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            extractor.process_all_articles(limit=limit)
        else:
            article_id = sys.argv[1]
            insights = extractor.process_article(article_id)
            if insights:
                print(json.dumps(insights, indent=2))
    else:
        print("Usage:")
        print("  Process single article: python3 pinkbike_intelligence_extractor.py ARTICLE_ID")
        print("  Process all: python3 pinkbike_intelligence_extractor.py all")
        print("  Process N articles: python3 pinkbike_intelligence_extractor.py all 5")


if __name__ == "__main__":
    main()

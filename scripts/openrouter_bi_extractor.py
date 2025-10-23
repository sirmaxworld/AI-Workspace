#!/usr/bin/env python3
"""
OpenRouter Business Intelligence Extractor
Parallel insights extraction using OpenRouter API (no Browserbase limits)
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Optional
import requests
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')


class OpenRouterBIExtractor:
    """Extract business intelligence using OpenRouter (Claude/Gemini)"""

    def __init__(self, model="anthropic/claude-sonnet-4"):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = model  # Options: anthropic/claude-sonnet-4, anthropic/claude-3.5-haiku
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.transcripts_dir = self.workspace_dir / "data" / "transcripts"
        self.insights_dir = self.workspace_dir / "data" / "business_insights"
        self.insights_dir.mkdir(parents=True, exist_ok=True)

    def extract_insights(self, transcript_data: Dict) -> Dict:
        """
        Extract comprehensive business intelligence from transcript via OpenRouter
        """
        video_id = transcript_data.get('video_id')
        title = transcript_data.get('title', '')

        # Get full transcript text
        segments = transcript_data.get('transcript', {}).get('segments', [])
        full_text = " ".join([seg.get('text', '') for seg in segments])

        if not full_text or len(full_text) < 500:
            return {"error": "Transcript too short for analysis"}

        # Get comments data
        comments_data = transcript_data.get('comments', {})
        top_comments = comments_data.get('top_comments', [])
        has_comments = len(top_comments) > 0

        print(f"  🧠 [OpenRouter] Analyzing: {title[:60]}...")
        if has_comments:
            print(f"    💬 Including {len(top_comments)} comments in analysis")

        # Build comments section for prompt
        comments_section = ""
        if has_comments:
            comments_text = "\n".join([
                f"- [{c['likes']} likes] @{c['author']}: {c['text'][:200]}"
                for c in top_comments[:15]
            ])
            comments_section = f"""

VIEWER COMMENTS (Top comments sorted by engagement):
{comments_text}
"""

        # Create comprehensive extraction prompt
        prompt = f"""Analyze this business/entrepreneurship video transcript and viewer comments to extract structured business intelligence.

VIDEO: {title}

TRANSCRIPT (first 8000 chars):
{full_text[:8000]}{comments_section}

Extract and structure the following information in JSON format:

{{
  "market_intelligence": {{
    "target_markets": [
      {{
        "market_description": "who is the target customer",
        "demographics": ["age", "income", "profession"],
        "pain_points": ["specific pain point 1", "pain point 2"],
        "market_size_indicators": "any mentions of market size or opportunity"
      }}
    ],
    "problems_validated": [
      {{
        "problem": "clear problem statement",
        "severity": "how painful is this problem",
        "current_solutions": "what people are currently using",
        "market_gap": "why current solutions fail"
      }}
    ]
  }},

  "products_tools": [
    {{
      "name": "product/tool name",
      "category": "saas/ai-tool/mobile-app/service",
      "use_case": "what problem it solves",
      "sentiment": "positive/negative/neutral/recommended",
      "pricing": "any pricing info mentioned",
      "metrics": "revenue/users/growth mentioned"
    }}
  ],

  "business_strategies": [
    {{
      "strategy_type": "monetization/growth/operations",
      "strategy": "specific strategy explained",
      "implementation": "how to implement (if explained)",
      "expected_results": "outcomes mentioned",
      "case_study": "real example if provided"
    }}
  ],

  "problems_solutions": [
    {{
      "problem": "specific problem discussed",
      "category": "technical/business/marketing/product",
      "solution": "solution provided",
      "steps": ["step 1", "step 2"],
      "tools_needed": ["tool 1", "tool 2"],
      "difficulty": "beginner/intermediate/advanced",
      "time_estimate": "if mentioned"
    }}
  ],

  "startup_ideas": [
    {{
      "idea": "startup idea description",
      "target_market": "who would use this",
      "problem_solved": "what pain point it addresses",
      "business_model": "how it makes money",
      "validation": "how to validate this idea",
      "investment_needed": "if mentioned"
    }}
  ],

  "mistakes_to_avoid": [
    {{
      "mistake": "what mistake is discussed",
      "consequences": "what happens if you make this mistake",
      "prevention": "how to avoid it",
      "example": "real example if shared"
    }}
  ],

  "growth_tactics": [
    {{
      "channel": "seo/paid-ads/content/viral/community",
      "tactic": "specific tactic explained",
      "steps": ["actionable steps"],
      "cost_estimate": "if mentioned",
      "results_expected": "expected outcomes"
    }}
  ],

  "ai_workflows": [
    {{
      "workflow_name": "name of the AI workflow",
      "tools_used": ["tool 1", "tool 2"],
      "steps": ["step-by-step process"],
      "automation_level": "manual/semi-automated/fully-automated",
      "use_case": "what problem it solves"
    }}
  ],

  "metrics_kpis": [
    {{
      "metric": "metric name",
      "benchmark": "what's considered good",
      "tracking_method": "how to track it",
      "optimization_tip": "how to improve it"
    }}
  ],

  "trends_signals": [
    {{
      "trend": "emerging trend described",
      "category": "technology/market/consumer-behavior",
      "stage": "early/growing/mainstream",
      "opportunity": "what opportunity this creates"
    }}
  ],

  "actionable_quotes": [
    {{
      "quote": "exact quote",
      "context": "context around the quote",
      "category": "strategy/mindset/tactical",
      "actionability": "what action this inspires"
    }}
  ],

  "key_statistics": [
    {{
      "statistic": "the stat (e.g., '80% of startups fail')",
      "context": "context provided",
      "source_reliability": "claimed/verified/estimated"
    }}
  ],

  "comment_insights": [
    {{
      "type": "problem/use_case/validation/feedback/trend",
      "insight": "What insight this comment reveals about the market/product/audience",
      "evidence": "The actual comment text (truncated if long)",
      "engagement": 0,
      "author": "@username",
      "relevance": "Why this comment is valuable for business intelligence"
    }}
  ],

  "top_validated_comments": [
    {{
      "comment": "High-engagement comment text",
      "likes": 0,
      "author": "@username",
      "insight_type": "market_validation/pain_point/use_case/trend_signal",
      "business_value": "What this tells us about the market/audience"
    }}
  ],

  "comment_derived_trends": [
    {{
      "trend": "Pattern or theme across multiple comments",
      "supporting_comments": ["comment 1", "comment 2"],
      "frequency": "how many comments mention this",
      "business_implication": "what opportunity this reveals"
    }}
  ]
}}

IMPORTANT:
- Only include items that are ACTUALLY discussed in the transcript
- Be specific and detailed
- Include real numbers and metrics when mentioned
- Focus on actionable, searchable information
- Return valid JSON only
"""

        try:
            start_time = time.time()

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 4000,
                    "temperature": 0.1
                },
                timeout=60
            )

            elapsed = time.time() - start_time
            print(f"    ⏱️  OpenRouter API call: {elapsed:.1f}s")

            if response.status_code != 200:
                return {"error": f"OpenRouter API error: {response.status_code} - {response.text}"}

            result = response.json()
            response_text = result['choices'][0]['message']['content']

            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())

                # Add metadata
                insights['meta'] = {
                    'video_id': video_id,
                    'title': title,
                    'extracted_at': __import__('datetime').datetime.now().isoformat(),
                    'model': f"openrouter/{self.model}",
                    'transcript_length': len(full_text),
                    'processing_time_seconds': elapsed
                }

                return insights
            else:
                return {"error": "Could not parse JSON from response"}

        except Exception as e:
            print(f"    ❌ OpenRouter Error: {e}")
            return {"error": str(e)}

    def process_transcript(self, video_id: str) -> Optional[Dict]:
        """Process a single transcript file"""
        transcript_file = self.transcripts_dir / f"{video_id}_full.json"

        if not transcript_file.exists():
            print(f"  ⚠️  Transcript not found: {video_id}")
            return None

        # Check if already processed
        insights_file = self.insights_dir / f"{video_id}_insights.json"
        if insights_file.exists():
            print(f"  ⚡ Using cached insights: {video_id}")
            with open(insights_file, 'r') as f:
                return json.load(f)

        # Load transcript
        with open(transcript_file, 'r') as f:
            transcript_data = json.load(f)

        # Extract insights
        insights = self.extract_insights(transcript_data)

        if 'error' not in insights:
            # Save insights
            with open(insights_file, 'w') as f:
                json.dump(insights, f, indent=2)
            print(f"    ✅ Insights saved via OpenRouter")

        return insights


def main():
    import sys

    extractor = OpenRouterBIExtractor()

    if len(sys.argv) > 1:
        video_id = sys.argv[1]
        insights = extractor.process_transcript(video_id)
        if insights:
            print(json.dumps(insights, indent=2))
    else:
        print("Usage:")
        print("  Process single video: python3 openrouter_bi_extractor.py VIDEO_ID")


if __name__ == "__main__":
    main()

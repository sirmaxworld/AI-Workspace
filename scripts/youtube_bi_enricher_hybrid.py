#!/usr/bin/env python3
"""
YouTube BI Enricher - Hybrid Model Approach
80% Gemini 2.0 Flash (cost optimization) + 20% Claude Sonnet 4 (quality)
Applies existing BI enrichment schema
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from anthropic import Anthropic
from openai import OpenAI

load_dotenv('/Users/yourox/AI-Workspace/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeBIEnricherHybrid:
    """Hybrid enrichment using Gemini Flash (80%) + Claude Sonnet 4 (20%)"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.transcripts_dir = self.workspace_dir / "data" / "transcripts"
        self.insights_dir = self.workspace_dir / "data" / "business_insights"
        self.insights_dir.mkdir(parents=True, exist_ok=True)

        # Load BI schema
        schema_file = self.workspace_dir / "config" / "business_intelligence_schema.json"
        with open(schema_file, 'r') as f:
            self.bi_schema = json.load(f)

        # Initialize clients
        self.claude_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.gemini_client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )

        self.claude_model = "claude-sonnet-4-20250514"
        self.gemini_model = "google/gemini-2.0-flash-001"

        # Pricing (per 1M tokens)
        self.claude_pricing = {"input": 3.0, "output": 15.0}
        self.gemini_pricing = {"input": 0.075, "output": 0.30}

        self.stats = {
            "claude": {"success": 0, "error": 0, "cost": 0.0},
            "gemini": {"success": 0, "error": 0, "cost": 0.0}
        }

        logger.info(f"✓ Hybrid BI Enricher initialized")
        logger.info(f"✓ Claude: {self.claude_model}")
        logger.info(f"✓ Gemini: {self.gemini_model}")

    def load_transcript(self, video_id: str) -> Optional[Dict]:
        """Load transcript from file"""
        transcript_file = self.transcripts_dir / f"{video_id}_full.json"

        if not transcript_file.exists():
            return None

        try:
            with open(transcript_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading transcript {video_id}: {e}")
            return None

    def build_extraction_prompt(self, transcript: Dict) -> str:
        """Build BI extraction prompt from transcript"""

        title = transcript.get('metadata', {}).get('title', 'Unknown')
        channel = transcript.get('metadata', {}).get('channel', 'Unknown')

        # Get transcript text
        transcript_data = transcript.get('transcript', {})
        segments = transcript_data.get('segments', [])

        # Combine segments into full text (limit to ~8000 words for context)
        transcript_text = " ".join([seg.get('text', '') for seg in segments[:500]])

        prompt = f"""Analyze this YouTube video transcript and extract comprehensive business intelligence.

VIDEO METADATA:
Title: {title}
Channel: {channel}

TRANSCRIPT:
{transcript_text}

Extract the following business intelligence in JSON format:

{{
  "products_tools": [
    {{
      "product_name": "string",
      "category": "saas|mobile_app|ai_tool|service|physical_product",
      "sentiment": "positive|negative|neutral|recommended|cautioned",
      "use_case": "string",
      "pricing_mentioned": "string or null",
      "metrics_shared": {{"revenue": "string or null", "users": "string or null", "growth_rate": "string or null"}}
    }}
  ],
  "business_strategies": [
    {{
      "strategy_type": "monetization|growth|operations",
      "description": "string",
      "revenue_model": "saas|ads|marketplace|affiliate|sponsorship|freemium|other",
      "tactics_explained": ["step 1", "step 2"],
      "expected_results": "string",
      "difficulty": "beginner|intermediate|advanced",
      "case_study_mentioned": "company name or null"
    }}
  ],
  "problems_solutions": [
    {{
      "problem_statement": "string",
      "category": "technical|business|marketing|product|operational",
      "severity": "critical|major|minor",
      "solution_description": "string",
      "implementation_steps": ["step 1", "step 2"],
      "tools_required": ["tool 1", "tool 2"],
      "cost_estimate": "string or null",
      "time_to_implement": "string or null"
    }}
  ],
  "startup_ideas": [
    {{
      "idea_description": "string",
      "target_market": "string",
      "problem_solved": "string",
      "business_model": "string",
      "estimated_investment": "string or null",
      "potential_revenue": "string or null"
    }}
  ],
  "growth_tactics": [
    {{
      "tactic_name": "string",
      "channel": "seo|paid_ads|content|partnerships|viral|community|referral|other",
      "description": "string",
      "steps": ["step 1", "step 2"],
      "cost_estimate": "string or null",
      "timeframe": "string or null",
      "expected_results": "string"
    }}
  ],
  "ai_workflows": [
    {{
      "workflow_name": "string",
      "tools_used": ["tool 1", "tool 2"],
      "steps": ["step 1", "step 2"],
      "automation_level": "manual|semi_automated|fully_automated",
      "use_case": "string",
      "results": "string or null"
    }}
  ],
  "trends_signals": [
    {{
      "trend_description": "string",
      "category": "technology|business_model|market|consumer_behavior",
      "stage": "early|growing|mainstream|declining",
      "opportunity_level": "high|medium|low",
      "timeframe": "string or null"
    }}
  ],
  "actionable_quotes": [
    {{
      "quote": "exact quote from video",
      "speaker": "speaker name",
      "context": "why this is important",
      "category": "strategy|mindset|tactical|inspirational"
    }}
  ],
  "key_statistics": [
    {{
      "statistic": "specific number or metric",
      "context": "what it means",
      "source": "where it came from",
      "verification_status": "verified|claimed|estimated"
    }}
  ],
  "mistakes_to_avoid": [
    {{
      "mistake_description": "string",
      "consequences": "string",
      "prevention": "how to avoid it",
      "real_examples": "string or null"
    }}
  ]
}}

IMPORTANT:
- Only extract insights that are EXPLICITLY mentioned in the transcript
- Provide actionable, specific information (not generic advice)
- Include concrete numbers, metrics, and examples when available
- If a category has no relevant insights, use an empty array []
- Focus on practical, implementable intelligence
- Be concise but comprehensive

Return ONLY valid JSON, no additional text."""

        return prompt

    def enrich_with_claude(self, video_id: str, transcript: Dict) -> Dict:
        """Enrich using Claude Sonnet 4 (high quality)"""
        try:
            prompt = self.build_extraction_prompt(transcript)

            response = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=4000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            insights_json = response.content[0].text

            # Claude might wrap in markdown
            if "```json" in insights_json:
                insights_json = insights_json.split("```json")[1].split("```")[0].strip()
            elif "```" in insights_json:
                insights_json = insights_json.split("```")[1].split("```")[0].strip()

            insights = json.loads(insights_json)

            # Calculate cost
            usage = response.usage
            cost = (usage.input_tokens / 1_000_000 * self.claude_pricing["input"]) + \
                   (usage.output_tokens / 1_000_000 * self.claude_pricing["output"])

            self.stats["claude"]["success"] += 1
            self.stats["claude"]["cost"] += cost

            return {
                "status": "success",
                "model": self.claude_model,
                **insights,
                "meta": {
                    "video_id": video_id,
                    "title": transcript.get('metadata', {}).get('title', ''),
                    "channel": transcript.get('metadata', {}).get('channel', ''),
                    "extracted_at": datetime.now().isoformat(),
                    "model_used": self.claude_model,
                    "tokens": {"input": usage.input_tokens, "output": usage.output_tokens},
                    "cost": round(cost, 6)
                }
            }

        except Exception as e:
            self.stats["claude"]["error"] += 1
            logger.error(f"[CLAUDE] Error enriching {video_id}: {str(e)[:150]}")
            return {
                "status": "error",
                "model": self.claude_model,
                "error": str(e)[:200]
            }

    def enrich_with_gemini(self, video_id: str, transcript: Dict) -> Dict:
        """Enrich using Gemini 2.0 Flash (cost optimized)"""
        try:
            prompt = self.build_extraction_prompt(transcript)

            response = self.gemini_client.chat.completions.create(
                model=self.gemini_model,
                messages=[
                    {"role": "system", "content": "You are a business intelligence analyst. Extract actionable insights from video transcripts. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            insights_json = response.choices[0].message.content
            insights = json.loads(insights_json)

            # Calculate cost
            usage = response.usage
            cost = (usage.prompt_tokens / 1_000_000 * self.gemini_pricing["input"]) + \
                   (usage.completion_tokens / 1_000_000 * self.gemini_pricing["output"])

            self.stats["gemini"]["success"] += 1
            self.stats["gemini"]["cost"] += cost

            return {
                "status": "success",
                "model": self.gemini_model,
                **insights,
                "meta": {
                    "video_id": video_id,
                    "title": transcript.get('metadata', {}).get('title', ''),
                    "channel": transcript.get('metadata', {}).get('channel', ''),
                    "extracted_at": datetime.now().isoformat(),
                    "model_used": self.gemini_model,
                    "tokens": {"input": usage.prompt_tokens, "output": usage.completion_tokens},
                    "cost": round(cost, 6)
                }
            }

        except Exception as e:
            self.stats["gemini"]["error"] += 1
            logger.error(f"[GEMINI] Error enriching {video_id}: {str(e)[:150]}")
            return {
                "status": "error",
                "model": self.gemini_model,
                "error": str(e)[:200]
            }

    def save_insights(self, video_id: str, insights: Dict):
        """Save insights to file"""
        output_file = self.insights_dir / f"{video_id}_insights.json"

        with open(output_file, 'w') as f:
            json.dump(insights, f, indent=2)

    def enrich_video(self, video_id: str, use_claude: bool = False) -> Dict:
        """Enrich a single video with specified model"""

        # Check if already exists
        output_file = self.insights_dir / f"{video_id}_insights.json"
        if output_file.exists():
            logger.info(f"[{video_id}] Already enriched, skipping")
            return {"status": "skipped", "reason": "already_exists"}

        # Load transcript
        transcript = self.load_transcript(video_id)
        if not transcript:
            return {"status": "skipped", "reason": "no_transcript"}

        # Enrich with appropriate model
        if use_claude:
            insights = self.enrich_with_claude(video_id, transcript)
        else:
            insights = self.enrich_with_gemini(video_id, transcript)

        # Save if successful
        if insights.get('status') == 'success':
            self.save_insights(video_id, insights)

        return insights

    def run_hybrid(
        self,
        video_ids: List[str],
        top_percent_claude: int = 20,
        workers: int = 50
    ):
        """
        Run hybrid enrichment

        Args:
            video_ids: List of video IDs (should be priority-ranked)
            top_percent_claude: Percentage of top videos to use Claude for
            workers: Concurrent workers (mostly for Gemini)
        """
        total = len(video_ids)
        claude_count = max(1, int(total * (top_percent_claude / 100)))

        # Split videos
        claude_videos = video_ids[:claude_count]
        gemini_videos = video_ids[claude_count:]

        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 HYBRID BI ENRICHMENT")
        logger.info(f"{'='*70}")
        logger.info(f"Total videos: {total}")
        logger.info(f"Claude Sonnet 4: {len(claude_videos)} videos (top {top_percent_claude}%)")
        logger.info(f"Gemini Flash: {len(gemini_videos)} videos ({100-top_percent_claude}%)")
        logger.info(f"Workers: {workers} (Gemini parallel)")
        logger.info(f"{'='*70}\n")

        start_time = time.time()

        # Process Claude videos first (sequential for quality)
        logger.info(f"🎯 Processing top {len(claude_videos)} videos with Claude Sonnet 4...\n")
        for i, video_id in enumerate(claude_videos, 1):
            logger.info(f"[{i}/{len(claude_videos)}] {video_id} (Claude)")
            self.enrich_video(video_id, use_claude=True)
            time.sleep(0.5)  # Rate limiting

        # Process Gemini videos in parallel
        logger.info(f"\n⚡ Processing {len(gemini_videos)} videos with Gemini Flash (parallel)...\n")

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self.enrich_video, video_id, False): video_id
                for video_id in gemini_videos
            }

            completed = 0
            for future in as_completed(futures):
                completed += 1
                video_id = futures[future]

                try:
                    result = future.result()
                    status = result.get('status', 'unknown')

                    if completed % 20 == 0 or completed == len(gemini_videos):
                        elapsed = time.time() - start_time
                        rate = completed / elapsed
                        remaining = (len(gemini_videos) - completed) / rate if rate > 0 else 0

                        logger.info(
                            f"[{completed}/{len(gemini_videos)}] {completed/len(gemini_videos)*100:.1f}% | "
                            f"Rate: {rate:.1f}/s | ETA: {remaining/60:.1f}m | "
                            f"✓{self.stats['gemini']['success']} ✗{self.stats['gemini']['error']}"
                        )

                except Exception as e:
                    logger.error(f"Error processing {video_id}: {e}")

        total_time = time.time() - start_time

        # Print summary
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ HYBRID ENRICHMENT COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Claude Sonnet 4:")
        logger.info(f"  Success: {self.stats['claude']['success']}")
        logger.info(f"  Errors: {self.stats['claude']['error']}")
        logger.info(f"  Cost: ${self.stats['claude']['cost']:.4f}")
        logger.info(f"\nGemini 2.0 Flash:")
        logger.info(f"  Success: {self.stats['gemini']['success']}")
        logger.info(f"  Errors: {self.stats['gemini']['error']}")
        logger.info(f"  Cost: ${self.stats['gemini']['cost']:.4f}")
        logger.info(f"\nTotals:")
        logger.info(f"  Total cost: ${self.stats['claude']['cost'] + self.stats['gemini']['cost']:.4f}")
        logger.info(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        logger.info(f"  Avg cost/video: ${(self.stats['claude']['cost'] + self.stats['gemini']['cost'])/total:.6f}")
        logger.info(f"{'='*70}\n")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Hybrid BI Enrichment for YouTube Videos')
    parser.add_argument('--video-ids-file', required=True, help='JSON file with ranked video IDs')
    parser.add_argument('--top-claude', type=int, default=20, help='Percentage of top videos for Claude (default: 20)')
    parser.add_argument('--workers', type=int, default=50, help='Concurrent workers for Gemini (default: 50)')

    args = parser.parse_args()

    # Load video IDs
    with open(args.video_ids_file, 'r') as f:
        data = json.load(f)

    # Extract video IDs (format depends on input file structure)
    if 'videos' in data:
        video_ids = [v['id'] for v in data['videos']]
    elif 'channels' in data:
        # Combined ranking file
        video_ids = []
        for channel in data['channels']:
            video_ids.extend([v['id'] for v in channel['videos']])
    else:
        # Assume it's a list of IDs
        video_ids = data

    logger.info(f"Loaded {len(video_ids)} video IDs")

    enricher = YouTubeBIEnricherHybrid()
    enricher.run_hybrid(video_ids, args.top_claude, args.workers)


if __name__ == "__main__":
    main()

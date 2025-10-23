#!/usr/bin/env python3
"""
YouTube BI Enricher - Demo Quality Comparison
Test 10 videos with Claude, Gemini, and GPT-4o to compare quality and costs
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv

from anthropic import Anthropic
from openai import OpenAI

load_dotenv('/Users/yourox/AI-Workspace/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeBIEnricherDemo:
    """Demo enricher to compare models"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.transcripts_dir = self.workspace_dir / "data" / "transcripts"
        self.demo_dir = self.workspace_dir / "data" / "demo_enrichment"
        self.demo_dir.mkdir(parents=True, exist_ok=True)

        # Initialize clients
        self.claude_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.gemini_client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )

        # Models
        self.models = {
            "claude": {
                "name": "claude-sonnet-4-20250514",
                "pricing": {"input": 3.0, "output": 15.0}
            },
            "gpt4o": {
                "name": "gpt-4o",
                "pricing": {"input": 2.5, "output": 10.0}
            },
            "gemini": {
                "name": "google/gemini-2.0-flash-001",
                "pricing": {"input": 0.075, "output": 0.30}
            }
        }

        self.results = {model: {"success": 0, "error": 0, "cost": 0.0, "insights": []}
                       for model in self.models.keys()}

    def load_transcript(self, video_id: str) -> Dict:
        """Load transcript"""
        transcript_file = self.transcripts_dir / f"{video_id}_full.json"

        with open(transcript_file, 'r') as f:
            return json.load(f)

    def build_prompt(self, transcript: Dict) -> str:
        """Build extraction prompt"""
        title = transcript.get('metadata', {}).get('title', 'Unknown')
        segments = transcript.get('transcript', {}).get('segments', [])
        transcript_text = " ".join([seg.get('text', '') for seg in segments[:500]])

        return f"""Extract business intelligence from this video transcript in JSON format:

TITLE: {title}

TRANSCRIPT:
{transcript_text}

Extract these categories (use empty arrays if nothing found):

{{
  "products_tools": [list products/tools mentioned with use cases],
  "business_strategies": [monetization, growth, operations strategies],
  "problems_solutions": [problems + concrete solutions with steps],
  "startup_ideas": [specific startup ideas discussed],
  "growth_tactics": [acquisition channels and tactics],
  "ai_workflows": [AI automation workflows],
  "trends_signals": [emerging trends and opportunities],
  "actionable_quotes": [powerful quotes with context],
  "key_statistics": [specific numbers and metrics],
  "mistakes_to_avoid": [common mistakes warned against]
}}

Be specific, actionable, and include real examples when mentioned."""

    def enrich_with_claude(self, video_id: str, transcript: Dict) -> Dict:
        """Enrich with Claude"""
        try:
            prompt = self.build_prompt(transcript)

            response = self.claude_client.messages.create(
                model=self.models["claude"]["name"],
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            insights_json = response.content[0].text

            if "```json" in insights_json:
                insights_json = insights_json.split("```json")[1].split("```")[0].strip()

            insights = json.loads(insights_json)

            usage = response.usage
            cost = (usage.input_tokens / 1_000_000 * self.models["claude"]["pricing"]["input"]) + \
                   (usage.output_tokens / 1_000_000 * self.models["claude"]["pricing"]["output"])

            self.results["claude"]["success"] += 1
            self.results["claude"]["cost"] += cost

            return {
                "status": "success",
                "model": "claude",
                **insights,
                "meta": {
                    "video_id": video_id,
                    "tokens": {"input": usage.input_tokens, "output": usage.output_tokens},
                    "cost": round(cost, 6)
                }
            }

        except Exception as e:
            self.results["claude"]["error"] += 1
            logger.error(f"Claude error on {video_id}: {e}")
            return {"status": "error", "model": "claude", "error": str(e)}

    def enrich_with_gpt4o(self, video_id: str, transcript: Dict) -> Dict:
        """Enrich with GPT-4o"""
        try:
            prompt = self.build_prompt(transcript)

            response = self.openai_client.chat.completions.create(
                model=self.models["gpt4o"]["name"],
                messages=[
                    {"role": "system", "content": "You are a business intelligence analyst. Extract actionable insights from video transcripts in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            insights_json = response.choices[0].message.content
            insights = json.loads(insights_json)

            usage = response.usage
            cost = (usage.prompt_tokens / 1_000_000 * self.models["gpt4o"]["pricing"]["input"]) + \
                   (usage.completion_tokens / 1_000_000 * self.models["gpt4o"]["pricing"]["output"])

            self.results["gpt4o"]["success"] += 1
            self.results["gpt4o"]["cost"] += cost

            return {
                "status": "success",
                "model": "gpt4o",
                **insights,
                "meta": {
                    "video_id": video_id,
                    "tokens": {"input": usage.prompt_tokens, "output": usage.completion_tokens},
                    "cost": round(cost, 6)
                }
            }

        except Exception as e:
            self.results["gpt4o"]["error"] += 1
            logger.error(f"GPT-4o error on {video_id}: {e}")
            return {"status": "error", "model": "gpt4o", "error": str(e)}

    def enrich_with_gemini(self, video_id: str, transcript: Dict) -> Dict:
        """Enrich with Gemini"""
        try:
            prompt = self.build_prompt(transcript)

            response = self.gemini_client.chat.completions.create(
                model=self.models["gemini"]["name"],
                messages=[
                    {"role": "system", "content": "You are a business intelligence analyst. Extract actionable insights from video transcripts in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            insights_json = response.choices[0].message.content
            insights = json.loads(insights_json)

            usage = response.usage
            cost = (usage.prompt_tokens / 1_000_000 * self.models["gemini"]["pricing"]["input"]) + \
                   (usage.completion_tokens / 1_000_000 * self.models["gemini"]["pricing"]["output"])

            self.results["gemini"]["success"] += 1
            self.results["gemini"]["cost"] += cost

            return {
                "status": "success",
                "model": "gemini",
                **insights,
                "meta": {
                    "video_id": video_id,
                    "tokens": {"input": usage.prompt_tokens, "output": usage.completion_tokens},
                    "cost": round(cost, 6)
                }
            }

        except Exception as e:
            self.results["gemini"]["error"] += 1
            logger.error(f"Gemini error on {video_id}: {e}")
            return {"status": "error", "model": "gemini", "error": str(e)}

    def run_demo(self, video_ids: List[str]):
        """Run demo comparison on video list"""
        logger.info(f"\n{'='*70}")
        logger.info(f"🧪 BI ENRICHMENT DEMO - MODEL COMPARISON")
        logger.info(f"{'='*70}")
        logger.info(f"Videos to test: {len(video_ids)}")
        logger.info(f"Models: Claude Sonnet 4, GPT-4o, Gemini 2.0 Flash")
        logger.info(f"{'='*70}\n")

        for i, video_id in enumerate(video_ids, 1):
            logger.info(f"\n[{i}/{len(video_ids)}] Processing {video_id}")

            transcript = self.load_transcript(video_id)

            # Test with all 3 models
            logger.info("  Testing Claude Sonnet 4...")
            claude_result = self.enrich_with_claude(video_id, transcript)
            time.sleep(1)

            logger.info("  Testing GPT-4o...")
            gpt4o_result = self.enrich_with_gpt4o(video_id, transcript)
            time.sleep(1)

            logger.info("  Testing Gemini 2.0 Flash...")
            gemini_result = self.enrich_with_gemini(video_id, transcript)

            # Save results
            self.results["claude"]["insights"].append(claude_result)
            self.results["gpt4o"]["insights"].append(gpt4o_result)
            self.results["gemini"]["insights"].append(gemini_result)

            # Save individual comparison
            comparison = {
                "video_id": video_id,
                "title": transcript.get('metadata', {}).get('title', ''),
                "claude": claude_result,
                "gpt4o": gpt4o_result,
                "gemini": gemini_result
            }

            comparison_file = self.demo_dir / f"{video_id}_comparison.json"
            with open(comparison_file, 'w') as f:
                json.dump(comparison, f, indent=2)

            logger.info(f"  ✓ Comparison saved to {comparison_file.name}")

        self.generate_report()

    def generate_report(self):
        """Generate comparison report"""
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 DEMO RESULTS SUMMARY")
        logger.info(f"{'='*70}\n")

        for model_name, model_results in self.results.items():
            logger.info(f"{model_name.upper()}:")
            logger.info(f"  Success: {model_results['success']}")
            logger.info(f"  Errors: {model_results['error']}")
            logger.info(f"  Total cost: ${model_results['cost']:.4f}")
            logger.info(f"  Avg cost/video: ${model_results['cost']/max(model_results['success'],1):.6f}\n")

        # Generate detailed report
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                model: {
                    "success_count": self.results[model]["success"],
                    "error_count": self.results[model]["error"],
                    "total_cost": round(self.results[model]["cost"], 6),
                    "avg_cost_per_video": round(self.results[model]["cost"]/max(self.results[model]["success"], 1), 6)
                }
                for model in self.models.keys()
            },
            "detailed_results": self.results
        }

        report_file = self.demo_dir / "demo_comparison_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📋 Full report saved to: {report_file}")
        logger.info(f"{'='*70}\n")

        return report


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Demo BI Enrichment - Model Comparison')
    parser.add_argument('video_ids', nargs='+', help='Video IDs to test (10 recommended)')

    args = parser.parse_args()

    demo = YouTubeBIEnricherDemo()
    demo.run_demo(args.video_ids)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Production Gemini 2.0 Flash Enrichment - Maximum Speed
95%+ cost savings vs Claude Sonnet 4
"""

import json
import time
import logging
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeminiFlashProduction:
    """Production Gemini 2.0 Flash enrichment - ultra-fast, ultra-cheap"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.enriched_dir = self.workspace_dir / "data" / "yc_enriched"
        self.companies_file = self.workspace_dir / "data" / "yc_companies" / "all_companies.json"

        # Initialize OpenRouter client
        self.client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )

        self.model = "google/gemini-2.0-flash-001"

        logger.info(f"✓ Gemini Flash Production initialized")
        logger.info(f"✓ Model: {self.model}")

        self.stats = {"success": 0, "error": 0}

    def load_companies(self) -> Dict[str, Dict]:
        """Load all companies"""
        with open(self.companies_file, 'r') as f:
            companies = json.load(f)
        return {c['slug']: c for c in companies}

    def get_incomplete_companies(self) -> List[tuple]:
        """Get companies needing Phase 8"""
        all_companies = self.load_companies()
        incomplete = []

        for enriched_file in self.enriched_dir.glob("*_enriched.json"):
            try:
                with open(enriched_file, 'r') as f:
                    data = json.load(f)

                if not data.get('phase8_complete'):
                    slug = data.get('slug')
                    if slug in all_companies:
                        full_company = {**all_companies[slug], **data}
                        incomplete.append((slug, enriched_file, full_company))

            except Exception as e:
                logger.warning(f"Error reading {enriched_file}: {e}")

        logger.info(f"Found {len(incomplete)} companies needing enrichment")
        return incomplete

    def enrich_with_gemini(self, company: Dict) -> Dict:
        """Enrich using Gemini 2.0 Flash"""
        company_name = company.get('name', 'Unknown')

        try:
            context = self._build_context(company)
            prompt = self._build_prompt(context)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a startup analyst providing strategic insights on Y Combinator companies. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            insights_json = response.choices[0].message.content
            insights = json.loads(insights_json)

            usage = response.usage
            # Gemini 2.0 Flash pricing via OpenRouter: ~$0.075/$0.30 per 1M tokens
            cost = (usage.prompt_tokens / 1_000_000 * 0.075) + (usage.completion_tokens / 1_000_000 * 0.30)

            result = {
                "ai_insights_version": "1.0.0",
                "model_used": self.model,
                "enriched_at": datetime.now().isoformat(),
                "status": "success",
                **insights,
                "tokens_used": {
                    "prompt": usage.prompt_tokens,
                    "completion": usage.completion_tokens,
                    "total": usage.total_tokens,
                    "estimated_cost": round(cost, 6)
                }
            }

            self.stats["success"] += 1
            return result

        except Exception as e:
            self.stats["error"] += 1
            logger.error(f"[GEMINI] Error enriching {company_name}: {str(e)[:100]}")
            return {
                "ai_insights_version": "1.0.0",
                "model_used": self.model,
                "enriched_at": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)[:200]
            }

    def _build_context(self, company: Dict) -> str:
        """Build context from company data"""
        context_parts = [
            f"Company: {company.get('name')}",
            f"One-liner: {company.get('one_liner', 'N/A')}",
            f"Description: {company.get('long_description', 'N/A')[:500]}",
            f"Industry: {company.get('industry', 'N/A')}",
            f"Batch: {company.get('batch', 'N/A')}",
            f"Team Size: {company.get('team_size', 'N/A')}",
            f"Status: {company.get('status', 'N/A')}",
            f"Website: {company.get('website', 'N/A')}"
        ]

        web_data = company.get('web_data', {})
        if web_data:
            domain_info = web_data.get('domain_info', {})
            if domain_info.get('domain_age_years'):
                context_parts.append(f"Domain age: {domain_info['domain_age_years']} years")

        github_data = company.get('github_data', {})
        if github_data and github_data.get('status') != 'no_github_link':
            repos = github_data.get('repositories', {})
            if repos.get('total_stars'):
                context_parts.append(f"GitHub: {repos.get('total_repos', 0)} repos, {repos.get('total_stars', 0)} stars")

        return "\n".join(context_parts)

    def _build_prompt(self, context: str) -> str:
        """Build enrichment prompt"""
        return f"""Analyze this Y Combinator company and provide strategic insights:

{context}

Provide a structured analysis in JSON format with these fields:

{{
  "market_analysis": {{
    "market_size": "estimation (small/medium/large/very large)",
    "market_stage": "emerging/growing/mature/declining",
    "key_trends": ["trend 1", "trend 2", "trend 3"]
  }},
  "competitive_positioning": {{
    "competitive_moat": "description of moat (network effects, tech, etc)",
    "differentiation": "what makes them unique",
    "competitive_advantages": ["advantage 1", "advantage 2"],
    "competitive_vulnerabilities": ["vulnerability 1", "vulnerability 2"]
  }},
  "business_model": {{
    "revenue_model": "SaaS/marketplace/hardware/etc",
    "scalability": "high/medium/low",
    "capital_intensity": "high/medium/low"
  }},
  "growth_assessment": {{
    "growth_stage": "pre-seed/seed/series-a/growth/mature",
    "growth_indicators": ["indicator 1", "indicator 2"],
    "growth_bottlenecks": ["bottleneck 1", "bottleneck 2"]
  }},
  "risk_analysis": {{
    "market_risk": "high/medium/low",
    "technology_risk": "high/medium/low",
    "execution_risk": "high/medium/low",
    "overall_risk_score": 5,
    "key_risks": ["risk 1", "risk 2", "risk 3"]
  }},
  "investment_thesis": {{
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "concerns": ["concern 1", "concern 2"],
    "exit_potential": "IPO/acquisition/strategic",
    "comparable_companies": ["company 1", "company 2"]
  }},
  "recommendations": {{
    "next_steps": ["step 1", "step 2"],
    "expansion_opportunities": ["opportunity 1", "opportunity 2"]
  }}
}}

Respond ONLY with valid JSON. Be concise but insightful."""

    def run(self, workers: int = 200):
        """
        Run production enrichment with Gemini Flash

        Args:
            workers: Number of parallel workers (default 150 for max speed)
        """
        companies = self.get_incomplete_companies()
        total = len(companies)

        if total == 0:
            logger.info("✅ All companies already enriched!")
            return

        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 GEMINI FLASH PRODUCTION - MAXIMUM SPEED")
        logger.info(f"{'='*70}")
        logger.info(f"Total companies: {total}")
        logger.info(f"Workers: {workers}")
        logger.info(f"Model: {self.model}")
        logger.info(f"Expected cost: ${total * 0.00045:.2f}")
        logger.info(f"{'='*70}\n")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {}

            for slug, enriched_file, company in companies:
                future = executor.submit(self.enrich_with_gemini, company)
                futures[future] = (slug, enriched_file, company)

            completed = 0
            for future in as_completed(futures):
                completed += 1
                slug, enriched_file, company = futures[future]

                try:
                    ai_insights = future.result()

                    # Update enriched file
                    with open(enriched_file, 'r') as f:
                        enriched_data = json.load(f)

                    enriched_data['ai_insights'] = ai_insights
                    enriched_data['phase8_complete'] = (ai_insights.get('status') == 'success')

                    with open(enriched_file, 'w') as f:
                        json.dump(enriched_data, f, indent=2)

                    if completed % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed
                        remaining = (total - completed) / rate if rate > 0 else 0

                        logger.info(
                            f"[{completed}/{total}] {completed/total*100:.1f}% | "
                            f"Rate: {rate:.1f}/s | ETA: {remaining/60:.1f}m | "
                            f"Success: {self.stats['success']}✓ / Errors: {self.stats['error']}✗"
                        )

                except Exception as e:
                    logger.error(f"Error processing {company.get('name', slug)}: {e}")

        total_time = time.time() - start_time
        total_cost = self.stats['success'] * 0.00045

        logger.info(f"\n{'='*70}")
        logger.info(f"✅ GEMINI FLASH PRODUCTION COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Success: {self.stats['success']} / {total} ({self.stats['success']/total*100:.1f}%)")
        logger.info(f"Errors: {self.stats['error']}")
        logger.info(f"Total cost: ${total_cost:.2f}")
        logger.info(f"Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        logger.info(f"Rate: {total/total_time:.2f} companies/second")
        logger.info(f"\nSavings vs Claude Sonnet 4: ${total * 0.0102 - total_cost:.2f} (95.6%)")
        logger.info(f"Savings vs GPT-4o: ${total * 0.0044 - total_cost:.2f} (89.8%)")
        logger.info(f"{'='*70}\n")


if __name__ == "__main__":
    enricher = GeminiFlashProduction()
    # Run with 200 workers for maximum speed (optimized for remaining companies)
    enricher.run(workers=200)

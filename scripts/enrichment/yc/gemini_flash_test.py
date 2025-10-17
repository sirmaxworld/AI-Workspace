#!/usr/bin/env python3
"""
Test Gemini 2.0 Flash via OpenRouter for cost comparison
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


class GeminiFlashTest:
    """Test Gemini 2.0 Flash quality and cost via OpenRouter"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.enriched_dir = self.workspace_dir / "data" / "yc_enriched"
        self.companies_file = self.workspace_dir / "data" / "yc_companies" / "all_companies.json"

        # Initialize OpenRouter client (OpenAI-compatible)
        self.client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )

        # Gemini 2.0 Flash model on OpenRouter (paid - fast & super cheap)
        self.model = "google/gemini-2.0-flash-001"

        logger.info(f"✓ OpenRouter client initialized")
        logger.info(f"✓ Model: {self.model}")

        self.stats = {"success": 0, "error": 0}

    def load_companies(self) -> Dict[str, Dict]:
        """Load all companies"""
        with open(self.companies_file, 'r') as f:
            companies = json.load(f)
        return {c['slug']: c for c in companies}

    def get_test_companies(self, limit: int = 50) -> List[tuple]:
        """Get test companies needing Phase 8"""
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

                        if len(incomplete) >= limit:
                            break

            except Exception as e:
                logger.warning(f"Error reading {enriched_file}: {e}")

        logger.info(f"Selected {len(incomplete)} test companies")
        return incomplete

    def enrich_with_gemini(self, company: Dict) -> Dict:
        """Enrich using Gemini 2.0 Flash via OpenRouter"""
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
            # OpenRouter pricing for Gemini 2.0 Flash: ~$0.15/$0.60 per 1M tokens
            cost = (usage.prompt_tokens / 1_000_000 * 0.15) + (usage.completion_tokens / 1_000_000 * 0.60)

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
            logger.info(f"✓ {company_name} - Cost: ${cost:.6f}")
            return result

        except Exception as e:
            self.stats["error"] += 1
            logger.error(f"✗ {company_name}: {str(e)[:200]}")
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

    def run_test(self, test_size: int = 50, workers: int = 10):
        """
        Run test enrichment with Gemini Flash

        Args:
            test_size: Number of companies to test
            workers: Number of parallel workers
        """
        companies = self.get_test_companies(limit=test_size)
        total = len(companies)

        if total == 0:
            logger.info("No test companies found!")
            return

        logger.info(f"\n{'='*70}")
        logger.info(f"🧪 GEMINI 2.0 FLASH TEST VIA OPENROUTER")
        logger.info(f"{'='*70}")
        logger.info(f"Test size: {total} companies")
        logger.info(f"Workers: {workers}")
        logger.info(f"Model: {self.model}")
        logger.info(f"{'='*70}\n")

        start_time = time.time()
        results = []

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
                    results.append({
                        'slug': slug,
                        'name': company.get('name'),
                        'insights': ai_insights
                    })

                    if completed % 10 == 0 or completed == total:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0

                        logger.info(
                            f"[{completed}/{total}] {completed/total*100:.1f}% | "
                            f"Rate: {rate:.1f}/s | "
                            f"Success: {self.stats['success']}✓ / Errors: {self.stats['error']}✗"
                        )

                except Exception as e:
                    logger.error(f"Error processing {company.get('name', slug)}: {e}")

        total_time = time.time() - start_time

        # Calculate stats
        successful = [r for r in results if r['insights'].get('status') == 'success']
        total_cost = sum(r['insights']['tokens_used']['estimated_cost'] for r in successful)
        avg_cost = total_cost / len(successful) if successful else 0

        avg_tokens = sum(r['insights']['tokens_used']['total'] for r in successful) / len(successful) if successful else 0

        logger.info(f"\n{'='*70}")
        logger.info(f"✅ GEMINI FLASH TEST COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Success: {self.stats['success']} / {total} ({self.stats['success']/total*100:.1f}%)")
        logger.info(f"Errors: {self.stats['error']}")
        logger.info(f"Total cost: ${total_cost:.4f}")
        logger.info(f"Average cost/company: ${avg_cost:.6f}")
        logger.info(f"Average tokens: {int(avg_tokens)}")
        logger.info(f"Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        logger.info(f"Rate: {total/total_time:.2f} companies/second")
        logger.info(f"\nProjected cost for 5,488 companies: ${avg_cost * 5488:.2f}")
        logger.info(f"vs Claude Sonnet 4: ${0.0102 * 5488:.2f}")
        logger.info(f"Savings: ${(0.0102 - avg_cost) * 5488:.2f} ({((0.0102 - avg_cost) / 0.0102 * 100):.1f}%)")
        logger.info(f"{'='*70}\n")

        # Save sample results
        sample_file = self.workspace_dir / "data" / "gemini_flash_test_results.json"
        with open(sample_file, 'w') as f:
            json.dump(results[:5], f, indent=2)

        logger.info(f"Sample results saved to: {sample_file}")


if __name__ == "__main__":
    tester = GeminiFlashTest()
    # Test on 50 companies with 10 workers
    tester.run_test(test_size=50, workers=10)

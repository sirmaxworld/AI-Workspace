#!/usr/bin/env python3
"""
Dual-Key GPT-4o Enrichment
Uses both OpenAI API keys to double throughput for GPT-4o enrichment
Each key gets 500 RPM + 30K TPM = 1000 RPM total, 60K TPM total
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


class DualKeyEnricher:
    """Uses two OpenAI API keys to double throughput"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.enriched_dir = self.workspace_dir / "data" / "yc_enriched"
        self.companies_file = self.workspace_dir / "data" / "yc_companies" / "all_companies.json"

        # Initialize two OpenAI clients
        key1 = os.getenv('OPENAI_API_KEY')
        key2 = os.getenv('OPENAI_API_KEY2')

        if not key1 or not key2:
            raise ValueError("Both OPENAI_API_KEY and OPENAI_API_KEY2 required")

        self.client1 = OpenAI(api_key=key1)
        self.client2 = OpenAI(api_key=key2)
        self.model = "gpt-4o"

        logger.info(f"✓ Dual-key enricher initialized with {self.model}")
        logger.info(f"✓ Key 1: ...{key1[-6:]}")
        logger.info(f"✓ Key 2: ...{key2[-6:]}")

        self.stats = {"key1": {"success": 0, "error": 0}, "key2": {"success": 0, "error": 0}}

    def load_companies(self) -> Dict[str, Dict]:
        """Load all companies"""
        with open(self.companies_file, 'r') as f:
            companies = json.load(f)
        return {c['slug']: c for c in companies}

    def get_failed_companies(self) -> List[tuple]:
        """Get companies that failed GPT-4o enrichment"""
        all_companies = self.load_companies()
        failed = []

        for enriched_file in self.enriched_dir.glob("*_enriched.json"):
            try:
                with open(enriched_file, 'r') as f:
                    data = json.load(f)

                ai_insights = data.get('ai_insights', {})
                # Target failed GPT-4o enrichments or incomplete
                if ((ai_insights.get('model_used') == 'gpt-4o' and ai_insights.get('status') == 'error') or
                    not data.get('phase8_complete')):

                    slug = data.get('slug')
                    if slug in all_companies:
                        full_company = {**all_companies[slug], **data}
                        failed.append((slug, enriched_file, full_company))

            except Exception as e:
                logger.warning(f"Error reading {enriched_file}: {e}")

        logger.info(f"Found {len(failed)} companies to enrich with GPT-4o")
        return failed

    def enrich_with_key(self, company: Dict, key_num: int) -> Dict:
        """Enrich using specified key"""
        client = self.client1 if key_num == 1 else self.client2
        key_name = f"key{key_num}"

        company_name = company.get('name', 'Unknown')

        try:
            # Build context
            context = self._build_context(company)

            # Generate insights
            prompt = self._build_prompt(context)

            response = client.chat.completions.create(
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

            # Add metadata
            usage = response.usage
            cost = (usage.prompt_tokens / 1000 * 0.0025) + (usage.completion_tokens / 1000 * 0.010)

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

            self.stats[key_name]["success"] += 1
            return result

        except Exception as e:
            self.stats[key_name]["error"] += 1
            logger.error(f"[{key_name.upper()}] Error enriching {company_name}: {str(e)[:100]}")
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

        # Add enriched data if available
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

    def run(self, max_workers: int = 16):
        """Run dual-key enrichment"""
        companies = self.get_failed_companies()
        total = len(companies)

        if total == 0:
            logger.info("✅ All companies already enriched!")
            return

        # Split companies between two keys (interleaved)
        key1_companies = companies[0::2]
        key2_companies = companies[1::2]

        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 DUAL-KEY GPT-4O ENRICHMENT")
        logger.info(f"{'='*70}")
        logger.info(f"Total companies: {total}")
        logger.info(f"Key 1 batch: {len(key1_companies)} companies")
        logger.info(f"Key 2 batch: {len(key2_companies)} companies")
        logger.info(f"Workers per key: {max_workers // 2}")
        logger.info(f"Combined throughput: ~1000 requests/min")
        logger.info(f"{'='*70}\n")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            # Submit key1 jobs
            for slug, enriched_file, company in key1_companies:
                future = executor.submit(self.enrich_with_key, company, 1)
                futures[future] = (slug, enriched_file, company, 1)

            # Submit key2 jobs
            for slug, enriched_file, company in key2_companies:
                future = executor.submit(self.enrich_with_key, company, 2)
                futures[future] = (slug, enriched_file, company, 2)

            # Process results
            completed = 0
            for future in as_completed(futures):
                completed += 1
                slug, enriched_file, company, key_num = futures[future]

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
                            f"K1: {self.stats['key1']['success']}✓/{self.stats['key1']['error']}✗ | "
                            f"K2: {self.stats['key2']['success']}✓/{self.stats['key2']['error']}✗"
                        )

                except Exception as e:
                    logger.error(f"Error processing {company.get('name', slug)}: {e}")

        total_time = time.time() - start_time

        logger.info(f"\n{'='*70}")
        logger.info(f"✅ DUAL-KEY ENRICHMENT COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Key 1: {self.stats['key1']['success']} success, {self.stats['key1']['error']} errors")
        logger.info(f"Key 2: {self.stats['key2']['success']} success, {self.stats['key2']['error']} errors")
        logger.info(f"Total: {self.stats['key1']['success'] + self.stats['key2']['success']} success")
        logger.info(f"Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        logger.info(f"Rate: {total/total_time:.2f} companies/second")
        logger.info(f"{'='*70}\n")


if __name__ == "__main__":
    enricher = DualKeyEnricher()
    enricher.run(max_workers=16)  # 8 workers per key

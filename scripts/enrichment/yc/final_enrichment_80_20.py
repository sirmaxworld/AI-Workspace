#!/usr/bin/env python3
"""
Final Enrichment: 80% Claude Sonnet 4, 20% GPT-4o
Priority on Claude for quality, GPT-4o for debugging rate limits
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
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FinalEnrichment:
    """80/20 split: Claude Sonnet 4 (high quality) / GPT-4o (debugging)"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.enriched_dir = self.workspace_dir / "data" / "yc_enriched"
        self.companies_file = self.workspace_dir / "data" / "yc_companies" / "all_companies.json"

        # Initialize clients
        self.claude_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        self.claude_model = "claude-sonnet-4-20250514"
        self.gpt_model = "gpt-4o"

        logger.info(f"✓ Claude model: {self.claude_model}")
        logger.info(f"✓ GPT model: {self.gpt_model}")

        self.stats = {
            "claude": {"success": 0, "error": 0},
            "gpt": {"success": 0, "error": 0}
        }

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

    def enrich_with_claude(self, company: Dict) -> Dict:
        """Enrich using Claude Sonnet 4"""
        company_name = company.get('name', 'Unknown')

        try:
            context = self._build_context(company)
            prompt = self._build_prompt(context)

            response = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=2000,
                temperature=0.3,
                system="You are a startup analyst providing strategic insights on Y Combinator companies. Always respond with valid JSON.",
                messages=[{"role": "user", "content": prompt}]
            )

            insights_json = response.content[0].text

            # Extract JSON from markdown if needed
            if "```json" in insights_json:
                insights_json = insights_json.split("```json")[1].split("```")[0].strip()
            elif "```" in insights_json:
                insights_json = insights_json.split("```")[1].split("```")[0].strip()

            insights = json.loads(insights_json)

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = (input_tokens / 1_000_000 * 3.0) + (output_tokens / 1_000_000 * 15.0)

            result = {
                "ai_insights_version": "1.0.0",
                "model_used": self.claude_model,
                "enriched_at": datetime.now().isoformat(),
                "status": "success",
                **insights,
                "tokens_used": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens,
                    "estimated_cost": round(cost, 6)
                }
            }

            self.stats["claude"]["success"] += 1
            return result

        except Exception as e:
            self.stats["claude"]["error"] += 1
            logger.error(f"[CLAUDE] Error enriching {company_name}: {str(e)[:100]}")
            return {
                "ai_insights_version": "1.0.0",
                "model_used": self.claude_model,
                "enriched_at": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)[:200]
            }

    def enrich_with_gpt(self, company: Dict) -> Dict:
        """Enrich using GPT-4o"""
        company_name = company.get('name', 'Unknown')

        try:
            context = self._build_context(company)
            prompt = self._build_prompt(context)

            response = self.openai_client.chat.completions.create(
                model=self.gpt_model,
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
            cost = (usage.prompt_tokens / 1000 * 0.0025) + (usage.completion_tokens / 1000 * 0.010)

            result = {
                "ai_insights_version": "1.0.0",
                "model_used": self.gpt_model,
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

            self.stats["gpt"]["success"] += 1
            return result

        except Exception as e:
            self.stats["gpt"]["error"] += 1
            logger.error(f"[GPT] Error enriching {company_name}: {str(e)[:100]}")
            return {
                "ai_insights_version": "1.0.0",
                "model_used": self.gpt_model,
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

    def run(self, claude_workers: int = 48, gpt_workers: int = 4):
        """
        Run 80/20 enrichment

        Args:
            claude_workers: Workers for Claude (80% of work)
            gpt_workers: Workers for GPT-4o (20% of work, debugging)
        """
        companies = self.get_incomplete_companies()
        total = len(companies)

        if total == 0:
            logger.info("✅ All companies already enriched!")
            return

        # Split 80/20
        split_point = int(total * 0.8)
        claude_companies = companies[:split_point]
        gpt_companies = companies[split_point:]

        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 FINAL ENRICHMENT: 80% CLAUDE / 20% GPT-4O")
        logger.info(f"{'='*70}")
        logger.info(f"Total companies: {total}")
        logger.info(f"Claude batch: {len(claude_companies)} ({len(claude_companies)/total*100:.0f}%) - {claude_workers} workers")
        logger.info(f"GPT batch: {len(gpt_companies)} ({len(gpt_companies)/total*100:.0f}%) - {gpt_workers} workers")
        logger.info(f"{'='*70}\n")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=claude_workers + gpt_workers) as executor:
            futures = {}

            # Submit Claude jobs (80%)
            for slug, enriched_file, company in claude_companies:
                future = executor.submit(self.enrich_with_claude, company)
                futures[future] = (slug, enriched_file, company, 'claude')

            # Submit GPT jobs (20%)
            for slug, enriched_file, company in gpt_companies:
                future = executor.submit(self.enrich_with_gpt, company)
                futures[future] = (slug, enriched_file, company, 'gpt')

            # Process results
            completed = 0
            for future in as_completed(futures):
                completed += 1
                slug, enriched_file, company, engine = futures[future]

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
                            f"Claude: {self.stats['claude']['success']}✓/{self.stats['claude']['error']}✗ | "
                            f"GPT: {self.stats['gpt']['success']}✓/{self.stats['gpt']['error']}✗"
                        )

                except Exception as e:
                    logger.error(f"Error processing {company.get('name', slug)}: {e}")

        total_time = time.time() - start_time

        logger.info(f"\n{'='*70}")
        logger.info(f"✅ FINAL ENRICHMENT COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Claude: {self.stats['claude']['success']} success, {self.stats['claude']['error']} errors")
        logger.info(f"GPT: {self.stats['gpt']['success']} success, {self.stats['gpt']['error']} errors")
        logger.info(f"Total: {self.stats['claude']['success'] + self.stats['gpt']['success']} success")
        logger.info(f"Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        logger.info(f"Rate: {total/total_time:.2f} companies/second")
        logger.info(f"{'='*70}\n")


if __name__ == "__main__":
    enricher = FinalEnrichment()
    # 144 Claude workers (80%), 12 GPT workers (20%), total 156 workers (3x speed)
    enricher.run(claude_workers=144, gpt_workers=12)

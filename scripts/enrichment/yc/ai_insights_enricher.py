#!/usr/bin/env python3
"""
AI Insights Enricher - Phase 8
Uses OpenAI GPT-4o-mini ($0.000150/1K input, $0.000600/1K output) to generate:
- Market analysis
- Competitive positioning
- Business model assessment
- Risk analysis
- Investment thesis
- Strategic recommendations

Cost: ~$0.001 per company = $5 total for 5,490 companies
"""

import os
import json
from typing import Dict
from datetime import datetime
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIInsightsEnricher:
    """Enriches YC companies with AI-generated insights"""

    VERSION = "1.0.0"

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # High-quality model
        logger.info(f"✓ AI Insights Enricher initialized with {self.model}")

    def enrich(self, company: Dict) -> Dict:
        """
        Main enrichment function for AI insights

        Args:
            company: Full company data dict with all enrichment data

        Returns:
            Dict with AI-generated insights
        """
        enrichment_data = {
            "ai_insights_version": self.VERSION,
            "model_used": self.model,
            "enriched_at": datetime.now().isoformat(),
        }

        company_name = company.get('name', '').strip()

        if not company_name:
            enrichment_data["status"] = "no_company_name"
            return enrichment_data

        logger.info(f"Generating AI insights for {company_name}")

        # Build context from all enriched data
        context = self._build_context(company)

        # Generate insights
        try:
            insights = self._generate_insights(company_name, context)
            enrichment_data.update(insights)
            enrichment_data["status"] = "success"

        except Exception as e:
            logger.error(f"AI insights generation failed for {company_name}: {e}")
            enrichment_data["status"] = "error"
            enrichment_data["error"] = str(e)[:200]

        return enrichment_data

    def _build_context(self, company: Dict) -> str:
        """Build context string from all available company data"""

        context_parts = []

        # Basic info
        context_parts.append(f"Company: {company.get('name')}")
        context_parts.append(f"One-liner: {company.get('one_liner', 'N/A')}")
        context_parts.append(f"Description: {company.get('long_description', 'N/A')[:500]}")
        context_parts.append(f"Industry: {company.get('industry', 'N/A')}")
        context_parts.append(f"Batch: {company.get('batch', 'N/A')}")
        context_parts.append(f"Team Size: {company.get('team_size', 'N/A')}")
        context_parts.append(f"Status: {company.get('status', 'N/A')}")
        context_parts.append(f"Website: {company.get('website', 'N/A')}")

        # Web data (Phase 1)
        web_data = company.get('web_data', {})
        if web_data:
            domain_info = web_data.get('domain_info', {})
            if domain_info.get('domain_age_years'):
                context_parts.append(f"Domain age: {domain_info['domain_age_years']} years")

        # GitHub data (Phase 3)
        github_data = company.get('github_data', {})
        if github_data and github_data.get('status') != 'no_github_link':
            org = github_data.get('organization', {})
            repos = github_data.get('repositories', {})
            if repos.get('total_stars'):
                context_parts.append(f"GitHub: {repos.get('total_repos', 0)} repos, {repos.get('total_stars', 0)} stars")
            tech_stack = github_data.get('tech_stack', {})
            if tech_stack.get('primary_language'):
                context_parts.append(f"Primary tech: {tech_stack['primary_language']}")

        # Network data (Phase 4)
        network_data = company.get('network_data', {})
        if network_data:
            metrics = network_data.get('network_metrics', {})
            if metrics:
                context_parts.append(f"YC connections: {metrics.get('total_yc_connections', 0)}")

        # Patent data (Phase 5)
        patent_data = company.get('patent_data', {})
        if patent_data:
            patents = patent_data.get('patents', {})
            if patents.get('patent_count', 0) > 0:
                context_parts.append(f"Patents: {patents['patent_count']}")

        return "\n".join(context_parts)

    def _generate_insights(self, company_name: str, context: str) -> Dict:
        """Generate AI insights using GPT-4o-mini"""

        prompt = f"""Analyze this Y Combinator company and provide strategic insights:

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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a startup analyst providing strategic insights on Y Combinator companies. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            insights_json = response.choices[0].message.content
            insights = json.loads(insights_json)

            # Add token usage for cost tracking
            usage = response.usage
            cost = (usage.prompt_tokens / 1000 * 0.000150) + (usage.completion_tokens / 1000 * 0.000600)

            return {
                **insights,
                "tokens_used": {
                    "prompt": usage.prompt_tokens,
                    "completion": usage.completion_tokens,
                    "total": usage.total_tokens,
                    "estimated_cost": round(cost, 6)
                }
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise Exception(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            raise


def main():
    """Test the enricher"""
    from pathlib import Path

    # Load a sample enriched company
    enriched_file = Path("/Users/yourox/AI-Workspace/data/yc_enriched/stripe_enriched.json")

    if enriched_file.exists():
        with open(enriched_file, 'r') as f:
            company = json.load(f)

        enricher = AIInsightsEnricher()
        result = enricher.enrich(company)

        print(f"\n{'='*70}")
        print(f"AI Insights for: {company['name']}")
        print(f"{'='*70}")
        print(json.dumps(result, indent=2))

        if result.get('tokens_used'):
            print(f"\n💰 Cost: ${result['tokens_used']['estimated_cost']:.6f}")
    else:
        print(f"❌ Test file not found: {enriched_file}")


if __name__ == "__main__":
    main()

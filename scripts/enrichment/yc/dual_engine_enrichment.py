#!/usr/bin/env python3
"""
Dual-Engine Parallel Enrichment
Runs OpenAI and Claude Sonnet 4 in parallel for maximum throughput
Target: Complete 2,451 companies in 30 minutes
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ai_insights_enricher import AIInsightsEnricher  # OpenAI version
from ai_insights_enricher_claude import AIInsightsEnricherClaude  # Claude version

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DualEngineEnrichment:
    """Coordinates parallel enrichment using both OpenAI and Claude"""

    def __init__(self, workspace_dir: Path = None):
        if workspace_dir is None:
            workspace_dir = Path("/Users/yourox/AI-Workspace")

        self.workspace_dir = workspace_dir
        self.companies_file = workspace_dir / "data" / "yc_companies" / "all_companies.json"
        self.enriched_dir = workspace_dir / "data" / "yc_enriched"

        # Initialize both enrichers
        logger.info("Initializing OpenAI enricher...")
        self.openai_enricher = AIInsightsEnricher()

        logger.info("Initializing Claude enricher...")
        self.claude_enricher = AIInsightsEnricherClaude()

        self.stats = {
            "openai": {"processed": 0, "errors": 0},
            "claude": {"processed": 0, "errors": 0}
        }

    def load_companies(self) -> List[Dict]:
        """Load all YC companies"""
        with open(self.companies_file, 'r') as f:
            return json.load(f)

    def get_enriched_path(self, company_slug: str) -> Path:
        """Get path to enriched file"""
        return self.enriched_dir / f"{company_slug}_enriched.json"

    def load_enriched(self, company_slug: str) -> Dict:
        """Load existing enriched data"""
        enriched_file = self.get_enriched_path(company_slug)
        if enriched_file.exists():
            with open(enriched_file, 'r') as f:
                return json.load(f)
        return None

    def save_enriched(self, company_slug: str, enriched_data: Dict):
        """Save enriched data"""
        enriched_file = self.get_enriched_path(company_slug)
        with open(enriched_file, 'w') as f:
            json.dump(enriched_data, f, indent=2)

    def get_incomplete_companies(self) -> List[Dict]:
        """Get companies that need Phase 8 enrichment"""
        all_companies = self.load_companies()
        incomplete = []

        for company in all_companies:
            slug = company.get('slug', '')
            enriched = self.load_enriched(slug)

            if enriched and not enriched.get('phase8_complete'):
                # Merge company data with enriched data
                incomplete.append({**company, **enriched})
            elif enriched is None:
                # No enriched file at all - skip
                continue

        logger.info(f"Found {len(incomplete)} companies needing Phase 8")
        return incomplete

    def enrich_company(self, company: Dict, engine: str) -> Dict:
        """
        Enrich a single company with specified engine

        Args:
            company: Company data with existing enrichment
            engine: 'openai' or 'claude'
        """
        slug = company.get('slug', '')
        name = company.get('name', 'Unknown')

        try:
            # Choose enricher
            if engine == 'openai':
                ai_insights = self.openai_enricher.enrich(company)
            else:
                ai_insights = self.claude_enricher.enrich(company)

            # Update enriched data
            enriched = self.load_enriched(slug)
            if enriched:
                enriched['ai_insights'] = ai_insights
                enriched['phase8_complete'] = True
                enriched['enriched_at'] = datetime.now().isoformat()
                self.save_enriched(slug, enriched)

            self.stats[engine]["processed"] += 1
            return {
                "status": "success",
                "slug": slug,
                "name": name,
                "engine": engine
            }

        except Exception as e:
            self.stats[engine]["errors"] += 1
            logger.error(f"[{engine.upper()}] Error enriching {name}: {e}")
            return {
                "status": "error",
                "slug": slug,
                "name": name,
                "engine": engine,
                "error": str(e)[:200]
            }

    def run_parallel(self, openai_workers: int = 40, claude_workers: int = 40):
        """
        Run parallel enrichment with both engines

        Args:
            openai_workers: Number of parallel OpenAI workers
            claude_workers: Number of parallel Claude workers
        """
        # Get incomplete companies
        companies = self.get_incomplete_companies()
        total = len(companies)

        if total == 0:
            logger.info("✅ All companies already have Phase 8 complete!")
            return

        # Split companies between engines (interleaved for balance)
        openai_batch = companies[0::2]  # Even indices
        claude_batch = companies[1::2]  # Odd indices

        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 DUAL-ENGINE PARALLEL ENRICHMENT")
        logger.info(f"{'='*70}")
        logger.info(f"Total companies: {total}")
        logger.info(f"OpenAI batch: {len(openai_batch)} companies ({openai_workers} workers)")
        logger.info(f"Claude batch: {len(claude_batch)} companies ({claude_workers} workers)")
        logger.info(f"Target: Complete in 30 minutes")
        logger.info(f"{'='*70}\n")

        start_time = time.time()

        # Run both batches in parallel using separate thread pools
        with ThreadPoolExecutor(max_workers=openai_workers + claude_workers) as executor:
            futures = {}

            # Submit OpenAI jobs
            for company in openai_batch:
                future = executor.submit(self.enrich_company, company, 'openai')
                futures[future] = ('openai', company)

            # Submit Claude jobs
            for company in claude_batch:
                future = executor.submit(self.enrich_company, company, 'claude')
                futures[future] = ('claude', company)

            # Process results as they complete
            completed = 0
            for future in as_completed(futures):
                completed += 1
                engine, company = futures[future]

                try:
                    result = future.result()
                    if result["status"] == "success":
                        if completed % 50 == 0:  # Progress update every 50
                            elapsed = time.time() - start_time
                            rate = completed / elapsed
                            remaining = (total - completed) / rate if rate > 0 else 0

                            logger.info(
                                f"[{completed}/{total}] {completed/total*100:.1f}% | "
                                f"Rate: {rate:.1f}/s | ETA: {remaining/60:.1f}m | "
                                f"OpenAI: {self.stats['openai']['processed']} | "
                                f"Claude: {self.stats['claude']['processed']}"
                            )
                    else:
                        logger.error(
                            f"[{engine.upper()}] ❌ {result['name'][:40]}: "
                            f"{result.get('error', 'unknown')[:100]}"
                        )

                except Exception as e:
                    logger.error(f"Exception processing {company.get('name', 'Unknown')}: {e}")

        total_time = time.time() - start_time

        # Final stats
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ DUAL-ENGINE ENRICHMENT COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"OpenAI processed: {self.stats['openai']['processed']}")
        logger.info(f"OpenAI errors: {self.stats['openai']['errors']}")
        logger.info(f"Claude processed: {self.stats['claude']['processed']}")
        logger.info(f"Claude errors: {self.stats['claude']['errors']}")
        logger.info(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        logger.info(f"Rate: {total/total_time:.2f} companies/second")
        logger.info(f"{'='*70}\n")

        return self.stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Dual-Engine Parallel Enrichment")
    parser.add_argument('--openai-workers', type=int, default=40,
                       help='Number of OpenAI parallel workers')
    parser.add_argument('--claude-workers', type=int, default=40,
                       help='Number of Claude parallel workers')

    args = parser.parse_args()

    enricher = DualEngineEnrichment()
    enricher.run_parallel(
        openai_workers=args.openai_workers,
        claude_workers=args.claude_workers
    )


if __name__ == "__main__":
    main()

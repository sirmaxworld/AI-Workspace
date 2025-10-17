#!/usr/bin/env python3
"""
YC Companies Enrichment Coordinator
Orchestrates all enrichment phases across 5,490+ companies
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from web_data_enricher import WebDataEnricher
from geographic_enricher_v2 import GeographicEnricherV2 as GeographicEnricher
from github_enricher import GitHubEnricher
from network_enricher import NetworkEnricher
from patent_enricher import PatentEnricher
from reviews_enricher import ReviewsEnricher
from hiring_enricher import HiringEnricher
from ai_insights_enricher import AIInsightsEnricher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YCEnrichmentCoordinator:
    """Coordinates enrichment of all YC companies across multiple phases"""

    VERSION = "1.0.0"

    def __init__(self, workspace_dir: Path = None):
        if workspace_dir is None:
            workspace_dir = Path("/Users/yourox/AI-Workspace")

        self.workspace_dir = workspace_dir
        self.companies_file = workspace_dir / "data" / "yc_companies" / "all_companies.json"
        self.enriched_dir = workspace_dir / "data" / "yc_enriched"
        self.enriched_dir.mkdir(parents=True, exist_ok=True)

        # Initialize all enrichers
        self.web_enricher = WebDataEnricher()
        self.geo_enricher = GeographicEnricher()
        self.github_enricher = GitHubEnricher()
        self.patent_enricher = PatentEnricher()
        self.reviews_enricher = ReviewsEnricher()
        self.hiring_enricher = HiringEnricher()
        self.ai_enricher = AIInsightsEnricher()

        # Network enricher needs all companies
        self.network_enricher = None  # Will be initialized when needed

        # Statistics
        self.stats = {
            "total": 0,
            "processed": 0,
            "cached": 0,
            "errors": 0,
            "skipped": 0
        }

        logger.info(f"YC Enrichment Coordinator v{self.VERSION} initialized")

    def load_companies(self) -> List[Dict]:
        """Load all YC companies"""
        if not self.companies_file.exists():
            raise FileNotFoundError(f"Companies file not found: {self.companies_file}")

        with open(self.companies_file, 'r') as f:
            companies = json.load(f)

        logger.info(f"Loaded {len(companies)} companies")
        return companies

    def get_enriched_path(self, company_slug: str) -> Path:
        """Get path to enriched file for a company"""
        return self.enriched_dir / f"{company_slug}_enriched.json"

    def load_enriched(self, company_slug: str) -> Optional[Dict]:
        """Load existing enriched data"""
        enriched_file = self.get_enriched_path(company_slug)

        if not enriched_file.exists():
            return None

        try:
            with open(enriched_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading enriched data for {company_slug}: {e}")
            return None

    def save_enriched(self, company_slug: str, enriched_data: Dict):
        """Save enriched data"""
        enriched_file = self.get_enriched_path(company_slug)

        try:
            with open(enriched_file, 'w') as f:
                json.dump(enriched_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving enriched data for {company_slug}: {e}")
            raise

    def enrich_company_phase1(
        self,
        company: Dict,
        force: bool = False
    ) -> Dict:
        """
        Enrich a single company with Phase 1 data (web + geo)

        Args:
            company: Company data dict
            force: Force re-enrichment even if already enriched

        Returns:
            Status dict
        """
        slug = company.get('slug', '')
        name = company.get('name', 'Unknown')

        # Check if already enriched
        if not force:
            existing = self.load_enriched(slug)
            if existing and existing.get('phase1_complete'):
                return {
                    "status": "cached",
                    "slug": slug,
                    "name": name
                }

        try:
            # Phase 1: Web Data
            web_data = self.web_enricher.enrich(company)

            # Build enriched data structure
            enriched = {
                "slug": slug,
                "name": name,
                "yc_id": company.get('id'),
                "batch": company.get('batch'),
                "website": company.get('website'),

                # Phase 1 enrichments
                "web_data": web_data,

                # Metadata
                "enrichment_version": self.VERSION,
                "enriched_at": datetime.now().isoformat(),
                "phase1_complete": True,
                "phase2_complete": False,
                "phase3_complete": False,
                "phase4_complete": False,
                "phase5_complete": False
            }

            # Save
            self.save_enriched(slug, enriched)

            return {
                "status": "success",
                "slug": slug,
                "name": name
            }

        except Exception as e:
            logger.error(f"Error enriching {name}: {e}")
            return {
                "status": "error",
                "slug": slug,
                "name": name,
                "error": str(e)[:200]
            }

    def enrich_batch(
        self,
        companies: List[Dict],
        phase: int = 1,
        force: bool = False,
        max_workers: int = 5,
        rate_limit_delay: float = 0.5
    ):
        """
        Enrich a batch of companies

        Args:
            companies: List of company dicts
            phase: Enrichment phase (1-5)
            force: Force re-enrichment
            max_workers: Number of parallel workers
            rate_limit_delay: Delay between requests (seconds)
        """
        total = len(companies)
        self.stats["total"] = total

        print(f"\n{'='*70}")
        print(f"🚀 YC COMPANIES ENRICHMENT - PHASE {phase}")
        print(f"{'='*70}\n")
        print(f"Total companies: {total}")
        print(f"Max workers: {max_workers}")
        print(f"Force mode: {force}\n")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for company in companies:
                if phase == 1:
                    future = executor.submit(self.enrich_company_phase1, company, force)
                    futures[future] = company

                # Add delay for rate limiting
                time.sleep(rate_limit_delay)

            # Process results as they complete
            for i, future in enumerate(as_completed(futures), 1):
                company = futures[future]
                try:
                    result = future.result()
                    status = result["status"]

                    if status == "success":
                        self.stats["processed"] += 1
                        print(f"[{i}/{total}] ✅ {result['name'][:40]}")

                    elif status == "cached":
                        self.stats["cached"] += 1
                        if i % 50 == 0:  # Only print every 50th cached
                            print(f"[{i}/{total}] ⚡ Cached: {result['name'][:40]}")

                    elif status == "error":
                        self.stats["errors"] += 1
                        print(f"[{i}/{total}] ❌ {result['name'][:40]}: {result.get('error', 'unknown')}")

                    # Progress update every 100 companies
                    if i % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed
                        remaining = (total - i) / rate if rate > 0 else 0
                        print(f"\n📊 Progress: {i}/{total} ({i/total*100:.1f}%) | Rate: {rate:.1f}/s | ETA: {remaining/60:.1f}m\n")

                except Exception as e:
                    self.stats["errors"] += 1
                    print(f"[{i}/{total}] ❌ Exception: {company.get('name', 'Unknown')}: {e}")

        total_time = time.time() - start_time

        print(f"\n{'='*70}")
        print(f"✅ PHASE {phase} ENRICHMENT COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Newly processed: {self.stats['processed']}")
        print(f"⚡ Cached (skipped): {self.stats['cached']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print(f"⏱️  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"📈 Rate: {total/total_time:.2f} companies/second")
        print(f"{'='*70}\n")

        return self.stats

    def enrich_company_all_phases(self, company: Dict, force: bool = False) -> Dict:
        """
        Enrich a single company with all phases (2-8)
        Phase 1 should already be complete

        Args:
            company: Company data with existing enrichment
            force: Force re-enrichment

        Returns:
            Updated enrichment data
        """
        slug = company.get('slug', '')
        name = company.get('name', 'Unknown')

        # Load existing enrichment (Phase 1)
        enriched = self.load_enriched(slug)
        if not enriched:
            logger.warning(f"No Phase 1 data for {name}, skipping")
            return {"status": "skipped", "reason": "no_phase1_data"}

        # Merge original company data
        full_company = {**company, **enriched}

        try:
            # Phase 2: Geographic
            if force or not enriched.get('phase2_complete'):
                geo_data = self.geo_enricher.enrich(full_company)
                enriched['geographic_data'] = geo_data
                enriched['phase2_complete'] = True

            # Phase 3: GitHub/Technical
            if force or not enriched.get('phase3_complete'):
                github_data = self.github_enricher.enrich(full_company)
                enriched['github_data'] = github_data
                enriched['phase3_complete'] = True

            # Phase 4: Network (needs all companies)
            if force or not enriched.get('phase4_complete'):
                if self.network_enricher:
                    network_data = self.network_enricher.enrich(full_company)
                    enriched['network_data'] = network_data
                    enriched['phase4_complete'] = True

            # Phase 5: Patents
            if force or not enriched.get('phase5_complete'):
                patent_data = self.patent_enricher.enrich(full_company)
                enriched['patent_data'] = patent_data
                enriched['phase5_complete'] = True

            # Phase 6: Reviews
            if force or not enriched.get('phase6_complete'):
                reviews_data = self.reviews_enricher.enrich(full_company)
                enriched['reviews_data'] = reviews_data
                enriched['phase6_complete'] = True

            # Phase 7: Hiring
            if force or not enriched.get('phase7_complete'):
                hiring_data = self.hiring_enricher.enrich(full_company)
                enriched['hiring_data'] = hiring_data
                enriched['phase7_complete'] = True

            # Phase 8: AI Insights
            if force or not enriched.get('phase8_complete'):
                ai_data = self.ai_enricher.enrich(full_company)
                enriched['ai_insights'] = ai_data
                enriched['phase8_complete'] = True

            # Update metadata
            enriched['enriched_at'] = datetime.now().isoformat()

            # Save
            self.save_enriched(slug, enriched)

            return {"status": "success", "slug": slug, "name": name}

        except Exception as e:
            logger.error(f"Error enriching {name}: {e}")
            return {"status": "error", "slug": slug, "name": name, "error": str(e)[:200]}

    def enrich_all_phase1(
        self,
        force: bool = False,
        max_workers: int = 5,
        limit: Optional[int] = None
    ):
        """Enrich all companies with Phase 1 data"""
        companies = self.load_companies()

        if limit:
            companies = companies[:limit]

        return self.enrich_batch(
            companies,
            phase=1,
            force=force,
            max_workers=max_workers
        )

    def enrich_all_phases(
        self,
        force: bool = False,
        max_workers: int = 3,
        limit: Optional[int] = None,
        phases: str = "2-8"
    ):
        """
        Enrich all companies with phases 2-8

        Args:
            force: Force re-enrichment
            max_workers: Parallel workers (lower for API rate limits)
            limit: Limit number of companies
            phases: Which phases to run (e.g., "2-8", "8", "2,3,8")
        """
        companies = self.load_companies()

        # Initialize network enricher with all companies
        logger.info("Initializing network enricher with all companies...")
        self.network_enricher = NetworkEnricher(companies)

        if limit:
            companies = companies[:limit]

        total = len(companies)
        self.stats = {"total": total, "processed": 0, "cached": 0, "errors": 0}

        print(f"\n{'='*70}")
        print(f"🚀 YC COMPANIES ENRICHMENT - PHASES {phases}")
        print(f"{'='*70}\n")
        print(f"Total companies: {total}")
        print(f"Max workers: {max_workers}")
        print(f"Force mode: {force}\n")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for company in companies:
                future = executor.submit(self.enrich_company_all_phases, company, force)
                futures[future] = company
                time.sleep(0.2)  # Rate limiting

            # Process results
            for i, future in enumerate(as_completed(futures), 1):
                company = futures[future]
                try:
                    result = future.result()
                    status = result["status"]

                    if status == "success":
                        self.stats["processed"] += 1
                        print(f"[{i}/{total}] ✅ {result['name'][:50]}")
                    elif status == "error":
                        self.stats["errors"] += 1
                        print(f"[{i}/{total}] ❌ {result['name'][:50]}: {result.get('error', '')[:100]}")
                    else:
                        self.stats["cached"] += 1

                    # Progress update
                    if i % 50 == 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed
                        remaining = (total - i) / rate if rate > 0 else 0
                        print(f"\n📊 Progress: {i}/{total} ({i/total*100:.1f}%) | Rate: {rate:.2f}/s | ETA: {remaining/60:.1f}m\n")

                except Exception as e:
                    self.stats["errors"] += 1
                    print(f"[{i}/{total}] ❌ Exception: {company.get('name', 'Unknown')}: {e}")

        total_time = time.time() - start_time

        print(f"\n{'='*70}")
        print(f"✅ PHASES {phases} ENRICHMENT COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Processed: {self.stats['processed']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print(f"⏱️  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"📈 Rate: {total/total_time:.2f} companies/second")
        print(f"{'='*70}\n")

        return self.stats

    def get_enrichment_stats(self) -> Dict:
        """Get statistics on enriched companies"""
        enriched_files = list(self.enriched_dir.glob("*_enriched.json"))

        stats = {
            "total_companies": 0,
            "total_enriched": len(enriched_files),
            "phase1_complete": 0,
            "phase2_complete": 0,
            "phase3_complete": 0,
            "phase4_complete": 0,
            "phase5_complete": 0,
            "with_website": 0,
            "with_social_links": 0,
            "with_domain_info": 0
        }

        # Load all companies to get total
        companies = self.load_companies()
        stats["total_companies"] = len(companies)

        # Analyze enriched files
        for enriched_file in enriched_files:
            try:
                with open(enriched_file, 'r') as f:
                    data = json.load(f)

                if data.get('phase1_complete'):
                    stats["phase1_complete"] += 1

                if data.get('phase2_complete'):
                    stats["phase2_complete"] += 1

                if data.get('phase3_complete'):
                    stats["phase3_complete"] += 1

                if data.get('phase4_complete'):
                    stats["phase4_complete"] += 1

                if data.get('phase5_complete'):
                    stats["phase5_complete"] += 1

                # Phase 1 specific stats
                web_data = data.get('web_data', {})
                if web_data.get('website_status', {}).get('reachable'):
                    stats["with_website"] += 1

                social_links = web_data.get('social_links', {})
                if any(social_links.values()):
                    stats["with_social_links"] += 1

                if 'domain_info' in web_data and not web_data['domain_info'].get('error'):
                    stats["with_domain_info"] += 1

            except Exception as e:
                logger.warning(f"Error reading {enriched_file}: {e}")

        return stats


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="YC Companies Enrichment Coordinator")
    parser.add_argument('command', choices=['phase1', 'all-phases', 'stats', 'test'],
                       help='Command to run')
    parser.add_argument('--force', action='store_true', help='Force re-enrichment')
    parser.add_argument('--workers', type=int, default=3, help='Number of parallel workers')
    parser.add_argument('--limit', type=int, help='Limit number of companies (for testing)')

    args = parser.parse_args()

    coordinator = YCEnrichmentCoordinator()

    if args.command == 'phase1':
        coordinator.enrich_all_phase1(
            force=args.force,
            max_workers=args.workers,
            limit=args.limit
        )

    elif args.command == 'all-phases':
        print("\n🚀 Running ALL enrichment phases (2-8) on all companies!")
        print("This will take ~6-8 hours and cost ~$2.11 (Phase 8 only)\n")

        coordinator.enrich_all_phases(
            force=args.force,
            max_workers=args.workers,
            limit=args.limit
        )

    elif args.command == 'stats':
        stats = coordinator.get_enrichment_stats()
        print("\n" + "="*70)
        print("📊 YC COMPANIES ENRICHMENT STATISTICS")
        print("="*70)
        for key, value in stats.items():
            print(f"{key:30s}: {value:,}")
        print("="*70 + "\n")

    elif args.command == 'test':
        print("Testing all phases on first 3 companies...\n")
        coordinator.enrich_all_phases(limit=3, force=True, max_workers=1)


if __name__ == "__main__":
    main()

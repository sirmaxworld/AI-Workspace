#!/usr/bin/env python3
"""
Fix Claude Enrichments
Re-enrich companies that failed with Claude due to JSON parsing bug
"""

import json
import time
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from ai_insights_enricher_claude import AIInsightsEnricherClaude

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_claude_enrichments(max_workers=60):
    """Re-enrich all failed Claude enrichments"""

    workspace_dir = Path("/Users/yourox/AI-Workspace")
    enriched_dir = workspace_dir / "data" / "yc_enriched"
    companies_file = workspace_dir / "data" / "yc_companies" / "all_companies.json"

    # Load all companies
    with open(companies_file, 'r') as f:
        all_companies = {c['slug']: c for c in json.load(f)}

    # Find failed Claude enrichments
    failed = []
    for enriched_file in enriched_dir.glob("*_enriched.json"):
        try:
            with open(enriched_file, 'r') as f:
                data = json.load(f)

            ai_insights = data.get('ai_insights', {})
            if (ai_insights.get('model_used') == 'claude-sonnet-4-20250514' and
                ai_insights.get('status') == 'error'):

                slug = data.get('slug')
                if slug in all_companies:
                    # Merge company + enriched data
                    full_company = {**all_companies[slug], **data}
                    failed.append((slug, enriched_file, full_company))

        except Exception as e:
            logger.warning(f"Error reading {enriched_file}: {e}")

    logger.info(f"Found {len(failed)} failed Claude enrichments to fix")

    if len(failed) == 0:
        logger.info("✅ No failed enrichments to fix!")
        return

    # Initialize enricher
    enricher = AIInsightsEnricherClaude()

    # Re-enrich in parallel
    stats = {"success": 0, "error": 0}
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}

        for slug, enriched_file, company in failed:
            future = executor.submit(enricher.enrich, company)
            futures[future] = (slug, enriched_file, company)

        for i, future in enumerate(as_completed(futures), 1):
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

                if ai_insights.get('status') == 'success':
                    stats["success"] += 1
                else:
                    stats["error"] += 1

                if i % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed
                    remaining = (len(failed) - i) / rate if rate > 0 else 0
                    logger.info(
                        f"[{i}/{len(failed)}] {i/len(failed)*100:.1f}% | "
                        f"Rate: {rate:.1f}/s | ETA: {remaining/60:.1f}m | "
                        f"Success: {stats['success']} | Errors: {stats['error']}"
                    )

            except Exception as e:
                stats["error"] += 1
                logger.error(f"Error re-enriching {company.get('name', slug)}: {e}")

    total_time = time.time() - start_time

    logger.info(f"\n{'='*70}")
    logger.info(f"✅ CLAUDE RE-ENRICHMENT COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Success: {stats['success']}")
    logger.info(f"Errors: {stats['error']}")
    logger.info(f"Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    logger.info(f"Rate: {len(failed)/total_time:.2f} companies/second")
    logger.info(f"{'='*70}\n")


if __name__ == "__main__":
    fix_claude_enrichments(max_workers=60)

#!/usr/bin/env python3
"""
Upgrade GPT-4o-mini enrichments to GPT-4o
Re-enrich all companies that used gpt-4o-mini for higher quality insights
"""

import json
import time
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from ai_insights_enricher import AIInsightsEnricher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upgrade_to_gpt4(max_workers=50):
    """Upgrade all gpt-4o-mini enrichments to gpt-4o"""

    workspace_dir = Path("/Users/yourox/AI-Workspace")
    enriched_dir = workspace_dir / "data" / "yc_enriched"
    companies_file = workspace_dir / "data" / "yc_companies" / "all_companies.json"

    # Load all companies
    with open(companies_file, 'r') as f:
        all_companies = {c['slug']: c for c in json.load(f)}

    # Find gpt-4o-mini enrichments to upgrade
    to_upgrade = []
    for enriched_file in enriched_dir.glob("*_enriched.json"):
        try:
            with open(enriched_file, 'r') as f:
                data = json.load(f)

            ai_insights = data.get('ai_insights', {})
            # Upgrade gpt-4o-mini OR missing/failed enrichments
            if (ai_insights.get('model_used') == 'gpt-4o-mini' or
                ai_insights.get('status') == 'error' or
                not data.get('phase8_complete')):

                slug = data.get('slug')
                if slug in all_companies:
                    full_company = {**all_companies[slug], **data}
                    to_upgrade.append((slug, enriched_file, full_company))

        except Exception as e:
            logger.warning(f"Error reading {enriched_file}: {e}")

    logger.info(f"Found {len(to_upgrade)} companies to upgrade to GPT-4o")

    if len(to_upgrade) == 0:
        logger.info("✅ All enrichments already use GPT-4o!")
        return

    # Initialize GPT-4o enricher
    enricher = AIInsightsEnricher()

    # Re-enrich in parallel
    stats = {"success": 0, "error": 0}
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}

        for slug, enriched_file, company in to_upgrade:
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

                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed
                    remaining = (len(to_upgrade) - i) / rate if rate > 0 else 0
                    logger.info(
                        f"[{i}/{len(to_upgrade)}] {i/len(to_upgrade)*100:.1f}% | "
                        f"Rate: {rate:.1f}/s | ETA: {remaining/60:.1f}m | "
                        f"Success: {stats['success']} | Errors: {stats['error']}"
                    )

            except Exception as e:
                stats["error"] += 1
                logger.error(f"Error upgrading {company.get('name', slug)}: {e}")

    total_time = time.time() - start_time

    logger.info(f"\n{'='*70}")
    logger.info(f"✅ GPT-4o UPGRADE COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Success: {stats['success']}")
    logger.info(f"Errors: {stats['error']}")
    logger.info(f"Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    logger.info(f"Rate: {len(to_upgrade)/total_time:.2f} companies/second")
    logger.info(f"{'='*70}\n")


if __name__ == "__main__":
    upgrade_to_gpt4(max_workers=50)

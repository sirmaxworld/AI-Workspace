#!/usr/bin/env python3
"""
Enrichment Engine - Main engine for computing enrichment metrics
Handles safe loading, versioning, and retroactive metric computation
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from metric_registry import MetricRegistry
from video_classifier import VideoTypeClassifier


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnrichmentEngine:
    """Main engine that applies metrics flexibly with safety checks"""

    VERSION = "1.0.0"

    def __init__(self, workspace_dir: Path = None):
        if workspace_dir is None:
            workspace_dir = Path("/Users/yourox/AI-Workspace")

        self.workspace_dir = workspace_dir
        self.insights_dir = workspace_dir / "data" / "business_insights"
        self.enriched_dir = workspace_dir / "data" / "enriched_insights"
        self.enriched_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.registry = MetricRegistry()
        self.classifier = VideoTypeClassifier()

        # Statistics
        self.stats = {
            "processed": 0,
            "cached": 0,
            "errors": 0,
            "skipped": 0
        }

        logger.info(f"Enrichment Engine v{self.VERSION} initialized")
        logger.info(f"Insights directory: {self.insights_dir}")
        logger.info(f"Enriched directory: {self.enriched_dir}")

    def get_insight_path(self, video_id: str) -> Path:
        """Get path to insight file"""
        return self.insights_dir / f"{video_id}_insights.json"

    def get_enriched_path(self, video_id: str) -> Path:
        """Get path to enriched file"""
        return self.enriched_dir / f"{video_id}_enriched.json"

    def load_insights(self, video_id: str) -> Optional[Dict]:
        """
        Safely load insights with error handling

        Returns:
            Insights dict or None if error
        """
        insight_file = self.get_insight_path(video_id)

        if not insight_file.exists():
            return None

        try:
            with open(insight_file, 'r') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {video_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {video_id}: {e}")
            return None

    def load_enriched(self, video_id: str) -> Optional[Dict]:
        """Load existing enriched data"""
        enriched_file = self.get_enriched_path(video_id)

        if not enriched_file.exists():
            return None

        try:
            with open(enriched_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading enriched data for {video_id}: {e}")
            return None

    def save_enriched(self, video_id: str, enriched_data: Dict):
        """Save enriched data"""
        enriched_file = self.get_enriched_path(video_id)

        try:
            with open(enriched_file, 'w') as f:
                json.dump(enriched_data, f, indent=2)
            logger.debug(f"Saved enriched data for {video_id}")
        except Exception as e:
            logger.error(f"Error saving enriched data for {video_id}: {e}")
            raise

    def is_complete_insight(self, insights: Dict) -> bool:
        """Check if insights data is complete"""
        # Must have meta field
        if 'meta' not in insights:
            return False

        # Must have video_id
        if 'video_id' not in insights.get('meta', {}):
            return False

        # Must have at least one data category
        data_categories = [
            'products_tools', 'business_strategies', 'problems_solutions',
            'startup_ideas', 'growth_tactics', 'ai_workflows',
            'trends_signals', 'actionable_quotes', 'key_statistics'
        ]

        has_data = any(
            key in insights and insights.get(key)
            for key in data_categories
        )

        return has_data

    def compute_all_metrics(self, insights: Dict, video_type: str) -> Dict:
        """
        Compute all applicable metrics for insights

        Args:
            insights: Full insights data
            video_type: Detected or manual video type

        Returns:
            Dict with all computed metrics
        """
        metrics = self.registry.get_metrics_for_type(video_type)

        universal_metrics = {}
        type_specific_metrics = {}

        # Compute metrics for each insight category
        insight_metrics = {}

        data_categories = {
            'products_tools': 'products',
            'business_strategies': 'strategies',
            'problems_solutions': 'problems',
            'startup_ideas': 'ideas',
            'mistakes_to_avoid': 'mistakes',
            'growth_tactics': 'tactics',
            'ai_workflows': 'workflows',
            'metrics_kpis': 'kpis',
            'trends_signals': 'trends',
            'actionable_quotes': 'quotes',
            'key_statistics': 'statistics'
        }

        for full_key, short_key in data_categories.items():
            if full_key in insights:
                items = insights[full_key]
                if isinstance(items, list):
                    insight_metrics[short_key] = []

                    for idx, item in enumerate(items):
                        item_metrics = {}

                        for metric in metrics:
                            try:
                                value = metric["compute_function"](item, full_key)

                                if metric["applies_to"] == ["all"]:
                                    item_metrics[metric["name"]] = value
                                else:
                                    item_metrics[metric["name"]] = value

                            except Exception as e:
                                logger.warning(
                                    f"Failed to compute {metric['name']} for {short_key}[{idx}]: {e}"
                                )

                        insight_metrics[short_key].append(item_metrics)

        # Compute video-level aggregates
        video_level_metrics = self._compute_video_level_metrics(insights, insight_metrics)

        return {
            "insight_metrics": insight_metrics,
            "video_level_metrics": video_level_metrics
        }

    def _compute_video_level_metrics(
        self,
        insights: Dict,
        insight_metrics: Dict
    ) -> Dict:
        """Compute aggregated video-level metrics"""

        aggregates = {}

        # Compute averages for each metric
        all_scores = {}

        for category, items in insight_metrics.items():
            for item in items:
                for metric_name, score in item.items():
                    if metric_name not in all_scores:
                        all_scores[metric_name] = []
                    all_scores[metric_name].append(score)

        # Calculate averages
        for metric_name, scores in all_scores.items():
            if scores:
                aggregates[f"avg_{metric_name}"] = round(sum(scores) / len(scores), 1)
                aggregates[f"max_{metric_name}"] = max(scores)
                aggregates[f"min_{metric_name}"] = min(scores)

        # Count high-value insights (score > 80)
        high_value_count = 0
        for category, items in insight_metrics.items():
            for item in items:
                if item.get('actionability_score', 0) > 80:
                    high_value_count += 1

        aggregates["high_value_insights"] = high_value_count

        # Total insights
        total_insights = sum(
            len(items) if isinstance(items, list) else 0
            for items in insights.values()
            if isinstance(items, list)
        )
        aggregates["total_insights"] = total_insights

        return aggregates

    def enrich_video(
        self,
        video_id: str,
        video_type: str = None,
        force: bool = False,
        retry: bool = True
    ) -> Dict[str, Any]:
        """
        Enrich a single video with all applicable metrics

        Args:
            video_id: Video to enrich
            video_type: Optional manual type override
            force: Force recompute even if already enriched
            retry: Retry once if file read fails

        Returns:
            Status dict with result info
        """
        # Check if insight file exists
        insight_file = self.get_insight_path(video_id)
        if not insight_file.exists():
            return {"status": "skipped", "reason": "not_extracted"}

        # Check if already enriched (and not forcing)
        if not force:
            enriched_file = self.get_enriched_path(video_id)
            if enriched_file.exists():
                try:
                    enriched_data = self.load_enriched(video_id)
                    if enriched_data and enriched_data.get('_version') == self.VERSION:
                        return {"status": "cached", "reason": "already_enriched"}
                except Exception:
                    pass  # Re-enrich if can't load

        # Try to load insights
        insights = self.load_insights(video_id)

        if insights is None:
            if retry:
                # File might be being written, retry once after 2 seconds
                logger.info(f"Retrying {video_id} in 2 seconds...")
                time.sleep(2)
                return self.enrich_video(video_id, video_type, force, retry=False)
            else:
                return {"status": "error", "reason": "cannot_load_insights"}

        # Validate completeness
        if not self.is_complete_insight(insights):
            return {"status": "skipped", "reason": "incomplete_data"}

        # Detect or use provided type
        if video_type is None:
            video_type, confidence, scores = self.classifier.classify_with_confidence(insights)
        else:
            confidence = 1.0  # Manual override
            scores = {}

        # Compute all metrics
        try:
            all_metrics = self.compute_all_metrics(insights, video_type)
        except Exception as e:
            logger.error(f"Error computing metrics for {video_id}: {e}")
            return {"status": "error", "reason": f"metric_computation_failed: {e}"}

        # Build enriched data structure
        enriched = {
            "video_id": video_id,
            "video_title": insights.get('meta', {}).get('title', ''),
            "video_type": video_type,
            "type_confidence": round(confidence, 3),
            "type_scores": {k: round(v, 1) for k, v in scores.items()},

            # Computed metrics
            **all_metrics,

            # Metadata
            "_version": self.VERSION,
            "_computed_at": datetime.now().isoformat(),
            "_metrics_applied": len(self.registry.get_metrics_for_type(video_type)),
            "_engine_version": self.VERSION,
            "_metric_registry_version": self.registry.VERSION,
            "_classifier_version": self.classifier.VERSION
        }

        # Save enriched data
        try:
            self.save_enriched(video_id, enriched)
        except Exception as e:
            return {"status": "error", "reason": f"save_failed: {e}"}

        return {
            "status": "success",
            "video_type": video_type,
            "confidence": confidence,
            "metrics_computed": enriched["_metrics_applied"]
        }

    def enrich_all_videos(self, force: bool = False, limit: int = None):
        """
        Enrich all videos in the insights directory

        Args:
            force: Force recompute even if already enriched
            limit: Optional limit on number of videos to process
        """
        print(f"\n{'='*70}")
        print(f"🧠 INTELLIGENCE ENRICHMENT ENGINE v{self.VERSION}")
        print(f"{'='*70}\n")

        # Find all insight files
        insight_files = list(self.insights_dir.glob("*_insights.json"))

        if limit:
            insight_files = insight_files[:limit]

        total = len(insight_files)

        print(f"📹 Found {total} insight files")

        # Check how many are already enriched
        enriched_count = sum(
            1 for f in insight_files
            if self.get_enriched_path(f.stem.replace('_insights', '')).exists()
        )

        print(f"✅ Already enriched: {enriched_count}")
        print(f"🔄 To process: {total - enriched_count if not force else total}\n")

        if force:
            print("⚡ Force mode: Re-computing all metrics\n")

        # Reset stats
        self.stats = {"processed": 0, "cached": 0, "errors": 0, "skipped": 0}

        start_time = time.time()

        for i, insight_file in enumerate(insight_files, 1):
            video_id = insight_file.stem.replace("_insights", "")

            elapsed = time.time() - start_time
            avg_time = elapsed / i if i > 0 else 0
            remaining = (total - i) * avg_time

            print(f"[{i}/{total}] {video_id} ", end="", flush=True)
            print(f"(avg: {avg_time:.1f}s, eta: {remaining:.0f}s) ", end="", flush=True)

            try:
                result = self.enrich_video(video_id, force=force)

                status = result["status"]

                if status == "success":
                    self.stats["processed"] += 1
                    vtype = result.get("video_type", "unknown")
                    conf = result.get("confidence", 0)
                    print(f"✅ {vtype} (conf: {conf:.2f})")

                elif status == "cached":
                    self.stats["cached"] += 1
                    print("⚡ cached")

                elif status == "skipped":
                    self.stats["skipped"] += 1
                    reason = result.get("reason", "unknown")
                    print(f"⏭️  skipped ({reason})")

                elif status == "error":
                    self.stats["errors"] += 1
                    reason = result.get("reason", "unknown")
                    print(f"❌ error ({reason})")

            except Exception as e:
                self.stats["errors"] += 1
                print(f"❌ exception: {e}")
                logger.exception(f"Exception processing {video_id}")

        total_time = time.time() - start_time

        print(f"\n{'='*70}")
        print(f"✅ ENRICHMENT COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Successfully processed: {self.stats['processed']}")
        print(f"⚡ Cached (skipped): {self.stats['cached']}")
        print(f"⏭️  Skipped: {self.stats['skipped']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print(f"⏱️  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"{'='*70}\n")

        return self.stats

    def add_new_metric_retroactively(
        self,
        metric_name: str,
        video_types: List[str] = None
    ):
        """
        Add a new metric and compute it for all existing videos

        Args:
            metric_name: Name of the metric to add
            video_types: Optional filter for video types (None = all)
        """
        print(f"\n{'='*70}")
        print(f"🔄 RETROACTIVE METRIC COMPUTATION: {metric_name}")
        print(f"{'='*70}\n")

        enriched_files = list(self.enriched_dir.glob("*_enriched.json"))
        total = len(enriched_files)

        print(f"📹 Found {total} enriched files")

        if video_types:
            print(f"🎯 Filtering for types: {', '.join(video_types)}\n")

        updated = 0
        skipped = 0

        for i, enriched_file in enumerate(enriched_files, 1):
            video_id = enriched_file.stem.replace("_enriched", "")

            try:
                # Load existing enriched data
                enriched_data = self.load_enriched(video_id)

                if not enriched_data:
                    skipped += 1
                    continue

                # Check if filtering by type
                if video_types and enriched_data.get('video_type') not in video_types:
                    skipped += 1
                    continue

                # Check if metric already exists
                if metric_name in enriched_data.get('video_level_metrics', {}):
                    skipped += 1
                    continue

                # Re-enrich with force
                result = self.enrich_video(video_id, force=True)

                if result["status"] == "success":
                    updated += 1
                    print(f"[{i}/{total}] {video_id} ✅ updated")
                else:
                    skipped += 1
                    print(f"[{i}/{total}] {video_id} ⏭️  skipped")

            except Exception as e:
                skipped += 1
                print(f"[{i}/{total}] {video_id} ❌ error: {e}")

        print(f"\n{'='*70}")
        print(f"✅ Updated: {updated}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"{'='*70}\n")

    def get_stats(self) -> Dict:
        """Get enrichment statistics"""
        return self.stats.copy()


def main():
    """CLI interface"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Business Intelligence Enrichment Engine")
    parser.add_argument('command', nargs='?', default='enrich',
                       choices=['enrich', 'enrich-all', 'stats', 'test'],
                       help='Command to run')
    parser.add_argument('--video-id', help='Video ID to enrich')
    parser.add_argument('--type', help='Manual video type override')
    parser.add_argument('--force', action='store_true', help='Force recompute')
    parser.add_argument('--limit', type=int, help='Limit number of videos')

    args = parser.parse_args()

    engine = EnrichmentEngine()

    if args.command == 'enrich':
        if not args.video_id:
            print("Error: --video-id required for 'enrich' command")
            sys.exit(1)

        result = engine.enrich_video(args.video_id, video_type=args.type, force=args.force)
        print(json.dumps(result, indent=2))

    elif args.command == 'enrich-all':
        engine.enrich_all_videos(force=args.force, limit=args.limit)

    elif args.command == 'stats':
        stats = engine.get_stats()
        print(json.dumps(stats, indent=2))

    elif args.command == 'test':
        # Test on first 3 videos
        print("Testing enrichment on first 3 videos...\n")
        engine.enrich_all_videos(limit=3, force=True)


if __name__ == "__main__":
    main()

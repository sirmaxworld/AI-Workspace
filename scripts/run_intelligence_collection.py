#!/usr/bin/env python3
"""
Intelligence Collection Orchestrator
Runs the complete data collection pipeline with quality checks
"""

import sys
import time
import subprocess
from datetime import datetime

def run_script(script_name: str, description: str):
    """Run a Python script and report results"""
    print(f"\n{'='*80}")
    print(f"  {description}")
    print(f"{'='*80}")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, f"/Users/yourox/AI-Workspace/scripts/{script_name}"],
            capture_output=False,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"\n✅ {description} completed in {elapsed/60:.1f} minutes")
            return True
        else:
            print(f"\n❌ {description} failed with code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print(f"\n⚠️  {description} timed out after 1 hour")
        return False
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}")
        return False

def main():
    """Main orchestration"""
    print("\n" + "="*80)
    print(" "*20 + "INTELLIGENCE COLLECTION PIPELINE")
    print("="*80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    pipeline_start = time.time()

    # Pipeline steps
    steps = [
        ("quality_check.py", "Quality Checks", True),  # Required
        ("github_repo_collector.py", "GitHub Repository Collection", True),  # Required
        ("github_pattern_extractor.py", "GitHub Pattern Extraction", True),  # Required
        ("oss_repo_collector.py", "OSS Repository Collection", True),  # Required
        ("oss_commercial_scorer.py", "OSS Commercial Scoring", True),  # Required
    ]

    results = []

    for script, description, required in steps:
        success = run_script(script, description)
        results.append((description, success))

        if not success and required:
            print(f"\n❌ PIPELINE FAILED: {description} is required but failed")
            break

        # Sleep between steps
        time.sleep(2)

    pipeline_elapsed = time.time() - pipeline_start

    # Summary
    print(f"\n{'='*80}")
    print("  PIPELINE SUMMARY")
    print(f"{'='*80}")

    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status} - {description}")

    all_passed = all(success for _, success in results)

    print(f"\n{'='*80}")
    if all_passed:
        print(f"✅ PIPELINE COMPLETED SUCCESSFULLY")
    else:
        print(f"❌ PIPELINE FAILED")

    print(f"   Total time: {pipeline_elapsed/60:.1f} minutes")
    print(f"   Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

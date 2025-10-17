#!/usr/bin/env python3
"""
Complete Video Processing Pipeline
1. Extract transcript using Browserbase (bypasses IP blocks)
2. Extract business intelligence using Claude AI
3. Save searchable, categorized data
"""

import sys
import subprocess
from pathlib import Path


def run_full_pipeline(video_id: str):
    """
    Run complete pipeline: Transcript + Business Intelligence extraction
    """

    print(f"\n{'='*70}")
    print(f"🚀 FULL VIDEO PROCESSING PIPELINE")
    print(f"{'='*70}\n")
    print(f"📹 Video ID: {video_id}\n")

    # Step 1: Extract transcript with Browserbase
    print(f"{'='*70}")
    print(f"STEP 1: TRANSCRIPT EXTRACTION (Browserbase)")
    print(f"{'='*70}\n")

    result = subprocess.run(
        ['python3', 'scripts/browserbase_transcript_extractor.py', video_id],
        capture_output=False
    )

    if result.returncode != 0:
        print(f"\n❌ Transcript extraction failed!")
        return False

    # Check if transcript was created
    transcript_file = Path(f"data/transcripts/{video_id}_full.json")
    if not transcript_file.exists():
        print(f"\n❌ Transcript file not found: {transcript_file}")
        return False

    print(f"\n✅ Step 1 Complete: Transcript extracted\n")

    # Step 2: Extract business intelligence
    print(f"{'='*70}")
    print(f"STEP 2: BUSINESS INTELLIGENCE EXTRACTION (Claude AI)")
    print(f"{'='*70}\n")

    result = subprocess.run(
        ['python3', 'scripts/business_intelligence_extractor.py', video_id],
        capture_output=False
    )

    if result.returncode != 0:
        print(f"\n❌ Business intelligence extraction failed!")
        return False

    # Check if insights were created
    insights_file = Path(f"data/business_insights/{video_id}_insights.json")
    if not insights_file.exists():
        print(f"\n❌ Insights file not found: {insights_file}")
        return False

    print(f"\n✅ Step 2 Complete: Business intelligence extracted\n")

    # Success summary
    print(f"\n{'='*70}")
    print(f"✅ PIPELINE COMPLETE!")
    print(f"{'='*70}")
    print(f"📁 Transcript: {transcript_file}")
    print(f"📁 Insights: {insights_file}")
    print(f"\n💡 Data is now searchable with:")
    print(f"   - Products & Tools (with sentiment)")
    print(f"   - Business Problems & Solutions")
    print(f"   - Startup Ideas")
    print(f"   - Growth Tactics")
    print(f"   - AI Workflows")
    print(f"   - Target Markets")
    print(f"   - Emerging Trends")
    print(f"   - Key Statistics & Quotes")
    print(f"{'='*70}\n")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python full_video_pipeline.py VIDEO_ID")
        print("\nExample:")
        print("  python full_video_pipeline.py 5FokzkHTpc0")
        sys.exit(1)

    video_id = sys.argv[1]
    success = run_full_pipeline(video_id)

    sys.exit(0 if success else 1)

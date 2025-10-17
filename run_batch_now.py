#!/usr/bin/env python3
"""
Direct batch processing script - processes 5 new videos immediately
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add the script directory to path
sys.path.insert(0, '/Users/yourox/AI-Workspace/scripts')
sys.path.insert(0, '/Users/yourox/AI-Workspace')

# Now import our modules
from dotenv import load_dotenv
load_dotenv('/Users/yourox/AI-Workspace/.env')

# Import processing components
from process_youtube_batch import YouTubeBatchProcessor

async def run_batch():
    """Run batch processing for 5 new videos"""
    print("\n" + "="*80)
    print("🚀 STARTING YOUTUBE BATCH PROCESSING")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target: 5 new videos from Greg Isenberg channel")
    print("="*80 + "\n")

    try:
        # Initialize processor
        processor = YouTubeBatchProcessor()

        # Process batch
        result = await processor.process_batch(
            channel_url="@GregIsenberg",
            max_videos=5,
            skip_existing=True,
            filter_shorts=True
        )

        # Save result for analysis
        result_file = Path('/Users/yourox/AI-Workspace/latest_batch_result.json')
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n💾 Full result saved to: {result_file}")

        return result

    except Exception as e:
        print(f"\n❌ Error during batch processing: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def main():
    """Main execution"""
    # Run the async batch processing
    result = asyncio.run(run_batch())

    # Print final status
    if result.get('status') == 'error':
        print(f"\n❌ Batch processing failed: {result.get('message')}")
        return 1
    else:
        print(f"\n✅ Batch processing completed successfully!")

        # Print summary if available
        if 'summary' in result:
            summary = result['summary']
            print(f"\n📊 Final Summary:")
            print(f"  • Attempted: {summary.get('attempted', 0)}")
            print(f"  • Successful: {summary.get('successful', 0)}")
            print(f"  • Failed: {summary.get('failed', 0)}")
            print(f"  • Success Rate: {summary.get('success_rate', 'N/A')}")

        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
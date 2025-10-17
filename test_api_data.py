#!/usr/bin/env python3
"""
Test script to verify API data loading functionality
"""

import json
import os
from pathlib import Path
import glob
from collections import defaultdict

# Configuration
DATA_DIR = Path("data/business_insights")
TRANSCRIPTS_DIR = Path("data/transcripts")

def test_data_loading():
    """Test if the API can load and process data correctly"""

    print("=" * 60)
    print("TESTING API DATA LOADING")
    print("=" * 60)

    # Check directories exist
    print(f"\n1. Checking directories:")
    print(f"   Data directory: {DATA_DIR}")
    print(f"   Exists: {DATA_DIR.exists()}")
    print(f"   Transcripts directory: {TRANSCRIPTS_DIR}")
    print(f"   Exists: {TRANSCRIPTS_DIR.exists()}")

    # Load all JSON files
    json_files = glob.glob(str(DATA_DIR / "*.json"))
    print(f"\n2. Found {len(json_files)} insight files")

    if not json_files:
        print("   ERROR: No JSON files found!")
        return

    # Load and analyze data structure
    all_data = defaultdict(list)
    meta_info = []
    errors = []

    print("\n3. Loading and analyzing data:")
    for i, file_path in enumerate(json_files[:5], 1):  # Sample first 5 files
        file_name = Path(file_path).name
        print(f"\n   File {i}: {file_name}")

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Check structure
            print(f"   - Keys found: {list(data.keys())[:5]}...")

            # Count items per category
            for key, value in data.items():
                if key == "meta":
                    meta_info.append(value)
                    print(f"   - Meta: {value.get('title', 'No title')[:50]}...")
                elif key == "market_intelligence":
                    if isinstance(value, dict):
                        if "target_markets" in value:
                            all_data["target_markets"].extend(value["target_markets"])
                        if "problems_validated" in value:
                            all_data["problems_validated"].extend(value["problems_validated"])
                elif isinstance(value, list):
                    all_data[key].extend(value)
                    print(f"   - {key}: {len(value)} items")

        except Exception as e:
            errors.append(f"{file_name}: {str(e)}")
            print(f"   ERROR: {e}")

    # Summary statistics
    print("\n4. Data Summary:")
    print(f"   Total files processed: {min(5, len(json_files))}")
    print(f"   Total categories found: {len(all_data)}")
    print("\n   Items per category:")
    for key, items in list(all_data.items())[:10]:
        print(f"   - {key}: {len(items)} items")

    if errors:
        print(f"\n5. Errors encountered: {len(errors)}")
        for error in errors[:3]:
            print(f"   - {error}")

    # Test sample data access
    print("\n6. Testing data access:")

    # Try to get some products
    products = all_data.get("products_tools", [])
    if products:
        print(f"   Products found: {len(products)}")
        if products:
            sample = products[0]
            print(f"   Sample product:")
            for key in list(sample.keys())[:3]:
                print(f"     - {key}: {sample.get(key, 'N/A')}")
    else:
        print("   No products found")

    # Try to get startup ideas
    ideas = all_data.get("startup_ideas", [])
    if ideas:
        print(f"\n   Startup ideas found: {len(ideas)}")
        if ideas:
            sample = ideas[0]
            print(f"   Sample idea:")
            for key in list(sample.keys())[:3]:
                value = sample.get(key, 'N/A')
                if isinstance(value, str):
                    value = value[:100] + "..." if len(value) > 100 else value
                print(f"     - {key}: {value}")
    else:
        print("   No startup ideas found")

    # Check for transcripts
    print("\n7. Checking transcripts:")
    transcript_files = glob.glob(str(TRANSCRIPTS_DIR / "*_full.json"))
    print(f"   Found {len(transcript_files)} transcript files")

    if transcript_files:
        # Test loading a transcript
        sample_transcript = transcript_files[0]
        print(f"   Testing transcript: {Path(sample_transcript).name}")
        try:
            with open(sample_transcript, 'r') as f:
                transcript_data = json.load(f)

            if 'transcript' in transcript_data:
                segments = transcript_data.get('transcript', {}).get('segments', [])
                print(f"   - Segments: {len(segments)}")
                if segments:
                    print(f"   - First segment: {segments[0].get('text', '')[:50]}...")
            else:
                print("   - No transcript key found")

        except Exception as e:
            print(f"   ERROR loading transcript: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

    return all_data

if __name__ == "__main__":
    data = test_data_loading()

    if data:
        print(f"\nData successfully loaded with {sum(len(v) for v in data.values())} total items")
    else:
        print("\nNo data loaded - check error messages above")
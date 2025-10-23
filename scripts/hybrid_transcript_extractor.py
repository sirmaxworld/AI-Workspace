#!/usr/bin/env python3
"""
Hybrid Transcript Extractor - 3-Tier Fallback Strategy
Designed to handle videos of ANY length (1min - 2hr+)

Tier 1: YouTube Transcript API (fast, free, no browser)
Tier 2: Browserbase with extended timeout (for protected/special videos)
Tier 3: Skip and log (genuinely unavailable)
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Import both extraction methods
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from browserbase_transcript_extractor import extract_youtube_transcript as browserbase_extract

load_dotenv('/Users/yourox/AI-Workspace/.env')


class HybridTranscriptExtractor:
    """
    Smart transcript extractor with fallback chain:
    1. Try YouTube Transcript API (fastest)
    2. Fall back to Browserbase if API fails
    3. Return error if both fail
    """

    def __init__(self):
        self.stats = {
            'api_success': 0,
            'browserbase_success': 0,
            'both_failed': 0
        }

    def extract_transcript(self, video_id: str, prefer_api: bool = True) -> Dict:
        """
        Extract transcript using hybrid approach

        Args:
            video_id: YouTube video ID
            prefer_api: If True, try API first. If False, use Browserbase only.

        Returns:
            Dict with transcript data and method used
        """

        print(f"\n{'='*70}")
        print(f"🎯 HYBRID EXTRACTION: {video_id}")
        print(f"{'='*70}\n")

        # TIER 1: Try YouTube Transcript API first (fast, no browser)
        if prefer_api:
            print(f"📡 Method 1/2: YouTube Transcript API...")
            api_result = self._try_api_extraction(video_id)

            if api_result.get('status') == 'success':
                print(f"✅ API extraction successful!")
                self.stats['api_success'] += 1
                return api_result

            print(f"⚠️  API failed: {api_result.get('error')}")
            print(f"   Falling back to Browserbase...\n")

        # TIER 2: Fall back to Browserbase (slower, but handles edge cases)
        print(f"🌐 Method 2/2: Browserbase (extended timeout for long videos)...")
        browserbase_result = self._try_browserbase_extraction(video_id)

        if browserbase_result.get('status') == 'success':
            print(f"✅ Browserbase extraction successful!")
            self.stats['browserbase_success'] += 1
            return browserbase_result

        # TIER 3: Both methods failed
        print(f"❌ Both methods failed")
        self.stats['both_failed'] += 1

        return {
            'video_id': video_id,
            'status': 'error',
            'error': 'Transcript not available (tried API + Browserbase)',
            'api_error': api_result.get('error'),
            'browserbase_error': browserbase_result.get('error')
        }

    def _try_api_extraction(self, video_id: str) -> Dict:
        """Try extraction via YouTube Transcript API"""
        try:
            # Get transcript (create instance first)
            api = YouTubeTranscriptApi()
            fetched_transcript = api.fetch(video_id)

            if not fetched_transcript:
                return {
                    'video_id': video_id,
                    'status': 'error',
                    'error': 'No transcript data returned from API'
                }

            # Convert FetchedTranscript to list and then to our format
            transcript_list = list(fetched_transcript)
            segments = []

            for snippet in transcript_list:
                segments.append({
                    'text': snippet.text,
                    'start': int(snippet.start),
                    'duration': int(snippet.duration)
                })

            print(f"   ✅ {len(segments)} segments extracted via API")

            return {
                'video_id': video_id,
                'title': 'Unknown Title',  # API doesn't provide title
                'channel': 'Unknown Channel',
                'transcript': {
                    'segments': segments,
                    'segment_count': len(segments)
                },
                'method': 'youtube_transcript_api',
                'status': 'success'
            }

        except TranscriptsDisabled:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': 'Transcripts disabled for this video'
            }
        except NoTranscriptFound:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': 'No transcript found'
            }
        except Exception as e:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': f'API error: {str(e)}'
            }

    def _try_browserbase_extraction(self, video_id: str) -> Dict:
        """
        Try extraction via Browserbase with extended timeout
        Note: Browserbase extractor needs to be modified to accept longer timeout
        """
        try:
            result = browserbase_extract(video_id)
            return result
        except Exception as e:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': f'Browserbase error: {str(e)}'
            }

    def save_transcript(self, video_id: str, data: dict, output_dir: str = "/Users/yourox/AI-Workspace/data/transcripts"):
        """Save transcript to JSON file"""
        output_path = Path(output_dir) / f"{video_id}_full.json"

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Saved to: {output_path}")
        return output_path

    def print_stats(self):
        """Print extraction statistics"""
        total = sum(self.stats.values())
        if total == 0:
            return

        print(f"\n{'='*70}")
        print(f"📊 EXTRACTION STATISTICS")
        print(f"{'='*70}")
        print(f"Total attempts: {total}")
        print(f"✅ API success: {self.stats['api_success']} ({self.stats['api_success']/total*100:.1f}%)")
        print(f"🌐 Browserbase success: {self.stats['browserbase_success']} ({self.stats['browserbase_success']/total*100:.1f}%)")
        print(f"❌ Both failed: {self.stats['both_failed']} ({self.stats['both_failed']/total*100:.1f}%)")
        print(f"{'='*70}\n")


def test_hybrid_extractor(video_id: str = '3q1QvEkbbyk'):
    """Test the hybrid extractor"""
    print(f"\n{'='*70}")
    print(f"🧪 TESTING HYBRID TRANSCRIPT EXTRACTOR")
    print(f"{'='*70}\n")

    extractor = HybridTranscriptExtractor()
    result = extractor.extract_transcript(video_id)

    print(f"\n{'='*70}")
    print(f"📋 RESULT:")
    print(f"{'='*70}")
    print(f"Status: {result.get('status')}")
    print(f"Method: {result.get('method', 'N/A')}")
    if result.get('status') == 'success':
        print(f"Segments: {result.get('transcript', {}).get('segment_count', 0)}")
    else:
        print(f"Error: {result.get('error')}")
    print(f"{'='*70}\n")

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python hybrid_transcript_extractor.py VIDEO_ID")
        print("\nTesting with sample Tier 2-3 video...")
        test_hybrid_extractor()
    else:
        video_id = sys.argv[1]

        extractor = HybridTranscriptExtractor()
        result = extractor.extract_transcript(video_id)

        if result.get('status') == 'success':
            extractor.save_transcript(video_id, result)
            print(f"\n✅ SUCCESS!")
        else:
            print(f"\n❌ FAILED: {result.get('error')}")

        extractor.print_stats()

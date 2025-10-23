#!/usr/bin/env python3
"""
VPN rotation extractor - automatically rotates ProtonVPN servers
Requires ProtonVPN CLI to be installed
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
except ImportError:
    print("❌ Please install: pip3 install youtube-transcript-api")
    exit(1)


class VPNRotationExtractor:
    """Extract transcripts with automatic VPN rotation"""

    def __init__(self):
        self.output_dir = Path("/Users/yourox/AI-Workspace/data/transcripts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.failures_per_ip = 0
        self.max_failures_before_rotation = 10

        # ProtonVPN servers to rotate through
        self.vpn_servers = [
            'US-FREE#1',
            'US-FREE#2',
            'US-FREE#3',
            'NL-FREE#1',
            'JP-FREE#1'
        ]
        self.current_server_index = 0

    def check_vpn_cli(self) -> bool:
        """Check if ProtonVPN CLI is installed"""
        try:
            subprocess.run(['protonvpn-cli', '--version'],
                          capture_output=True, check=True)
            return True
        except:
            return False

    def rotate_vpn(self) -> bool:
        """Rotate to next VPN server"""
        if not self.check_vpn_cli():
            print("⚠️  ProtonVPN CLI not installed - skipping rotation")
            return False

        self.current_server_index = (self.current_server_index + 1) % len(self.vpn_servers)
        server = self.vpn_servers[self.current_server_index]

        print(f"\n🔄 Rotating VPN to: {server}")
        try:
            # Disconnect current
            subprocess.run(['protonvpn-cli', 'd'], capture_output=True)
            time.sleep(2)

            # Connect to new server
            subprocess.run(['protonvpn-cli', 'c', server],
                          capture_output=True, check=True)
            time.sleep(3)

            print(f"✅ Connected to {server}")
            self.failures_per_ip = 0
            return True

        except Exception as e:
            print(f"❌ VPN rotation failed: {e}")
            return False

    def extract_transcript(self, video_id: str) -> dict:
        """Extract transcript (same as local extractor)"""
        try:
            api = YouTubeTranscriptApi()
            transcript = api.get_transcript(video_id)

            segments = []
            for item in transcript:
                segments.append({
                    'text': item['text'],
                    'start': int(item['start']),
                    'duration': int(item['duration'])
                })

            self.failures_per_ip = 0  # Reset on success
            return {
                'video_id': video_id,
                'transcript': {
                    'segments': segments,
                    'segment_count': len(segments)
                },
                'method': 'youtube_transcript_api_vpn_rotated',
                'status': 'success'
            }

        except Exception as e:
            error_str = str(e).lower()
            if 'blocked' in error_str or 'ip' in error_str:
                self.failures_per_ip += 1

            return {
                'video_id': video_id,
                'status': 'error',
                'error': str(e)
            }

    def process_video(self, video_id: str, index: int, total: int) -> bool:
        """Process single video with auto-rotation"""

        # Check if already exists
        output_file = self.output_dir / f"{video_id}_full.json"
        if output_file.exists():
            print(f"[{index}/{total}] ⏭️  {video_id}: Already exists")
            return True

        # Check if we should rotate
        if self.failures_per_ip >= self.max_failures_before_rotation:
            print(f"\n⚠️  {self.failures_per_ip} failures detected - rotating VPN...")
            self.rotate_vpn()

        print(f"[{index}/{total}] 🔄 {video_id}: Extracting...")
        result = self.extract_transcript(video_id)

        if result['status'] == 'success':
            # Save transcript
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)

            segments = result['transcript']['segment_count']
            print(f"[{index}/{total}] ✅ {video_id}: {segments} segments")
            return True
        else:
            print(f"[{index}/{total}] ❌ {video_id}: {result['error']}")
            return False


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🔄 VPN ROTATION EXTRACTOR")
    print("="*70)

    extractor = VPNRotationExtractor()

    # Check if VPN CLI is available
    if not extractor.check_vpn_cli():
        print("\n⚠️  ProtonVPN CLI not detected!")
        print("   Install: https://github.com/ProtonVPN/linux-cli")
        print("\n   This script will run without rotation (manual connection required)")
        response = input("\n   Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            exit(0)
    else:
        print("\n✅ ProtonVPN CLI detected - will auto-rotate on failures")

    # Load failed videos
    failed_file = Path("/tmp/tier2_3_failed.txt")
    if not failed_file.exists():
        print(f"\n❌ Failed videos file not found: {failed_file}")
        exit(1)

    with open(failed_file) as f:
        video_ids = [line.strip() for line in f if line.strip()]

    print(f"\n📋 Processing {len(video_ids)} failed videos")
    print(f"🔄 Will rotate VPN every {extractor.max_failures_before_rotation} failures")
    print("="*70 + "\n")

    success = 0
    failed = 0
    start = time.time()

    # Process sequentially to allow for VPN rotation
    for i, video_id in enumerate(video_ids, 1):
        if extractor.process_video(video_id, i, len(video_ids)):
            success += 1
        else:
            failed += 1

        # Small delay between requests
        time.sleep(0.5)

    elapsed = time.time() - start

    print("\n" + "="*70)
    print("✅ COMPLETE")
    print("="*70)
    print(f"Time: {elapsed/60:.1f} minutes")
    print(f"Success: {success}/{len(video_ids)} ({success/len(video_ids)*100:.1f}%)")
    print(f"Failed: {failed}/{len(video_ids)} ({failed/len(video_ids)*100:.1f}%)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

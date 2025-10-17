#!/usr/bin/env python3
"""
Rate Limiting Test Script
Tests Browserbase with rapid consecutive requests to verify rate limiting bypass
"""

import time
import json
from pathlib import Path
from browserbase_transcript_extractor import extract_youtube_transcript, save_transcript

def test_rate_limiting(num_tests: int = 5):
    """
    Test rate limiting by extracting the same video multiple times rapidly

    This simulates rapid requests that would normally trigger YouTube's rate limiting
    """
    # Use an existing video ID for testing
    test_video_id = "5FokzkHTpc0"  # Seena Rez video

    print(f"\n{'='*80}")
    print(f"🔥 RATE LIMITING TEST")
    print(f"{'='*80}\n")
    print(f"Testing with {num_tests} consecutive requests...")
    print(f"Video ID: {test_video_id}")
    print(f"Expected: All requests should succeed (Browserbase bypasses rate limits)\n")

    results = []
    total_start = time.time()

    for i in range(1, num_tests + 1):
        print(f"\n--- Request {i}/{num_tests} ---")

        request_start = time.time()

        try:
            # Extract transcript via Browserbase
            result = extract_youtube_transcript(test_video_id)

            request_time = time.time() - request_start

            if result.get('status') == 'success':
                transcript_count = len(result.get('transcript', {}).get('segments', []))
                comments_count = result.get('comments', {}).get('count', 0)

                print(f"✅ SUCCESS ({request_time:.1f}s)")
                print(f"   Segments: {transcript_count}")
                print(f"   Comments: {comments_count}")

                results.append({
                    'request_num': i,
                    'success': True,
                    'time': request_time,
                    'segments': transcript_count,
                    'comments': comments_count,
                    'error': None
                })
            else:
                print(f"❌ FAILED: {result.get('error')}")
                results.append({
                    'request_num': i,
                    'success': False,
                    'time': request_time,
                    'error': result.get('error')
                })

        except Exception as e:
            request_time = time.time() - request_start
            print(f"❌ EXCEPTION: {e}")
            results.append({
                'request_num': i,
                'success': False,
                'time': request_time,
                'error': str(e)
            })

        # Small delay between requests
        if i < num_tests:
            print("⏳ Waiting 1 second...")
            time.sleep(1)

    total_time = time.time() - total_start

    # Analyze results
    print(f"\n{'='*80}")
    print(f"📊 RATE LIMITING TEST RESULTS")
    print(f"{'='*80}\n")

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"✅ Successful requests: {len(successful)}/{num_tests}")
    print(f"❌ Failed requests: {len(failed)}/{num_tests}")

    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        total_comments = sum(r.get('comments', 0) for r in successful)

        print(f"\n⏱️  Performance:")
        print(f"   Average time per request: {avg_time:.1f}s")
        print(f"   Total time: {total_time:.1f}s")
        print(f"   Requests per minute: {(len(successful) / total_time) * 60:.1f}")

        print(f"\n💬 Comments Extraction:")
        print(f"   Total comments: {total_comments}")
        print(f"   Average per request: {total_comments / len(successful):.1f}")

    if failed:
        print(f"\n❌ Failures:")
        for r in failed:
            print(f"   Request {r['request_num']}: {r.get('error', 'Unknown error')}")

    # Verdict
    success_rate = (len(successful) / num_tests) * 100
    print(f"\n{'='*80}")

    if success_rate >= 80:
        print(f"🎉 RATE LIMITING BYPASS: ✅ WORKING")
        print(f"   Success rate: {success_rate:.0f}%")
        print(f"   Browserbase is successfully bypassing YouTube rate limits!")
    elif success_rate >= 50:
        print(f"⚠️  RATE LIMITING BYPASS: PARTIAL")
        print(f"   Success rate: {success_rate:.0f}%")
        print(f"   Some requests are failing - may need investigation")
    else:
        print(f"❌ RATE LIMITING BYPASS: FAILED")
        print(f"   Success rate: {success_rate:.0f}%")
        print(f"   Rate limiting is still being enforced")

    print(f"{'='*80}\n")

    # Save results
    results_file = Path("/Users/yourox/AI-Workspace/data/rate_limiting_test_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'num_tests': num_tests,
            'success_rate': success_rate,
            'total_time': total_time,
            'results': results
        }, f, indent=2)

    print(f"📊 Results saved to: {results_file}\n")

    return success_rate >= 80


if __name__ == "__main__":
    import sys

    num_tests = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    print(f"\n🔥 Testing rate limiting with {num_tests} consecutive requests...")
    print(f"This will take approximately {num_tests * 15} seconds\n")

    success = test_rate_limiting(num_tests)

    sys.exit(0 if success else 1)

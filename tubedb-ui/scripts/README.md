# TubeDB Video Extraction Scripts

## Quick Start

### Extract a single video (with paid proxy):
```bash
# Option 1: Configure proxy once, then use for all extractions
cp scripts/proxy-config.example.py scripts/proxy-config.py
# Edit proxy-config.py with your credentials
python3 scripts/extract-video-paid-proxy.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Option 2: Pass proxy directly
python3 scripts/extract-video-paid-proxy.py "URL" "http://user:pass@proxy.com:8080"
```

### Extract without proxy (may hit rate limits):
```bash
python3 scripts/extract-video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Recommended Proxy Services

### For bypassing YouTube rate limits, use residential proxies:

**Affordable Options ($25-75/month):**
- **IPRoyal** (https://iproyal.com/) - $1.75/GB residential, good for YouTube
- **SmartProxy** (https://smartproxy.com/) - $8.5/GB residential, reliable
- **Webshare** (https://webshare.io/) - $2.99/GB residential, newer service

**Premium Options ($100-300/month):**
- **Bright Data** (https://brightdata.com/) - Best success rate, pricey
- **Oxylabs** (https://oxylabs.io/) - Enterprise-grade, very reliable

**Setup Example (SmartProxy):**
```bash
# 1. Copy config template
cp scripts/proxy-config.example.py scripts/proxy-config.py

# 2. Edit proxy-config.py and add:
PROXY_URL = "http://user-USERNAME:PASSWORD@gate.smartproxy.com:7000"

# 3. Run extraction
python3 scripts/extract-video-paid-proxy.py "https://youtube.com/watch?v=5FokzkHTpc0"
```

## Troubleshooting

### Rate Limiting (HTTP 429)

If you encounter "Too Many Requests" errors:

**Option 1: Wait and Retry**
```bash
# Wait a few minutes, then try again
sleep 300 && python3 scripts/extract-video.py "URL"
```

**Option 2: Use VPN or Different IP**
- Connect to a VPN
- Retry the extraction

**Option 3: Use YouTube API Key**
```bash
# Set your API key
export YOUTUBE_API_KEY="your_key_here"
python3 scripts/extract-video-api.py "URL"
```

**Option 4: Manual Extraction**
1. Go to https://youtubetranscript.com/
2. Paste the video URL
3. Download the transcript as JSON
4. Use the manual import script:
```bash
python3 scripts/import-transcript.py VIDEO_ID transcript.json
```

## Alternative Methods

### Method 1: Browser Extension
1. Install "YouTube Transcript" Chrome extension
2. Visit the video page
3. Export transcript
4. Import using our script

### Method 2: YouTube Studio (for your own videos)
1. Go to YouTube Studio
2. Navigate to Subtitles
3. Download the transcript
4. Import using our script

### Method 3: Third-party Services
- https://youtubetranscript.com/
- https://www.rev.com/
- https://downsub.com/

## For Video: 5FokzkHTpc0

**Title**: "how I built a $2.7M brand using a.i (my actual product, website, ads, viral videos)"
**Duration**: ~15 minutes

**To extract this video later:**
```bash
# Try again in a few minutes
python3 scripts/extract-video.py "https://www.youtube.com/watch?v=5FokzkHTpc0"

# Or use manual method:
# 1. Get transcript from https://youtubetranscript.com/
# 2. Save as 5FokzkHTpc0_transcript.json
# 3. Run: python3 scripts/import-transcript.py 5FokzkHTpc0 5FokzkHTpc0_transcript.json
```

## Batch Processing

Extract multiple videos:
```bash
python3 scripts/batch-extract.py videos.txt
```

Where `videos.txt` contains one URL per line.

## API Endpoint

You can also use the Next.js API endpoint:

```bash
curl -X POST http://localhost:4000/api/video/add \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

## Data Format

Videos are added to: `/Users/yourox/AI-Workspace/data/transcripts/batch_20251015_201035.json`

Format:
```json
{
  "video_id": "string",
  "title": "string",
  "agent_id": 99,
  "method": "youtube_captions",
  "transcript": {
    "language": "en",
    "segments": [...],
    "segment_count": number
  },
  "qc_verification": {
    "quality_score": 0.0,
    "key_topics": [],
    "summary": "Pending analysis"
  }
}
```

## Next Steps After Adding Video

1. Refresh the TubeDB UI at http://localhost:4000
2. The new video will appear in the grid
3. Click on it to view the transcript
4. Add QC verification and analysis as needed

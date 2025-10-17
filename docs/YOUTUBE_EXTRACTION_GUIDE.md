# YouTube Extraction Pipeline - Complete Guide

**Created:** October 15, 2025
**Status:** Production Ready

---

## 🎯 Overview

The enhanced YouTube extraction pipeline provides:

1. **Channel Scraping** - Extract videos from any YouTube channel
2. **Shorts Filtering** - Automatically exclude YouTube Shorts (< 60s videos)
3. **Transcript Extraction** - Use YouTube captions or Whisper API fallback
4. **Quality Control** - AI agent validates extraction quality
5. **Semantic Storage** - Store in Mem0 for semantic search

---

## 📦 Components

### 1. Channel Extractor (`youtube_channel_extractor.py`)

Fetches video metadata from YouTube channels with filtering.

**Features:**
- Supports `@username` or full channel URLs
- Filters out YouTube Shorts automatically
- Caches results for 24 hours
- Returns rich metadata (duration, views, likes, tags, thumbnails)

**Usage:**
```bash
# Extract 50 videos from Greg Isenberg's channel
python scripts/youtube_channel_extractor.py @GregIsenberg --max-videos 50

# Include Shorts
python scripts/youtube_channel_extractor.py @GregIsenberg --include-shorts

# Only last 30 days
python scripts/youtube_channel_extractor.py @GregIsenberg --days-back 30

# Custom output location
python scripts/youtube_channel_extractor.py @GregIsenberg -o data/my_videos.json
```

### 2. Transcript Extractor (`youtube_transcriber_pro.py`)

Hybrid transcription system using YouTube captions + Whisper API fallback.

**Features:**
- Tries YouTube captions first (free, fast)
- Falls back to Whisper API if no captions
- Semantic chunking with timestamps
- Stores in Mem0 with rich metadata
- Caches transcripts locally

**Usage:**
```bash
# Transcribe single video
python scripts/youtube_transcriber_pro.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Search transcripts
python scripts/youtube_transcriber_pro.py --search "AI agents"
```

### 3. QC Pipeline (`youtube_qc_pipeline.py`)

Complete end-to-end pipeline with AI quality control.

**Features:**
- Orchestrates extraction + transcription + validation
- CrewAI agent reviews each transcript
- Generates comprehensive quality reports
- Validates completeness, quality, content value
- Provides actionable recommendations

**Usage:**
```bash
# Full pipeline with QC (default)
python scripts/youtube_qc_pipeline.py @GregIsenberg --max-videos 50

# Skip quality control (faster)
python scripts/youtube_qc_pipeline.py @GregIsenberg --skip-qc

# Include Shorts
python scripts/youtube_qc_pipeline.py @GregIsenberg --include-shorts
```

### 4. Quick Start Script

**Easiest way to run:**
```bash
./scripts/run_greg_isenberg_extraction.sh
```

This runs the full 50-video pipeline with QC automatically.

---

## 📊 Quality Control Metrics

The QC agent evaluates each transcript on:

### Completeness Score (0.0 - 1.0)
- Does transcript length match video duration?
- Are there obvious gaps or truncation?

### Quality Score (0.0 - 1.0)
- Is text coherent and properly formatted?
- Are there transcription errors or gibberish?

### Content Value Score (0.0 - 1.0)
- Does it contain meaningful information?
- Is it worth storing in knowledge base?

### Overall Rating
- **Excellent** - Perfect transcription, high value
- **Good** - Minor issues, still valuable
- **Fair** - Some problems, marginal value
- **Poor** - Major issues, consider re-extraction

### QC Report Includes:
- Issues detected (truncation, errors, low quality)
- Strengths (completeness, clarity, value)
- Recommendations (retry with Whisper, manual review, etc.)
- Pass/Fail decision

---

## 🗂️ Output Structure

### Extracted Videos JSON
```json
{
  "extracted_at": "2025-10-15T10:30:00",
  "total_videos": 50,
  "channel": "Greg Isenberg",
  "videos": [
    {
      "id": "VIDEO_ID",
      "url": "https://youtube.com/watch?v=VIDEO_ID",
      "title": "Video Title",
      "channel": "Greg Isenberg",
      "duration": 1234,
      "duration_formatted": "20:34",
      "upload_date": "20251010",
      "view_count": 50000,
      "description": "...",
      "tags": ["AI", "business"],
      "is_short": false
    }
  ]
}
```

### QC Report JSON
```json
{
  "pipeline_run": {
    "channel": "Greg Isenberg",
    "started_at": "2025-10-15T10:00:00",
    "duration_formatted": "15m 30s"
  },
  "extraction_summary": {
    "total_videos_found": 50,
    "transcribed_successfully": 48,
    "success_rate": "96.0%"
  },
  "quality_control": {
    "videos_reviewed": 48,
    "passed_qc": 46,
    "qc_pass_rate": "95.8%",
    "quality_distribution": {
      "excellent": 35,
      "good": 11,
      "fair": 2,
      "poor": 0
    },
    "average_completeness_score": "0.97",
    "average_quality_score": "0.95"
  },
  "qc_reports": [
    {
      "video_id": "VIDEO_ID",
      "video_title": "Title",
      "overall_quality": "excellent",
      "completeness_score": 0.98,
      "quality_score": 0.97,
      "content_value_score": 0.95,
      "passed_qc": true,
      "issues": [],
      "strengths": ["Complete", "Clear", "Valuable"],
      "recommendations": []
    }
  ]
}
```

---

## 🔍 Searching Transcripts

After extraction, transcripts are stored in Mem0 for semantic search.

### Via Python:
```python
from youtube_transcriber_pro import YouTubeTranscriberPro

transcriber = YouTubeTranscriberPro()
results = transcriber.search("AI agents for business", limit=10)

for result in results:
    print(f"{result['video_title']}")
    print(f"  Channel: {result['channel']}")
    print(f"  Link: {result['timestamp_url']}")
    print(f"  Relevance: {result['relevance']}")
```

### Via MCP Server:
Use the Claude Desktop MCP server to query transcripts directly in conversations.

---

## ⚙️ Configuration

### Shorts Filtering
By default, videos under 60 seconds are excluded. To change:

In `youtube_channel_extractor.py`:
```python
self.shorts_max_duration = 60  # Change to your preference
```

### Transcription Method
Priority order:
1. YouTube captions (free, instant)
2. Whisper API (costs ~$0.006/minute)

To disable Whisper fallback:
```python
transcriber = YouTubeTranscriberPro(use_whisper_fallback=False)
```

### Cache Duration
Transcripts are cached indefinitely. Videos metadata cached for 24 hours.

To clear cache:
```bash
rm -rf /Users/yourox/AI-Workspace/data/transcripts/*.json
rm -rf /Users/yourox/AI-Workspace/data/youtube_channels/*_videos.json
```

---

## 💰 Cost Estimates

### Per Video Costs:
- **YouTube Captions**: FREE (90% of videos)
- **Whisper API**: ~$0.006/minute (~$0.36 for 1-hour video)
- **Quality Control**: ~$0.01 per video (Claude API)

### 50 Videos Example:
- Assuming 30min average duration
- 45 videos with captions (FREE)
- 5 videos need Whisper ($0.006 × 30min × 5 = $0.90)
- QC for all 50 ($0.01 × 50 = $0.50)
- **Total: ~$1.40**

---

## 🚨 Troubleshooting

### "No transcript available"
- Video has no captions and Whisper fallback disabled
- Solution: Enable Whisper fallback or skip video

### "Rate limited"
- YouTube/Google throttling requests
- Solution: Add delays, use proxies, run overnight

### "Whisper transcription failed"
- Audio download failed or API error
- Solution: Check OpenAI API key, try manual download

### QC Agent Errors
- CrewAI/Claude API issues
- Solution: Check API keys, retry with `--skip-qc`

---

## 📈 Performance

### Speed:
- **Channel extraction**: ~2-3 minutes for 50 videos
- **Transcription (captions)**: ~5-10 seconds per video
- **Transcription (Whisper)**: ~1-2 minutes per video
- **Quality control**: ~10-15 seconds per video

### Full 50-Video Pipeline:
- Best case (all captions): ~10-15 minutes
- Worst case (all Whisper): ~2-3 hours
- Typical (mixed): ~20-30 minutes

---

## 🎯 Next Steps

### Integrate with Knowledge Pipeline
```python
from knowledge_pipeline import KnowledgePipeline

pipeline = KnowledgePipeline()
pipeline.run('youtube_content')  # Domain key
```

### Add to Orchestrator
Edit `scripts/orchestrator.py` to include YouTube extraction in domain workflows.

### Schedule Regular Updates
```bash
# Cron job: Daily extraction of latest videos
0 2 * * * cd /Users/yourox/AI-Workspace && ./scripts/run_greg_isenberg_extraction.sh
```

---

## 📚 Related Documentation

- `README.md` - Main project overview
- `VISION_AND_ROADMAP.md` - Project goals and phases
- `DATA_SOURCES.md` - All data source integrations
- `YOUTUBE_KNOWLEDGE_BASE.md` - YouTube-specific knowledge system

---

**Last Updated:** October 15, 2025
**Version:** 2.0 (Enhanced with QC)

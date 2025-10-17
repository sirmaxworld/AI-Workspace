# Documentation Index

## Active Documentation

### Quick Start
- [README.md](../README.md) - Main project overview

### Current Systems
- **Transcription & Search:**
  - [TRANSCRIPTION_SUCCESS_REPORT.md](active/TRANSCRIPTION_SUCCESS_REPORT.md) - Parallel extraction results (49 videos, 6 min)
  - [FAST_TRANSCRIPTION_ARCHITECTURE.md](active/FAST_TRANSCRIPTION_ARCHITECTURE.md) - System architecture
  - [SCALING_ACTION_PLAN.md](active/SCALING_ACTION_PLAN.md) - Scaling strategy
  - [YOUTUBE_PIPELINE_READY.md](active/YOUTUBE_PIPELINE_READY.md) - Pipeline overview

- **Setup Guides:**
  - [SYSTEM_READY.md](active/SYSTEM_READY.md) - System status
  - [MCP_SETUP_COMPLETE.md](active/MCP_SETUP_COMPLETE.md) - MCP configuration
  - [SECURE_MEMORY_GUIDE.md](active/SECURE_MEMORY_GUIDE.md) - Memory system guide
  - [QUICK_START_MEMORY.md](active/QUICK_START_MEMORY.md) - Quick memory setup
  - [REF_MCP_INSTALLATION.md](active/REF_MCP_INSTALLATION.md) - MCP installation reference
  - [YOUTUBE_COOKIES_SETUP.md](YOUTUBE_COOKIES_SETUP.md) - Rate limit bypass

## Archived Documentation

Historical documentation and old session notes moved to `docs/archive/`:
- Architecture redesigns and planning docs
- Security audits and analysis
- Old session summaries
- Cleanup reports

## Key Files by Use Case

**Setting up the system:**
1. Start with [README.md](../README.md)
2. Follow [SYSTEM_READY.md](active/SYSTEM_READY.md)
3. Configure MCP: [MCP_SETUP_COMPLETE.md](active/MCP_SETUP_COMPLETE.md)

**Using transcription:**
1. [TRANSCRIPTION_SUCCESS_REPORT.md](active/TRANSCRIPTION_SUCCESS_REPORT.md) - See what's possible
2. [FAST_TRANSCRIPTION_ARCHITECTURE.md](active/FAST_TRANSCRIPTION_ARCHITECTURE.md) - Understand the system
3. Run: `python3 scripts/parallel_transcriber.py 50`

**Using semantic search:**
1. Check setup: `python3 scripts/simple_vector_ingest.py stats`
2. Search: `python3 scripts/simple_vector_ingest.py search "your query"`

**Troubleshooting:**
- Rate limits: [YOUTUBE_COOKIES_SETUP.md](YOUTUBE_COOKIES_SETUP.md)
- Memory issues: [SECURE_MEMORY_GUIDE.md](active/SECURE_MEMORY_GUIDE.md)

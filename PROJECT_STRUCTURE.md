# Project Structure

## Root Directory
```
AI-Workspace/
├── README.md                    # Main project overview
├── requirements.txt             # Python dependencies
├── .env                        # API keys (gitignored)
├── .gitignore                  # Git exclusions
│
├── scripts/                    # All executable scripts (17 active)
├── docs/                       # All documentation
├── data/                       # All data files
├── config/                     # Configuration files
├── archive/                    # Old versions & backups
└── logs/                       # Log files
```

## Organized Structure

### `/scripts/` - 17 Active Scripts
**Core Transcription & Search:**
- `parallel_transcriber.py` - Fast parallel extraction (49 videos in 6 min)
- `simple_vector_ingest.py` - Qdrant semantic search
- `youtube_channel_extractor.py` - Channel video fetching
- `youtube_qc_pipeline.py` - Quality control pipeline

**Data Processing:**
- `source_adapters.py` - Unified data adapters
- `quality_control.py` - QC validation
- `quick_extract_to_mem0.py` - Quick workflow

**Infrastructure:**
- `orchestrator.py` - Main orchestration
- `knowledge_pipeline.py` - Knowledge processing
- `data_collection_crew.py` - CrewAI workflows

**Memory & Integration:**
- `claude_memory_ultimate.py` - Memory system
- `create_apple_notes.py` - Apple Notes sync
- `quick_apple_notes.py` - Quick notes

**Utilities:**
- `ingest_transcripts_to_vector_db.py` - Vector ingestion
- `youtube_knowledge.py` - Knowledge base
- `youtube_transcriber_pro.py` - Pro transcriber
- `QUICK_FIXES.sh` - Quick fixes script

### `/docs/` - Organized Documentation

**Active Documentation (`docs/active/`):**
- Transcription guides & reports
- System setup & configuration
- Memory system guides
- MCP setup instructions

**Archive (`docs/archive/`):**
- Old architecture docs
- Historical session notes
- Audit reports
- Deprecated guides

**Root Documentation:**
- `INDEX.md` - Documentation index
- `YOUTUBE_COOKIES_SETUP.md` - Rate limit bypass
- Other setup guides

### `/data/` - Data Storage
```
data/
├── transcripts/                 # 49 video transcripts (JSON)
├── youtube_qdrant_direct/       # Vector database (387 chunks)
├── greg_isenberg_videos.json    # Video metadata (50 videos)
├── qc_reports/                  # Quality control reports
└── extraction_reports/          # Extraction stats
```

### `/archive/` - Historical Files
```
archive/
├── 2025-10-14_project_history/  # Previous cleanup
└── 2025-10-15_scripts_cleanup/  # Today's cleanup (7 old scripts)
    └── README.md                # Cleanup documentation
```

## Quick Navigation

**Start here:**
- Main docs: `docs/INDEX.md`
- Project README: `README.md`

**Run transcription:**
```bash
python3 scripts/parallel_transcriber.py 50
```

**Search knowledge:**
```bash
python3 scripts/simple_vector_ingest.py search "your query"
```

**Check status:**
```bash
python3 scripts/simple_vector_ingest.py stats
```

## File Organization Rules

✅ **Keep in root:** Only README.md, requirements.txt, .env, .gitignore
✅ **Scripts:** All .py executables in `/scripts/`
✅ **Docs:** All .md documentation in `/docs/`
✅ **Data:** All data files in `/data/`
✅ **Archive:** Old versions in `/archive/YYYY-MM-DD_description/`

## Last Updated
October 15, 2025 - Full cleanup and reorganization

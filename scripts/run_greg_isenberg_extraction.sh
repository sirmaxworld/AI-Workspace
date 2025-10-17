#!/bin/bash
#
# Run Greg Isenberg Channel Full Extraction (50 videos with QC)
# This script orchestrates the complete YouTube extraction pipeline
#

set -e  # Exit on error

WORKSPACE="/Users/yourox/AI-Workspace"
PYTHON="/usr/local/bin/python3.11"

echo "================================================================================"
echo "  GREG ISENBERG YOUTUBE CHANNEL - FULL EXTRACTION PIPELINE"
echo "================================================================================"
echo ""
echo "This will:"
echo "  1. Extract latest 50 videos from @GregIsenberg channel (excluding Shorts)"
echo "  2. Transcribe all videos using YouTube captions or Whisper API"
echo "  3. Run quality control validation with AI agent"
echo "  4. Generate comprehensive quality report"
echo "  5. Store transcripts in Mem0 for semantic search"
echo ""
echo "Estimated time: 20-30 minutes"
echo ""
read -p "Press ENTER to start or Ctrl+C to cancel..."
echo ""

cd "$WORKSPACE"

# Run the pipeline
echo "🚀 Starting pipeline..."
echo ""

$PYTHON scripts/youtube_qc_pipeline.py @GregIsenberg --max-videos 50

echo ""
echo "================================================================================"
echo "✅ PIPELINE COMPLETE!"
echo "================================================================================"
echo ""
echo "Results saved to:"
echo "  - Transcripts: $WORKSPACE/data/transcripts/"
echo "  - QC Reports: $WORKSPACE/data/qc_reports/"
echo "  - Mem0 Database: $WORKSPACE/data/youtube_qdrant/"
echo ""
echo "To search transcripts:"
echo "  python scripts/youtube_transcriber_pro.py --search 'your query'"
echo ""

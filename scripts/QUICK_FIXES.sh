#!/bin/bash
#
# Quick Fixes - Resolve Dependencies
#

set -e

echo "================================================================================"
echo "  QUICK FIXES - Installing Dependencies"
echo "================================================================================"
echo ""

# Fix 1: YouTube Transcript API
echo "🔧 Fix 1: Reinstalling youtube-transcript-api..."
/usr/local/bin/python3.11 -m pip uninstall -y youtube-transcript-api 2>/dev/null || true
/usr/local/bin/python3.11 -m pip install youtube-transcript-api
echo "✅ youtube-transcript-api installed"
echo ""

# Fix 2: FFmpeg
echo "🔧 Fix 2: Installing ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg already installed: $(ffmpeg -version | head -1)"
else
    echo "Installing ffmpeg via Homebrew..."
    brew install ffmpeg
    echo "✅ ffmpeg installed"
fi
echo ""

# Verify installations
echo "================================================================================"
echo "  Verification"
echo "================================================================================"
echo ""

echo "Python packages:"
/usr/local/bin/python3.11 -m pip list | grep -i "youtube-transcript-api"
echo ""

echo "FFmpeg:"
ffmpeg -version | head -1
echo ""

echo "================================================================================"
echo "✅ ALL FIXES COMPLETE!"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "  1. Test extraction:"
echo "     python scripts/source_adapters.py youtube --handle @GregIsenberg --max-items 2"
echo ""
echo "  2. Run full pipeline with transcription (this may take 10-15 minutes):"
echo "     python scripts/youtube_transcriber_pro.py https://www.youtube.com/watch?v=IjYKIqvTyXg"
echo ""
echo "  3. Update MCP config (optional - for Claude Desktop access):"
echo "     See MCP_SETUP_COMPLETE.md"
echo ""

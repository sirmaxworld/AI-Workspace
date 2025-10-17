#!/bin/bash
#
# Auto-Enrichment Script
# Automatically enrich new videos as they're added
#
# Usage:
#   ./auto_enrich.sh          # Run enrichment once
#   ./auto_enrich.sh --watch  # Watch for new files and auto-enrich
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSIGHTS_DIR="/Users/yourox/AI-Workspace/data/business_insights"
ENRICHED_DIR="/Users/yourox/AI-Workspace/data/enriched_insights"
SUMMARIES_DIR="/Users/yourox/AI-Workspace/data/video_summaries"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}🤖 AUTO-ENRICHMENT SYSTEM${NC}"
echo -e "${BLUE}======================================================================${NC}"

# Function to run full enrichment pipeline
run_enrichment() {
    echo -e "\n${GREEN}🧠 Step 1/3: Running enrichment engine...${NC}"
    cd "$SCRIPT_DIR"
    python3 enrichment_engine.py enrich-all

    echo -e "\n${GREEN}📝 Step 2/3: Generating video summaries...${NC}"
    python3 video_summarizer.py

    echo -e "\n${GREEN}🔍 Step 3/3: Updating meta-intelligence...${NC}"
    python3 meta_intelligence.py

    echo -e "\n${GREEN}✅ Enrichment pipeline complete!${NC}"
}

# Function to check for new videos
check_new_videos() {
    local insight_count=$(ls -1 "$INSIGHTS_DIR"/*_insights.json 2>/dev/null | wc -l | tr -d ' ')
    local enriched_count=$(ls -1 "$ENRICHED_DIR"/*_enriched.json 2>/dev/null | wc -l | tr -d ' ')

    local new_count=$((insight_count - enriched_count))

    if [ $new_count -gt 0 ]; then
        echo -e "${YELLOW}📹 Found $new_count new videos to enrich${NC}"
        return 0
    else
        echo -e "${GREEN}✅ All videos are enriched ($enriched_count total)${NC}"
        return 1
    fi
}

# Watch mode
if [ "$1" == "--watch" ]; then
    echo -e "${BLUE}👁️  Watch mode enabled - monitoring for new videos...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"

    while true; do
        if check_new_videos; then
            echo -e "${GREEN}🚀 Starting enrichment...${NC}"
            run_enrichment
        fi

        echo -e "\n${BLUE}⏳ Waiting 60 seconds before next check...${NC}"
        sleep 60
    done
else
    # Single run mode
    if check_new_videos; then
        echo -e "${GREEN}🚀 Starting enrichment...${NC}"
        run_enrichment
    fi
fi

echo -e "\n${BLUE}======================================================================${NC}"
echo -e "${GREEN}✅ DONE!${NC}"
echo -e "${BLUE}======================================================================${NC}"

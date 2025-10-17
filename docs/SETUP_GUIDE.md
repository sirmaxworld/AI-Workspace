# 🚀 Multi-Domain Knowledge Base System - Setup Guide

## 📋 Overview

This is your **complete AI-powered knowledge management system** with:
- ✅ **8 specialized knowledge domains** (3D printing, robotics, AI trends, etc.)
- ✅ **Multi-source data collection** (YouTube, research papers, social media, blogs)
- ✅ **CrewAI agent orchestration** (5 specialized agents per domain)
- ✅ **Vector database storage** (Qdrant for semantic search)
- ✅ **Claude memory integration** (never lose context)
- ✅ **Affordable data sources** ($0-69/month)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Master Control)            │
│  • Manages all 8 knowledge domains                          │
│  • Schedules data collection crews                          │
│  • Monitors system health                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│   DOMAIN 1   │   ...    │   DOMAIN 8   │
│  Robotics    │          │  AI Trends   │
└──────┬───────┘          └──────┬───────┘
       │                          │
       ▼                          ▼
┌─────────────────────────────────────────┐
│     DATA COLLECTION CREW (5 Agents)     │
│  1. YouTube Researcher                  │
│  2. Academic Researcher                 │
│  3. Social Media Analyst                │
│  4. Industry News Monitor               │
│  5. Knowledge Synthesizer               │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────┐        ┌──────────────┐
│ SOURCES │        │ VECTOR DB    │
│ (APIs)  │   →    │ (Qdrant)     │
│         │        │ Searchable   │
└─────────┘        └──────────────┘
```

---

## 🗂️ Directory Structure

```
AI-Workspace/
├── .env                          # API keys (NEVER commit!)
├── requirements.txt              # Python dependencies
│
├── config/
│   └── knowledge_domains.json    # 8 domain definitions
│
├── scripts/
│   ├── orchestrator.py           # Master pipeline CLI
│   ├── data_collection_crew.py   # CrewAI agents with toolchain + JSON schema
│   ├── knowledge_pipeline.py     # Validates, dedupes, ingests curated knowledge
│   ├── claude_memory_ultimate.py # Dual-layer memory (JSON + Mem0)
│   ├── youtube_knowledge.py      # YouTube ingestion
│   └── youtube_transcriber_pro.py # Transcript downloader
│
├── data/
│   ├── qdrant/                   # Vector database
│   │   ├── kb_robotics/          # Robotics collection
│   │   ├── kb_3d_printing/       # 3D printing collection
│   │   └── ... (8 collections)
│   │
│   ├── claude_memory_json/       # Claude conversation memory
│   │   └── memories.json
│   │
│   ├── transcripts/              # YouTube transcripts
│   │   ├── videos.json
│   │   └── *_full.txt
│   │
│   ├── crew_results/             # Legacy crew outputs (still populated)
│   └── pipeline_runs/            # Pipeline artifacts per domain/run
│
└── docs/
    ├── DATA_SOURCES.md           # API documentation
    └── SETUP_GUIDE.md            # This file
```

---

## ⚙️ Step 1: Install Dependencies

```bash
cd /Users/yourox/AI-Workspace

# Install all required packages
pip install -r requirements.txt

# Or install manually:
pip install crewai crewai-tools mem0ai anthropic openai
pip install qdrant-client chromadb
pip install tavily-python exa-py firecrawl-py
pip install arxiv semanticscholar praw youtube-transcript-api
pip install pandas numpy python-dotenv
```

---

## 🔑 Step 2: Set Up API Keys

Edit `/Users/yourox/AI-Workspace/.env`:

```bash
# Essential (you already have these)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...

# Search APIs (get free tiers from their websites)
TAVILY_API_KEY=tvly-...              # https://tavily.com (1k free/month)
BRAVE_SEARCH_API_KEY=...             # https://brave.com/search/api (2k free/month)
SERPER_API_KEY=...                   # https://serper.dev (2.5k free/month)

# Optional Premium APIs
FIRECRAWL_API_KEY=fc-...             # https://firecrawl.dev ($0-49/month)
EXA_API_KEY=...                      # https://exa.ai ($0-20/month)

# Social Media
REDDIT_CLIENT_ID=...                 # https://reddit.com/prefs/apps
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=AI-Workspace/1.0

# Optional: Twitter/X (very limited free tier)
TWITTER_BEARER_TOKEN=...             # https://developer.twitter.com
```

### 🎁 **Free Tiers Summary:**
- Tavily: 1,000 searches/month
- Brave: 2,000 searches/month
- Serper: 2,500 searches/month
- arXiv: Unlimited
- Reddit: Rate-limited but functional
- YouTube Transcript API: Unlimited

**Total cost with free tiers only: $0/month** ✅

---

## 🎯 Step 3: Understanding the 8 Knowledge Domains

### Your Knowledge Domains:

| Domain Key | Name | Priority | Collection Name |
|------------|------|----------|----------------|
| `3d_printing` | 3D Printing & Additive Manufacturing | HIGH | `kb_3d_printing` |
| `robotics` | Robotics & Automation | HIGH | `kb_robotics` |
| `manufacturing_automation` | Manufacturing & Industry 4.0 | MEDIUM | `kb_manufacturing` |
| `visual_ai` | Visual AI & Computer Vision | VERY HIGH | `kb_visual_ai` |
| `multimedia` | Multimedia Production | MEDIUM | `kb_multimedia` |
| `mental_health` | Mental Health & Psychology | HIGH | `kb_mental_health` |
| `business_strategy` | Business Strategy | HIGH | `kb_business` |
| `ai_trends` | AI Trends & Emerging Tech | VERY HIGH | `kb_ai_trends` |

Each domain has its own:
- Curated YouTube channels
- Research paper sources
- Social media communities
- Industry blogs

---

## 🚀 Step 4: Using the System

### **A. List All Domains**
```bash
python3 scripts/orchestrator.py list
```

### **B. View Domain Details**
```bash
python3 scripts/orchestrator.py info robotics
```

### **C. Run Autonomous Pipeline for One Domain**
```bash
# Collect + validate + ingest AI trends knowledge
python3 scripts/orchestrator.py collect ai_trends
```

Artifacts are saved to `data/pipeline_runs/ai_trends/<timestamp>/` and include:
- `raw_run_summary.json` – crew outputs prior to validation
- `validated_outputs.json` – schema-checked payloads
- `pipeline_summary.json` – ingestion report (dedupe/ingested counts)

### **D. Trigger Pipeline Directly (advanced)**
```bash
python3 scripts/knowledge_pipeline.py ai_trends
```

### **E. Legacy Commands (still available)**
- `python3 scripts/orchestrator.py list`
- `python3 scripts/orchestrator.py info robotics`
- `python3 scripts/orchestrator.py stats`

---

## 🧠 Step 5: Claude Memory Integration

### **Load Memory at Start of Conversation:**
```bash
python3 scripts/claude_memory_hybrid.py load
```
Copy the output and paste it into Claude chat.

### **Save Memory at End of Conversation:**
```bash
python3 scripts/claude_memory_hybrid.py save "Today we set up the multi-domain knowledge base system with 8 domains and CrewAI orchestration"
```

### **Quick Access Aliases** (add to ~/.zshrc):
```bash
alias claude-load="python3 /Users/yourox/AI-Workspace/scripts/claude_memory_hybrid.py load"
alias claude-save="python3 /Users/yourox/AI-Workspace/scripts/claude_memory_hybrid.py save"
alias kb-collect="python3 /Users/yourox/AI-Workspace/scripts/orchestrator.py collect"
alias kb-stats="python3 /Users/yourox/AI-Workspace/scripts/orchestrator.py stats"
```

Then use:
```bash
claude-load
kb-collect robotics
kb-stats
claude-save "collected robotics data"
```

---

## 📊 Step 6: Understanding Data Flow

### **1. Data Collection (CrewAI Agents)**
```
YouTube Agent → Finds videos → Extracts metadata
Academic Agent → Searches papers → Extracts abstracts
Social Agent → Monitors Reddit/Twitter → Analyzes sentiment
Industry Agent → Reads blogs → Summarizes news
Synthesizer → Combines all → Structures for database
```

### **2. Storage (Qdrant Vector DB)**
```
Raw data → Chunked → Embedded (OpenAI) → Stored in Qdrant
```

### **3. Search & Retrieval**
```
Your query → Embedded → Vector similarity search → Top results
```

---

## 🎯 Example Workflow

### **Day 1: Setup High-Priority Domains**
```bash
# Collect robotics knowledge
python3 scripts/orchestrator.py collect robotics

# Collect AI trends
python3 scripts/orchestrator.py collect ai_trends

# Check results
python3 scripts/orchestrator.py stats
```

### **Day 2: Ingest YouTube Transcripts**
```bash
# Download transcripts for a robotics channel
python3 scripts/youtube_transcriber_pro.py

# Ingest into knowledge base
python3 scripts/youtube_knowledge.py ingest

# Search the knowledge base
python3 scripts/youtube_knowledge.py search "ROS navigation"
```

### **Ongoing: Update Knowledge**
```bash
# Update high-priority domains weekly
python3 scripts/orchestrator.py collect-all --priority very_high

# Update everything monthly
python3 scripts/orchestrator.py collect-all
```

---

## 🔍 How Each Component Works

### **Orchestrator (`orchestrator.py`)**
- Master control script
- Lists domains
- Triggers collection crews
- Shows statistics
- Manages scheduling

### **Data Collection Crew (`data_collection_crew.py`)**
- 5 AI agents per domain
- Collects from multiple sources
- Synthesizes data
- Outputs structured JSON

### **Knowledge Pipeline (`knowledge_pipeline.py`)**
- Executes CrewAI workflow with structured output enforcement
- Validates JSON via `jsonschema` (auto fallback if missing)
- Deduplicates knowledge items and persists indices in `data/knowledge_index`
- Optionally ingests curated content into Mem0 per domain user ID

### **YouTube System**
- `youtube_transcriber_pro.py`: Downloads transcripts
- `youtube_knowledge.py`: Ingests into vector DB
- Searchable via semantic search

### **Claude Memory (`claude_memory_ultimate.py`)**
- Dual-layer memory (fast JSON + semantic Mem0)
- Thread-safe access for MCP and scripts
- Updated MCP servers expose memory + curated knowledge resources

---

## 🎁 Recommended Getting Started Path

### **Phase 1: Quick Win (Day 1) ✅**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up free API keys (Tavily + Brave)
nano .env

# 3. Test with one domain
python3 scripts/orchestrator.py collect ai_trends

# 4. Check results
python3 scripts/orchestrator.py stats
```

### **Phase 2: Full Setup (Week 1) ✅**
```bash
# Collect all high-priority domains
python3 scripts/orchestrator.py collect-all --priority high

# Set up YouTube ingestion
python3 scripts/youtube_transcriber_pro.py
python3 scripts/youtube_knowledge.py ingest

# Test Claude memory
python3 scripts/claude_memory_hybrid.py save "System setup complete"
```

### **Phase 3: Production (Ongoing) ✅**
```bash
# Daily: Update very high priority
python3 scripts/orchestrator.py collect-all --priority very_high

# Weekly: Update all domains
python3 scripts/orchestrator.py collect-all

# Always: Use Claude memory
claude-load  # At start
claude-save "summary"  # At end
```

---

## 💡 Pro Tips

### **1. Start Small**
Begin with 1-2 domains (e.g., ai_trends + robotics) before scaling to all 8.

### **2. Use Free Tiers First**
You can accomplish a LOT with just the free API tiers.

### **3. Schedule Regular Updates**
Set up cron jobs for automatic updates:
```bash
# Add to crontab -e
0 9 * * * cd /Users/yourox/AI-Workspace && python3 scripts/orchestrator.py collect-all --priority very_high
```

### **4. Monitor Costs**
Track API usage in your provider dashboards.

### **5. Iterate on Domains**
Customize `config/knowledge_domains.json` to add/remove sources.

---

## 🆘 Troubleshooting

### **Issue: API Key Not Found**
```bash
# Check .env file
cat /Users/yourox/AI-Workspace/.env

# Make sure it's loaded
python3 -c "from dotenv import load_dotenv; load_dotenv('/Users/yourox/AI-Workspace/.env'); import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

### **Issue: Import Error**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### **Issue: Qdrant Not Starting**
```bash
# Check Qdrant directory
ls -la /Users/yourox/AI-Workspace/data/qdrant/

# Create if missing
mkdir -p /Users/yourox/AI-Workspace/data/qdrant
```

### **Issue: CrewAI Agent Timeout**
- Increase timeout in `data_collection_crew.py`
- Use smaller test datasets first
- Check API rate limits

---

## 📈 Next Steps

1. ✅ Install dependencies
2. ✅ Set up API keys (at least free tiers)
3. ✅ Test one domain collection
4. ✅ Review results
5. ⏳ Scale to more domains
6. ⏳ Set up automation
7. ⏳ Integrate with your workflow

---

## 🎉 You're Ready!

Your multi-domain knowledge base system is ready to go. Start with one domain and scale from there!

**Questions?** Check:
- `docs/DATA_SOURCES.md` for API details
- `config/knowledge_domains.json` for domain configuration
- Individual script files for implementation details

**Happy knowledge building!** 🚀

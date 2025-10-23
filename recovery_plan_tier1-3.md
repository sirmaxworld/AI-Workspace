# Video Extraction Recovery Plan - Tier 1-3 Channels
**Created:** October 17, 2025 16:13
**Status:** Recovery after Cursor crash

---

## 📊 Current Situation

### What Happened
- Cursor crashed while processing videos from 3 top-tier business channels
- **3 transcripts** were successfully extracted before crash
- **0 insights** generated for those 3 (crash occurred during BI extraction)
- **297 videos** still need complete processing

### Data Sources (300 videos total)
1. **Alex Hormozi** - 100 videos (Tier 1: Operator)
2. **Dan Martell** - 100 videos (Tier 1: SaaS Scaling)
3. **SaaStr** - 100 videos (Tier 1: B2B SaaS)

### Files Status
- ✅ Channel data collected: `data/youtube_channels/*.json`
- ✅ 3 transcripts extracted (incomplete - need insights)
- ❌ 297 videos need: transcript + insights
- ✅ Processing script ready: `scripts/batch_extract_videos_enhanced.py`

---

## 💰 Model Cost Analysis

### Option 1: Claude Sonnet 4 (Current)
**Per Video:**
- Transcript extraction: Browserbase only ($0.0242)
- BI extraction: ~4K tokens input, ~1K tokens output
  - Input: 4,000 tokens × $3/1M = $0.012
  - Output: 1,000 tokens × $15/1M = $0.015
- **Total per video: ~$0.051**

**For 300 videos:**
- Transcript: $7.26 (Browserbase)
- BI extraction: $8.10 (Sonnet 4)
- **Total: $15.36**
- **Time estimate:** ~5-6 hours (300 videos × ~60-80s avg, 10 parallel workers)

---

### Option 2: Claude Haiku 3.5
**Per Video:**
- Transcript extraction: $0.0242 (same Browserbase)
- BI extraction: ~4K tokens input, ~1K tokens output
  - Input: 4,000 tokens × $1/1M = $0.004
  - Output: 1,000 tokens × $5/1M = $0.005
- **Total per video: ~$0.033**

**For 300 videos:**
- Transcript: $7.26 (Browserbase)
- BI extraction: $2.70 (Haiku 3.5)
- **Total: $9.96**
- **Time estimate:** ~4-5 hours (faster model)
- **Savings: $5.40 vs Sonnet 4 (35% cheaper)**

---

### Option 3: Claude Haiku 4.5 (Newest, Best Price/Performance)
**Per Video:**
- Transcript extraction: $0.0242 (same Browserbase)
- BI extraction: ~4K tokens input, ~1K tokens output
  - Input: 4,000 tokens × $1/1M = $0.004
  - Output: 1,000 tokens × $5/1M = $0.005
- **Total per video: ~$0.033**

**For 300 videos:**
- Transcript: $7.26 (Browserbase)
- BI extraction: $2.70 (Haiku 4.5)
- **Total: $9.96**
- **Time estimate:** ~3-4 hours (newest, fastest Haiku)
- **Savings: $5.40 vs Sonnet 4 (35% cheaper)**
- **Quality:** Comparable to Haiku 3.5, but faster

---

## 🎯 Recommended Approach: HYBRID STRATEGY

### Phase 1: Quality Test (10 videos) - Use Sonnet 4
**Purpose:** Establish quality baseline
- Extract 10 videos from each channel (30 total)
- Use current Sonnet 4 model
- **Cost:** 30 × $0.051 = $1.53
- **Time:** ~30 minutes
- Manually review quality of insights

### Phase 2: Switch to Haiku 4.5 (270 videos)
**If quality acceptable:**
- Process remaining 270 videos with Haiku 4.5
- **Cost:** 270 × $0.033 = $8.91
- **Time:** ~3 hours

**Total Hybrid Cost: $10.44**
**Total Hybrid Time: ~3.5 hours**

### Quality Comparison Metrics
For the 30 test videos, evaluate:
1. **Completeness:** Are all categories captured?
2. **Accuracy:** Are insights relevant and accurate?
3. **Detail Level:** Sufficient depth vs generic?
4. **Actionability:** Can insights be used for decisions?

---

## 🚀 Implementation Steps

### Step 1: Resume Processing for 3 Incomplete Videos
```bash
# These have transcripts but no insights
python3 scripts/business_intelligence_extractor.py Wr6n_zNKvMk
python3 scripts/business_intelligence_extractor.py Avp3xh3Y1Ic
python3 scripts/business_intelligence_extractor.py k-3PoOT4vOM
```

### Step 2: Create Test Batch (30 videos)
```bash
# Extract 10 from each channel for quality test
jq -r '.videos[0:10] | .[].id' data/youtube_channels/alex_hormozi_latest_100.json > data/test_batch_tier1.txt
jq -r '.videos[0:10] | .[].id' data/youtube_channels/dan_martell_latest_100.json >> data/test_batch_tier1.txt
jq -r '.videos[0:10] | .[].id' data/youtube_channels/saastr_latest_100.json >> data/test_batch_tier1.txt

# Run test batch with Sonnet 4 (current default)
python3 scripts/batch_extract_videos_enhanced.py --file data/test_batch_tier1.txt --workers 10
```

### Step 3: Quality Review
```bash
# Check quality of first 10 insights
ls -lt data/business_insights/ | head -15
# Manually review 5 random insights
```

### Step 4: Modify Script for Haiku 4.5
**Edit:** `scripts/business_intelligence_extractor.py`
**Change line ~50:**
```python
# FROM:
model = "claude-sonnet-4-20250514"

# TO:
model = "claude-haiku-4-20250514"  # or "claude-3-5-haiku-20241022"
```

### Step 5: Process Remaining Videos
```bash
# Create remaining video list (exclude already processed)
jq -r '.videos[10:100] | .[].id' data/youtube_channels/alex_hormozi_latest_100.json > data/remaining_tier1.txt
jq -r '.videos[10:100] | .[].id' data/youtube_channels/dan_martell_latest_100.json >> data/remaining_tier1.txt
jq -r '.videos[10:100] | .[].id' data/youtube_channels/saastr_latest_100.json >> data/remaining_tier1.txt

# Run with Haiku 4.5
python3 scripts/batch_extract_videos_enhanced.py --file data/remaining_tier1.txt --workers 10
```

---

## 📋 Checkpoint & Recovery Features

The batch script (`batch_extract_videos_enhanced.py`) has built-in features:

1. **Checkpointing:** Saves progress every 10 videos
   - File: `data/batch_checkpoint.json`
   - Auto-resume on restart

2. **Failed Videos Tracking:**
   - File: `data/failed_videos.txt`
   - Retry separately after main batch

3. **Skip Existing:**
   - Automatically skips videos with existing insights
   - Safe to re-run without duplicate work

---

## 🎓 Expected Outcomes

### After Phase 1 (30 videos):
- ✅ Quality baseline established
- ✅ Decision on Haiku 4.5 vs Sonnet 4
- ✅ ~1-2 hours elapsed
- ✅ $1.53 spent

### After Phase 2 (300 videos total):
- ✅ All Tier 1 channels processed
- ✅ 300 transcripts with business insights
- ✅ ~4-5 hours total elapsed
- ✅ ~$10-15 total cost

### Data Available:
- Products & tools mentioned (with sentiment)
- Business problems & solutions
- Startup ideas & opportunities
- Growth tactics & frameworks
- AI workflows & automation
- Target markets & personas
- Emerging trends
- Key statistics & quotes

---

## 🔄 Next Steps After Tier 1-3

### Tier 4-6 Expansion (Optional)
Once Tier 1-3 complete, expand to:
- **Tier 2:** My First Million, Codie Sanchez (200 videos)
- **Tier 3:** Steven Bartlett, Gary Vee, etc. (400 videos)
- **Tier 4-6:** Additional 600 videos

**Total addressable:** 1,500+ videos from all tiers
**Estimated cost (all Haiku 4.5):** ~$50
**Estimated time:** ~20 hours

---

## 💡 Key Decisions Needed

1. **Model Choice:**
   - [ ] Start with 30-video test using Sonnet 4
   - [ ] If quality good, switch to Haiku 4.5 for remaining 270
   - [ ] If quality insufficient, continue with Sonnet 4

2. **Processing Priority:**
   - [ ] Process all 3 channels equally (recommended)
   - [ ] OR prioritize Alex Hormozi first (highest quality)

3. **Parallel Workers:**
   - [ ] 10 workers (recommended, ~5 hours total)
   - [ ] 5 workers (safer, ~8 hours total)
   - [ ] 15 workers (fastest, ~3 hours, but higher error risk)

---

## 📞 Quick Commands Reference

```bash
# Check status
ls data/transcripts/*.json | wc -l
ls data/business_insights/*.json | wc -l

# Resume from checkpoint
python3 scripts/batch_extract_videos_enhanced.py --file data/test_batch_tier1.txt --workers 10

# Process failed videos
python3 scripts/batch_extract_videos_enhanced.py --file data/failed_videos.txt --workers 5

# Check costs so far
jq '.results.transcripts.success' data/batch_extraction_results.json
# Multiply by $0.0242 for Browserbase cost

# Monitor progress
tail -f /tmp/batch_extraction.log  # If logging enabled
```

---

## ✅ Ready to Execute

**Immediate next action:**
1. Process 3 incomplete videos (have transcripts, need insights)
2. Start 30-video quality test with Sonnet 4
3. Evaluate and decide on Haiku 4.5 switch
4. Process remaining 270 videos

**Total estimated time to complete:** 4-5 hours
**Total estimated cost:** $10-15
**Expected completion:** Tonight (Oct 17) or tomorrow morning

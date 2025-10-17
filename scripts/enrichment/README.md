# Intelligence Enrichment System v1.0.0

A multi-resolution intelligence enrichment system for business insights extracted from YouTube videos.

## 📊 Architecture Overview

The system computes metrics at three resolution levels:

### Layer 1: Insight-Level Enrichment
- **Universal Metrics** (all video types):
  - `actionability_score` (0-100): How actionable the insight is
  - `specificity_score` (0-100): Level of detail and specificity
  - `evidence_strength` (0-100): Quality of supporting evidence
  - `recency_score` (0-100): How recent/timely the insight is

- **Type-Specific Metrics** (entrepreneurship videos):
  - `business_viability_score`: Market validation, business model strength
  - `market_validation_depth`: Evidence of market demand
  - `profitability_indicators`: Revenue/profit signals
  - `implementation_clarity`: Clarity of execution steps
  - `competitive_analysis_depth`: Competition analysis quality
  - `risk_assessment_score`: Risk factors identified

### Layer 2: Video-Level Summaries
- **Content Profile**: Video type, themes, experience level, industry focus
- **Key Takeaways**: Top 5 most valuable insights
- **Standout Insights**: High-scoring insights (>60)
- **Opportunity Map**: Startup ideas, market gaps, trend opportunities
- **Metrics Summary**: Aggregated statistics
- **Practical Next Steps**: Actionable recommendations
- **Related Keywords**: For discovering similar content

### Layer 3: Cross-Video Meta-Intelligence
- **Trend Analysis**: 36 unique trends across all videos with frequency and opportunities
- **Product Ecosystem**: 146 products with sentiment analysis and use cases
- **Strategy Playbooks**: 4 recurring patterns (Viral Growth, Audience First, SEO, Freemium)
- **Expert Consensus**: Agreement/disagreement on 5 key topics
- **Opportunity Matrix**: 183 total opportunities (64 startup ideas, 28 market gaps, 91 trends)

## 🚀 Quick Start

### 1. Run Enrichment on All Videos

```bash
cd /Users/yourox/AI-Workspace/scripts/enrichment
python3 enrichment_engine.py
```

### 2. Generate Video Summaries

```bash
python3 video_summarizer.py
```

### 3. Analyze Cross-Video Patterns

```bash
python3 meta_intelligence.py
```

## 📁 Output Structure

```
/Users/yourox/AI-Workspace/data/
├── enriched_insights/          # Layer 1: Insight-level metrics
│   ├── m9iaJNJE2-M_enriched.json
│   ├── ndqX4vbR7Rc_enriched.json
│   └── ... (51 files)
│
├── video_summaries/            # Layer 2: Video-level summaries
│   ├── m9iaJNJE2-M_summary.json
│   ├── ndqX4vbR7Rc_summary.json
│   └── ... (51 files)
│
└── meta_intelligence/          # Layer 3: Cross-video analysis
    └── meta_intelligence_report.json
```

## 🔍 MCP Tools Available

The enriched data is accessible through 8 new MCP tools:

### 1. `search_enriched_insights()`
Query videos by metric scores
```python
search_enriched_insights(
    video_type="entrepreneurship",
    min_actionability=70,
    min_specificity=50,
    limit=10
)
```

### 2. `get_high_value_insights()`
Get top insights by score
```python
get_high_value_insights(
    min_score=80,
    metric_type="actionability",  # or "specificity", "evidence", "all"
    limit=20
)
```

### 3. `search_video_summaries()`
Search video summaries
```python
search_video_summaries(
    query="microSaaS",
    video_type="entrepreneurship",
    experience_level="advanced"
)
```

### 4. `get_meta_trends()`
Get cross-video trends
```python
get_meta_trends(
    min_frequency=5,
    category="technology",
    stage="growing"
)
```

### 5. `get_product_ecosystem()`
Get product recommendations
```python
get_product_ecosystem(
    min_mentions=3,
    category="ai-tool",
    sentiment="highly_positive"
)
```

### 6. `get_strategy_playbooks()`
Get recurring strategies
```python
get_strategy_playbooks(limit=10)
```

### 7. `get_expert_consensus()`
Get topic consensus
```python
get_expert_consensus(topic="ai_tools")  # or "content_marketing", "saas_business", etc.
```

### 8. `get_opportunity_matrix()`
Get comprehensive opportunities
```python
get_opportunity_matrix(
    opportunity_type="startup_ideas",  # or "market_gaps", "trend_opportunities", "all"
    limit=20
)
```

## 📈 Key Statistics

**Enrichment Results:**
- ✅ 51 videos enriched
- 📊 1,109 total insights analyzed
- ⭐ 79 high-value insights (score > 80)
- 🎯 Video Types: 29 entrepreneurship, 22 market research

**Meta-Intelligence Discoveries:**
- 📈 36 unique trends (AI/AI Agents leading with 55 mentions)
- 🔧 146 unique products (IdeaBrowser.com most recommended)
- 📚 4 recurring strategy playbooks
- 🎯 183 total opportunities identified

## 🔧 Extensibility

### Adding New Metrics

1. Register metric in `metric_registry.py`:
```python
METRICS_REGISTRY['new_metric'] = {
    'name': 'new_metric',
    'display_name': 'New Metric Name',
    'description': 'What this metric measures',
    'type': 'score',
    'range': [0, 100],
    'applies_to': ['all']  # or specific video types
}
```

2. Add computation function:
```python
def compute_new_metric(self, insight: Dict[str, Any], category: str) -> int:
    # Your scoring logic
    return score
```

3. Re-run enrichment with `--force` flag to recompute

### Adding New Video Types

1. Add type definition in `video_classifier.py`
2. Add type-specific metrics in `metric_registry.py`
3. Re-run enrichment to apply new classification

## 📊 Performance

- Enrichment: 0.1s for 51 videos (idempotent, caches results)
- Summaries: ~1s for 51 videos
- Meta-intelligence: ~1s for cross-video analysis
- Total: <3s for complete enrichment pipeline

## 🎯 Use Cases

1. **High-Value Insight Discovery**: Find the most actionable insights across all videos
2. **Trend Analysis**: Identify emerging trends before they go mainstream
3. **Product Research**: See what tools experts recommend with sentiment analysis
4. **Strategy Learning**: Study proven playbooks used by successful businesses
5. **Opportunity Mining**: Discover validated startup ideas and market gaps
6. **Consensus Analysis**: Understand expert agreement on key topics

## 🔄 Version Tracking

All enriched data includes version metadata:
- `_version`: Enrichment system version
- `_computed_at`: Timestamp of computation
- `_engine_version`: Enrichment engine version
- `_metric_registry_version`: Metric registry version
- `_classifier_version`: Video classifier version

This enables backward compatibility and retroactive metric computation.

## 🚀 Next Steps

The enrichment system is production-ready and integrated with the MCP server. You can now:

1. Query enriched data through Claude Desktop using MCP tools
2. Build dashboards that visualize metric distributions
3. Create recommendation engines based on similarity scores
4. Export high-value insights for content creation
5. Track metric evolution over time as new videos are added

---

Built with ❤️ for multi-resolution business intelligence

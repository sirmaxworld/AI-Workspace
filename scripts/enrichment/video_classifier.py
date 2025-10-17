#!/usr/bin/env python3
"""
Video Type Classifier - Automatically detect video type from content
Supports manual override and confidence scoring
"""

from typing import Dict, Tuple, List


class VideoTypeClassifier:
    """Automatically classify video type based on content analysis"""

    VERSION = "1.0.0"

    # Video type definitions
    TYPES = {
        "entrepreneurship": {
            "keywords": ["business", "startup", "revenue", "profit", "market", "founder",
                        "monetization", "growth", "strategy", "saas", "customer", "idea"],
            "categories": ["startup_ideas", "business_strategies", "growth_tactics",
                          "market_intelligence", "mistakes_to_avoid"],
            "weight": 1.0
        },
        "tutorial": {
            "keywords": ["code", "tutorial", "how to", "step by step", "guide", "learn",
                        "build", "create", "implement", "programming", "development"],
            "categories": ["ai_workflows"],  # Technical workflows
            "indicators": ["code_examples", "prerequisites", "troubleshooting"],
            "weight": 1.0
        },
        "interview": {
            "keywords": ["interview", "conversation", "discussion", "podcast", "guest",
                        "talk", "chat", "dialogue", "q&a", "ask"],
            "categories": ["actionable_quotes"],  # High quote content
            "indicators": ["multiple_speakers", "dialogue_format"],
            "weight": 1.0
        },
        "case_study": {
            "keywords": ["case study", "post-mortem", "autopsy", "journey", "story",
                        "how we", "our experience", "failed", "succeeded", "lessons"],
            "categories": ["mistakes_to_avoid", "key_statistics"],
            "indicators": ["timeline", "metrics_disclosure"],
            "weight": 1.0
        },
        "market_research": {
            "keywords": ["research", "report", "analysis", "data", "study", "findings",
                        "survey", "statistics", "trend", "forecast", "prediction"],
            "categories": ["trends_signals", "key_statistics", "market_intelligence"],
            "indicators": ["data_heavy", "multiple_sources"],
            "weight": 1.0
        }
    }

    def __init__(self):
        self.last_classification = None
        self.last_confidence = 0.0
        self.last_scores = {}

    def classify_video(self, video_insights: Dict) -> str:
        """
        Classify video type based on content analysis

        Args:
            video_insights: Full insights data for a video

        Returns:
            Video type string (entrepreneurship, tutorial, interview, etc.)
        """
        scores = {}

        # Analyze title
        title = video_insights.get('meta', {}).get('title', '').lower()

        # Analyze content distribution
        content_counts = self._count_categories(video_insights)

        # Analyze text content
        all_text = self._extract_all_text(video_insights).lower()

        # Score each type
        for vtype, config in self.TYPES.items():
            score = 0

            # Title keyword matching (20 points max)
            title_matches = sum(1 for keyword in config['keywords'] if keyword in title)
            score += min(title_matches * 5, 20)

            # Content keyword matching (30 points max)
            text_matches = sum(1 for keyword in config['keywords'] if keyword in all_text)
            keyword_density = text_matches / max(len(config['keywords']), 1)
            score += min(keyword_density * 100, 30)

            # Category distribution (40 points max)
            if 'categories' in config:
                category_score = 0
                for category in config['categories']:
                    if category in content_counts and content_counts[category] > 0:
                        # More items = higher score
                        category_score += min(content_counts[category] * 5, 15)
                score += min(category_score, 40)

            # Special indicators (10 points max)
            if 'indicators' in config:
                indicator_score = self._check_indicators(vtype, video_insights, all_text)
                score += min(indicator_score, 10)

            scores[vtype] = score * config['weight']

        # Get top type
        if not scores:
            top_type = "general"
            confidence = 0.5
        else:
            top_type = max(scores, key=scores.get)
            top_score = scores[top_type]
            total_score = sum(scores.values())

            # Confidence is ratio of top score to total
            confidence = top_score / max(total_score, 1) if total_score > 0 else 0.5

            # If score is too low, default to entrepreneurship (current content type)
            if top_score < 20:
                top_type = "entrepreneurship"
                confidence = 0.6

        # Store for debugging
        self.last_classification = top_type
        self.last_confidence = confidence
        self.last_scores = scores

        return top_type

    def classify_with_confidence(self, video_insights: Dict) -> Tuple[str, float, Dict]:
        """
        Classify video and return confidence score

        Returns:
            Tuple of (type, confidence, scores_dict)
        """
        vtype = self.classify_video(video_insights)
        return vtype, self.last_confidence, self.last_scores

    def get_type_confidence(self) -> float:
        """Return confidence in last classification (0-1)"""
        return self.last_confidence

    def _count_categories(self, video_insights: Dict) -> Dict[str, int]:
        """Count items in each category"""
        counts = {}

        category_keys = [
            'products_tools', 'business_strategies', 'problems_solutions',
            'startup_ideas', 'mistakes_to_avoid', 'growth_tactics',
            'ai_workflows', 'metrics_kpis', 'trends_signals',
            'actionable_quotes', 'key_statistics'
        ]

        for key in category_keys:
            if key in video_insights:
                items = video_insights[key]
                if isinstance(items, list):
                    counts[key] = len(items)

        # Handle nested market_intelligence
        if 'market_intelligence' in video_insights:
            mi = video_insights['market_intelligence']
            if isinstance(mi, dict):
                counts['market_intelligence'] = sum(
                    len(v) for v in mi.values() if isinstance(v, list)
                )

        return counts

    def _extract_all_text(self, video_insights: Dict) -> str:
        """Extract all text content for keyword analysis"""
        import json
        # Convert entire insights to string for keyword matching
        # Exclude meta to avoid false positives from metadata
        data_copy = {k: v for k, v in video_insights.items() if k != 'meta'}
        return json.dumps(data_copy)

    def _check_indicators(self, vtype: str, insights: Dict, all_text: str) -> int:
        """Check for special indicators of video type"""
        score = 0

        if vtype == "tutorial":
            # Check for code examples
            if 'code' in all_text or 'function' in all_text or '()' in all_text:
                score += 5

            # Check for ai_workflows (often technical)
            if 'ai_workflows' in insights and len(insights.get('ai_workflows', [])) > 5:
                score += 5

        elif vtype == "interview":
            # Check for high quote density
            quotes = len(insights.get('actionable_quotes', []))
            total_insights = sum(
                len(v) for v in insights.values()
                if isinstance(v, list)
            )
            if total_insights > 0 and quotes / total_insights > 0.3:  # >30% quotes
                score += 5

        elif vtype == "case_study":
            # Check for timeline/journey keywords
            if any(word in all_text for word in ['timeline', 'journey', 'from', 'to', 'started']):
                score += 5

            # Check for high statistics density
            stats = len(insights.get('key_statistics', []))
            if stats > 10:
                score += 5

        elif vtype == "market_research":
            # Check for data-heavy content
            stats = len(insights.get('key_statistics', []))
            trends = len(insights.get('trends_signals', []))
            if stats + trends > 15:
                score += 5

            # Check for research keywords
            if any(word in all_text for word in ['research', 'study', 'report', 'data', 'analysis']):
                score += 5

        return score

    def override_type(self, manual_type: str) -> bool:
        """
        Manually override the detected type

        Args:
            manual_type: Type to set manually

        Returns:
            True if valid type, False otherwise
        """
        if manual_type in self.TYPES or manual_type == "general":
            self.last_classification = manual_type
            self.last_confidence = 1.0  # Manual override = 100% confidence
            return True
        return False

    def get_type_info(self, vtype: str) -> Dict:
        """Get information about a video type"""
        if vtype in self.TYPES:
            return self.TYPES[vtype]
        return {}

    def list_supported_types(self) -> List[str]:
        """List all supported video types"""
        return list(self.TYPES.keys()) + ["general"]

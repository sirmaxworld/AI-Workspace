#!/usr/bin/env python3
"""
Metric Registry - Central registry for all enrichment metrics
Supports universal and type-specific metrics with versioning
"""

import re
from typing import Dict, List, Any, Callable
from datetime import datetime


class MetricRegistry:
    """Central registry of all available enrichment metrics"""

    VERSION = "1.0.0"

    def __init__(self):
        self.universal_metrics = self._register_universal_metrics()
        self.type_specific_metrics = self._register_type_specific_metrics()

    def _register_universal_metrics(self) -> List[Dict[str, Any]]:
        """Register metrics that apply to all video types"""
        return [
            {
                "name": "actionability_score",
                "description": "How immediately actionable this insight is (0-100)",
                "applies_to": ["all"],
                "version": "1.0",
                "compute_function": self.compute_actionability
            },
            {
                "name": "specificity_score",
                "description": "How specific vs generic this insight is (0-100)",
                "applies_to": ["all"],
                "version": "1.0",
                "compute_function": self.compute_specificity
            },
            {
                "name": "evidence_strength",
                "description": "Quality of evidence, examples, and validation (0-100)",
                "applies_to": ["all"],
                "version": "1.0",
                "compute_function": self.compute_evidence_strength
            },
            {
                "name": "recency_score",
                "description": "How current and relevant this insight is (0-100)",
                "applies_to": ["all"],
                "version": "1.0",
                "compute_function": self.compute_recency
            }
        ]

    def _register_type_specific_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Register metrics specific to video types"""
        return {
            "entrepreneurship": [
                {
                    "name": "business_viability_score",
                    "description": "Likelihood of business success based on validation (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_business_viability
                },
                {
                    "name": "market_validation_depth",
                    "description": "How well validated the market opportunity is (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_market_validation
                },
                {
                    "name": "profitability_indicators",
                    "description": "Presence of revenue/profit data and business model clarity (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_profitability_indicators
                },
                {
                    "name": "implementation_clarity",
                    "description": "Clarity of execution steps and implementation details (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_implementation_clarity
                },
                {
                    "name": "competitive_analysis_depth",
                    "description": "Quality of competitive landscape analysis (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_competitive_analysis
                },
                {
                    "name": "risk_assessment_score",
                    "description": "How well risks and challenges are addressed (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_risk_assessment
                }
            ],
            "tutorial": [
                {
                    "name": "code_quality_indicators",
                    "description": "Presence of best practices and quality code (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_code_quality
                },
                {
                    "name": "prerequisite_clarity",
                    "description": "How well prerequisites are explained (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_prerequisite_clarity
                },
                {
                    "name": "troubleshooting_coverage",
                    "description": "Coverage of common issues and debugging (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_troubleshooting
                }
            ],
            "interview": [
                {
                    "name": "expert_credibility_score",
                    "description": "Credibility of expert/interviewee (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_expert_credibility
                },
                {
                    "name": "anecdote_richness",
                    "description": "Richness of personal stories and experiences (0-100)",
                    "version": "1.0",
                    "compute_function": self.compute_anecdote_richness
                }
            ]
        }

    def get_metrics_for_type(self, video_type: str) -> List[Dict[str, Any]]:
        """Get all applicable metrics for a video type"""
        metrics = self.universal_metrics.copy()
        type_metrics = self.type_specific_metrics.get(video_type, [])
        metrics.extend(type_metrics)
        return metrics

    def register_new_metric(self, metric_def: Dict[str, Any], video_types: List[str]):
        """Add new metric without breaking existing code"""
        if "all" in video_types:
            self.universal_metrics.append(metric_def)
        else:
            for vtype in video_types:
                if vtype not in self.type_specific_metrics:
                    self.type_specific_metrics[vtype] = []
                self.type_specific_metrics[vtype].append(metric_def)

    # ==================== UNIVERSAL METRIC COMPUTATIONS ====================

    def compute_actionability(self, insight: Dict[str, Any], category: str) -> int:
        """
        Compute actionability score (0-100) based on:
        - Presence of specific steps
        - Presence of tools/resources
        - Difficulty level
        - Cost estimates
        """
        score = 0
        text = str(insight).lower()

        # Has specific steps (+30)
        if 'steps' in insight and insight.get('steps'):
            steps = insight['steps']
            if isinstance(steps, list) and len(steps) > 0:
                score += 30
                # Bonus for detailed steps
                if len(steps) >= 3:
                    score += 10

        # Has tools/resources mentioned (+20)
        if any(key in insight for key in ['tools_needed', 'tools_used', 'pricing']):
            if insight.get('tools_needed') or insight.get('tools_used'):
                score += 20

        # Has cost estimate (+15)
        if any(key in insight for key in ['cost_estimate', 'pricing', 'investment_needed']):
            if insight.get('cost_estimate') or insight.get('pricing') or insight.get('investment_needed'):
                score += 15

        # Difficulty level (easier = more actionable) (+15)
        difficulty = insight.get('difficulty', '').lower()
        if difficulty == 'beginner':
            score += 15
        elif difficulty == 'intermediate':
            score += 10
        elif difficulty == 'advanced':
            score += 5

        # Has time estimate (+10)
        if 'time_estimate' in insight or 'timeframe' in text:
            score += 10

        # Bonus for tactical keywords
        tactical_keywords = ['step', 'how to', 'implement', 'build', 'create', 'launch', 'start']
        keyword_count = sum(1 for keyword in tactical_keywords if keyword in text)
        score += min(keyword_count * 2, 10)

        return min(score, 100)

    def compute_specificity(self, insight: Dict[str, Any], category: str) -> int:
        """
        Compute specificity score (0-100) based on:
        - Presence of specific numbers/metrics
        - Named entities (companies, products, people)
        - Concrete examples vs generic advice
        """
        score = 0
        text = str(insight).lower()

        # Has specific numbers/metrics (+25)
        number_patterns = [
            r'\$[\d,]+',  # Dollar amounts
            r'\d+%',  # Percentages
            r'\d+[kKmM]',  # 10k, 5M notation
            r'\d+\s*(users|customers|subscribers)',  # User counts
            r'\d+\s*(hours|days|weeks|months)',  # Time periods
        ]
        for pattern in number_patterns:
            if re.search(pattern, text):
                score += 5
        score = min(score, 25)

        # Has named products/tools (+20)
        if 'name' in insight and insight.get('name'):
            score += 20

        # Has case study or example (+20)
        if any(key in insight for key in ['case_study', 'example', 'real_examples']):
            if insight.get('case_study') or insight.get('example') or insight.get('real_examples'):
                score += 20

        # Has specific implementation details (+15)
        specific_fields = ['implementation', 'solution', 'steps', 'strategy']
        for field in specific_fields:
            if field in insight and insight.get(field):
                value = str(insight[field])
                if len(value) > 50:  # Detailed content
                    score += 5
        score = min(score, 15) + (score - 15 if score > 15 else 0)

        # Penalize generic words
        generic_words = ['general', 'usually', 'typically', 'sometimes', 'might', 'could']
        generic_count = sum(1 for word in generic_words if word in text)
        score -= generic_count * 3

        # Has category/classification (+10)
        if 'category' in insight and insight.get('category'):
            score += 10

        return max(0, min(score, 100))

    def compute_evidence_strength(self, insight: Dict[str, Any], category: str) -> int:
        """
        Compute evidence strength (0-100) based on:
        - Metrics and data provided
        - Case studies and examples
        - Source reliability
        - Validation signals
        """
        score = 0
        text = str(insight).lower()

        # Has metrics/data (+30)
        if 'metrics' in insight and insight.get('metrics'):
            score += 30
        elif any(key in insight for key in ['benchmark', 'statistic', 'results_expected']):
            score += 20

        # Has case study (+25)
        if 'case_study' in insight and insight.get('case_study'):
            case_study = str(insight['case_study'])
            if len(case_study) > 20:  # Substantive case study
                score += 25

        # Source reliability (+20)
        if 'source_reliability' in insight:
            reliability = insight['source_reliability'].lower()
            if reliability == 'verified':
                score += 20
            elif reliability == 'claimed':
                score += 10
            elif reliability == 'estimated':
                score += 5

        # Validation mentions (+15)
        validation_keywords = ['proven', 'validated', 'tested', 'verified', 'research', 'study']
        validation_count = sum(1 for keyword in validation_keywords if keyword in text)
        score += min(validation_count * 5, 15)

        # Has real example (+10)
        if 'example' in insight or 'real example' in text or 'for example' in text:
            score += 10

        return min(score, 100)

    def compute_recency(self, insight: Dict[str, Any], category: str) -> int:
        """
        Compute recency score (0-100) based on:
        - Technology/tool currency
        - Time-sensitive language
        - Explicit dates mentioned
        - Trend stage
        """
        score = 70  # Base score (neutral)
        text = str(insight).lower()

        # Check for current year (2025) or recent years (+15)
        if '2025' in text or '2024' in text:
            score += 15
        elif '2023' in text:
            score += 10
        elif any(year in text for year in ['2021', '2022']):
            score += 5
        elif any(year in text for year in ['2019', '2020']):
            score -= 10
        elif any(year in text for year in ['2017', '2018']):
            score -= 20

        # Time-sensitive language
        current_keywords = ['now', 'currently', 'today', 'this year', 'recent', 'latest', 'new']
        current_count = sum(1 for keyword in current_keywords if keyword in text)
        score += min(current_count * 3, 15)

        # Dated language
        dated_keywords = ['used to', 'back then', 'in the past', 'legacy', 'outdated', 'old']
        dated_count = sum(1 for keyword in dated_keywords if keyword in text)
        score -= dated_count * 5

        # Trend stage (if applicable)
        if 'stage' in insight:
            stage = insight['stage'].lower()
            if stage in ['early', 'emerging', 'growing']:
                score += 10
            elif stage == 'mainstream':
                score += 5
            elif stage == 'declining':
                score -= 20

        # Modern tech/tools mentioned
        modern_tech = ['ai', 'gpt', 'claude', 'chatgpt', 'llm', 'automation', 'saas', 'api']
        modern_count = sum(1 for tech in modern_tech if tech in text)
        score += min(modern_count * 2, 10)

        return max(0, min(score, 100))

    # ==================== ENTREPRENEURSHIP-SPECIFIC METRICS ====================

    def compute_business_viability(self, insight: Dict[str, Any], category: str) -> int:
        """Compute business viability score for entrepreneurship insights"""
        score = 0
        text = str(insight).lower()

        # Has validation (+25)
        if 'validation' in insight and insight.get('validation'):
            score += 25
        elif any(word in text for word in ['validated', 'proven', 'tested']):
            score += 15

        # Has business model (+20)
        if 'business_model' in insight and insight.get('business_model'):
            score += 20

        # Has target market defined (+20)
        if 'target_market' in insight and insight.get('target_market'):
            score += 20

        # Has revenue/profit indicators (+20)
        if any(char in text for char in ['$', '€', '£']) or 'revenue' in text or 'profit' in text:
            score += 20

        # Has clear problem-solution fit (+15)
        if 'problem_solved' in insight or 'pain_point' in text:
            score += 15

        return min(score, 100)

    def compute_market_validation(self, insight: Dict[str, Any], category: str) -> int:
        """Compute market validation depth"""
        score = 0
        text = str(insight).lower()

        # Market size indicators (+30)
        if 'market_size' in text or 'tam' in text or any(re.search(r'\d+[kKmMbB].*market', text) for _ in [1]):
            score += 30

        # Existing solutions mentioned (+20)
        if 'current_solutions' in insight or 'competitors' in text or 'alternatives' in text:
            score += 20

        # Severity/frequency data (+20)
        if 'severity' in insight or 'frequency' in insight:
            score += 20

        # Customer interviews/feedback (+15)
        if any(word in text for word in ['interview', 'survey', 'feedback', 'customer', 'user']):
            score += 15

        # Market gap identified (+15)
        if 'market_gap' in insight or 'gap' in text or 'opportunity' in text:
            score += 15

        return min(score, 100)

    def compute_profitability_indicators(self, insight: Dict[str, Any], category: str) -> int:
        """Compute profitability indicators score"""
        score = 0
        text = str(insight).lower()

        # Revenue numbers mentioned (+35)
        if 'revenue' in text or 'mrr' in text or 'arr' in text:
            score += 35
            # Bonus for specific numbers
            if re.search(r'\$[\d,]+', text):
                score += 10

        # Profit margins mentioned (+25)
        if 'margin' in text or 'profit' in text:
            score += 25

        # Pricing model clear (+20)
        if 'pricing' in insight and insight.get('pricing'):
            score += 20

        # Business model defined (+20)
        if 'business_model' in insight or 'monetization' in text:
            score += 20

        return min(score, 100)

    def compute_implementation_clarity(self, insight: Dict[str, Any], category: str) -> int:
        """Compute implementation clarity score"""
        score = 0

        # Has detailed steps (+40)
        if 'steps' in insight and insight.get('steps'):
            steps = insight['steps']
            if isinstance(steps, list):
                score += 20
                score += min(len(steps) * 5, 20)  # Bonus for more steps

        # Has implementation field (+25)
        if 'implementation' in insight and insight.get('implementation'):
            impl = str(insight['implementation'])
            if len(impl) > 50:
                score += 25

        # Has tools specified (+20)
        if 'tools_needed' in insight or 'tools_used' in insight:
            score += 20

        # Has time estimate (+15)
        if 'time_estimate' in insight or 'timeframe' in str(insight).lower():
            score += 15

        return min(score, 100)

    def compute_competitive_analysis(self, insight: Dict[str, Any], category: str) -> int:
        """Compute competitive analysis depth"""
        score = 0
        text = str(insight).lower()

        # Competitors mentioned (+30)
        if 'competitors' in text or 'competition' in text:
            score += 30

        # Alternative solutions (+25)
        if 'alternatives' in text or 'current_solutions' in insight:
            score += 25

        # Competitive advantages (+25)
        if 'advantage' in text or 'differentiation' in text or 'unique' in text:
            score += 25

        # Market positioning (+20)
        if 'positioning' in text or 'market_gap' in insight or 'opportunity' in text:
            score += 20

        return min(score, 100)

    def compute_risk_assessment(self, insight: Dict[str, Any], category: str) -> int:
        """Compute risk assessment quality"""
        score = 0
        text = str(insight).lower()

        # Risks/challenges mentioned (+35)
        if 'risk' in text or 'challenge' in text or 'problem' in text:
            score += 35

        # Mistakes to avoid (+30)
        if 'mistake' in insight or 'avoid' in text or 'warning' in text:
            score += 30

        # Consequences discussed (+20)
        if 'consequences' in insight or 'impact' in text or 'result' in text:
            score += 20

        # Prevention strategies (+15)
        if 'prevention' in insight or 'mitigate' in text or 'solution' in text:
            score += 15

        return min(score, 100)

    # ==================== TUTORIAL-SPECIFIC METRICS ====================

    def compute_code_quality(self, insight: Dict[str, Any], category: str) -> int:
        """Compute code quality indicators (placeholder for tutorial videos)"""
        score = 50  # Neutral for non-tutorial content
        text = str(insight).lower()

        # Best practices mentioned
        if 'best practice' in text or 'pattern' in text:
            score += 25

        # Testing mentioned
        if 'test' in text or 'testing' in text:
            score += 25

        return min(score, 100)

    def compute_prerequisite_clarity(self, insight: Dict[str, Any], category: str) -> int:
        """Compute prerequisite clarity (placeholder)"""
        score = 50
        text = str(insight).lower()

        if 'prerequisite' in text or 'requirement' in text or 'need to know' in text:
            score += 30

        if 'beginner' in text or 'basic' in text:
            score += 20

        return min(score, 100)

    def compute_troubleshooting(self, insight: Dict[str, Any], category: str) -> int:
        """Compute troubleshooting coverage (placeholder)"""
        score = 50
        text = str(insight).lower()

        if 'error' in text or 'troubleshoot' in text or 'debug' in text:
            score += 30

        if 'common issue' in text or 'problem' in text:
            score += 20

        return min(score, 100)

    # ==================== INTERVIEW-SPECIFIC METRICS ====================

    def compute_expert_credibility(self, insight: Dict[str, Any], category: str) -> int:
        """Compute expert credibility (placeholder)"""
        score = 70  # Default good credibility for Greg Isenberg content
        text = str(insight).lower()

        if 'founder' in text or 'ceo' in text or 'expert' in text:
            score += 15

        if any(word in text for word in ['exit', 'acquired', 'raised', 'vc']):
            score += 15

        return min(score, 100)

    def compute_anecdote_richness(self, insight: Dict[str, Any], category: str) -> int:
        """Compute anecdote richness (placeholder)"""
        score = 60
        text = str(insight).lower()

        if 'story' in text or 'example' in text or 'experience' in text:
            score += 20

        if 'case_study' in insight:
            score += 20

        return min(score, 100)

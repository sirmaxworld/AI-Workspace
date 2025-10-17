#!/usr/bin/env python3
"""
Multi-Layer Quality Control System
Professional QC with automated checks, AI validation, and confidence scoring
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import re

from crewai import Agent, Task, Crew, Process


@dataclass
class QCResult:
    """Quality control result"""
    passed: bool
    confidence: float  # 0.0-1.0
    layer: str
    scores: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'passed': self.passed,
            'confidence': self.confidence,
            'layer': self.layer,
            'scores': self.scores,
            'issues': self.issues,
            'strengths': self.strengths,
            'recommendations': self.recommendations,
            'metadata': self.metadata
        }


class QCLayer(ABC):
    """Base class for QC layers"""

    def __init__(self, name: str, thresholds: Dict[str, float] = None):
        self.name = name
        self.thresholds = thresholds or {}

    @abstractmethod
    def check(self, item: Dict) -> QCResult:
        """Run quality check on item"""
        pass


class AutomatedQC(QCLayer):
    """
    Layer 1: Fast automated checks
    - Completeness validation
    - Format verification
    - Error detection
    - Metadata validation
    """

    def __init__(self, thresholds: Dict[str, float] = None):
        super().__init__("automated", thresholds)
        self.default_thresholds = {
            'min_completeness': 0.7,
            'min_content_length': 100,
            'max_error_rate': 0.1
        }
        self.thresholds = {**self.default_thresholds, **(thresholds or {})}

    def check(self, item: Dict) -> QCResult:
        """Run automated checks"""

        issues = []
        strengths = []
        scores = {}

        # Check 1: Completeness (duration vs content length)
        completeness = self._check_completeness(item)
        scores['completeness'] = completeness

        if completeness < self.thresholds['min_completeness']:
            issues.append(f"Low completeness: {completeness:.2f} (expected >{self.thresholds['min_completeness']})")
        else:
            strengths.append(f"Good completeness: {completeness:.2f}")

        # Check 2: Format validation
        format_valid = self._check_format(item)
        scores['format'] = 1.0 if format_valid else 0.0

        if not format_valid:
            issues.append("Invalid format or missing required fields")
        else:
            strengths.append("Valid format and structure")

        # Check 3: Content quality
        content_score = self._check_content_quality(item)
        scores['content_quality'] = content_score

        if content_score < 0.5:
            issues.append(f"Low content quality: {content_score:.2f}")
        else:
            strengths.append(f"Acceptable content quality: {content_score:.2f}")

        # Check 4: Error detection
        error_rate = self._detect_errors(item)
        scores['error_rate'] = 1.0 - error_rate

        if error_rate > self.thresholds['max_error_rate']:
            issues.append(f"High error rate: {error_rate:.2f}")
        else:
            strengths.append("Low error rate")

        # Calculate overall confidence
        confidence = sum(scores.values()) / len(scores)

        # Pass if no critical issues
        passed = len(issues) == 0 or confidence > 0.7

        return QCResult(
            passed=passed,
            confidence=confidence,
            layer=self.name,
            scores=scores,
            issues=issues,
            strengths=strengths,
            metadata={'thresholds': self.thresholds}
        )

    def _check_completeness(self, item: Dict) -> float:
        """Check if content is complete relative to expected length"""

        # For YouTube: check transcript length vs video duration
        if item.get('source_type') == 'youtube':
            duration = item.get('metadata', {}).get('duration', 0)
            content = item.get('content', '')
            transcript_length = len(content)

            if duration == 0:
                return 0.0

            # Rough estimate: ~150 words/minute, ~5 chars/word
            expected_length = duration / 60 * 150 * 5
            completeness = min(transcript_length / expected_length, 1.0)

            return completeness

        # Generic: check if content exists and has minimum length
        content = item.get('content', '')
        if len(content) < self.thresholds['min_content_length']:
            return 0.0

        return 1.0

    def _check_format(self, item: Dict) -> bool:
        """Validate format and required fields"""

        required_fields = ['id', 'title', 'source_type', 'source_url']

        for field in required_fields:
            if field not in item or not item[field]:
                return False

        return True

    def _check_content_quality(self, item: Dict) -> float:
        """Basic content quality checks"""

        content = item.get('content', '')

        if not content:
            return 0.0

        score = 1.0

        # Check for repeated patterns (indicates poor quality)
        if len(set(content.split())) < len(content.split()) * 0.3:
            score -= 0.3  # High repetition

        # Check for proper sentence structure
        sentences = content.split('.')
        if len(sentences) < 5:
            score -= 0.2  # Too few sentences

        # Check for reasonable word length
        words = content.split()
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        if avg_word_length < 3 or avg_word_length > 15:
            score -= 0.2  # Unusual word length

        return max(score, 0.0)

    def _detect_errors(self, item: Dict) -> float:
        """Detect transcription errors and gibberish"""

        content = item.get('content', '')

        if not content:
            return 1.0  # No content = 100% error rate

        errors = 0
        total_checks = 0

        # Check for common transcription artifacts
        artifacts = ['[Music]', '[Applause]', '[inaudible]', '[??]', '...']
        for artifact in artifacts:
            if artifact.lower() in content.lower():
                errors += content.lower().count(artifact.lower())
        total_checks += len(content.split())

        # Check for excessive punctuation
        punct_ratio = sum(1 for c in content if not c.isalnum() and not c.isspace()) / max(len(content), 1)
        if punct_ratio > 0.15:
            errors += 10
        total_checks += 10

        error_rate = errors / max(total_checks, 1)
        return min(error_rate, 1.0)


class AIAgentQC(QCLayer):
    """
    Layer 2: AI agent quality validation
    - Content coherence
    - Information value
    - Technical accuracy
    - Actionability
    """

    def __init__(self, thresholds: Dict[str, float] = None):
        super().__init__("ai_agent", thresholds)
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create QC agent"""
        return Agent(
            role='Quality Control Specialist',
            goal='Validate content quality, coherence, and information value',
            backstory="""You are an expert quality assurance specialist. You evaluate
            content for completeness, coherence, accuracy, and practical value. You
            provide detailed, actionable feedback.""",
            verbose=False,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'  # Using highest model
        )

    def check(self, item: Dict) -> QCResult:
        """Run AI agent validation"""

        # Prepare validation input
        content_sample = item.get('content', '')[:1000]  # First 1000 chars

        task = Task(
            description=f"""
            Evaluate this content for quality:

            Title: {item.get('title', 'Unknown')}
            Source: {item.get('source_type', 'Unknown')} - {item.get('source_name', 'Unknown')}
            Content Sample (first 1000 chars):
            {content_sample}

            Evaluate:
            1. Coherence: Is the content well-structured and logical?
            2. Information Value: Does it contain useful, actionable information?
            3. Accuracy: Are there obvious factual errors or inconsistencies?
            4. Completeness: Does it seem complete or truncated?

            Respond with **valid JSON only**:
            {{
              "coherence_score": 0.0-1.0,
              "value_score": 0.0-1.0,
              "accuracy_score": 0.0-1.0,
              "completeness_score": 0.0-1.0,
              "overall_quality": "excellent"|"good"|"fair"|"poor",
              "issues": [str],
              "strengths": [str],
              "recommendations": [str],
              "passed": true|false
            }}
            """,
            expected_output="JSON quality assessment with scores and feedback",
            agent=self.agent
        )

        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )

        try:
            result = crew.kickoff()
            parsed = self._parse_agent_output(result)

            # Calculate confidence from scores
            scores = {
                'coherence': parsed.get('coherence_score', 0),
                'value': parsed.get('value_score', 0),
                'accuracy': parsed.get('accuracy_score', 0),
                'completeness': parsed.get('completeness_score', 0)
            }
            confidence = sum(scores.values()) / len(scores)

            return QCResult(
                passed=parsed.get('passed', confidence > 0.7),
                confidence=confidence,
                layer=self.name,
                scores=scores,
                issues=parsed.get('issues', []),
                strengths=parsed.get('strengths', []),
                recommendations=parsed.get('recommendations', []),
                metadata={'overall_quality': parsed.get('overall_quality', 'unknown')}
            )

        except Exception as e:
            # If AI QC fails, return neutral result
            return QCResult(
                passed=True,
                confidence=0.5,
                layer=self.name,
                issues=[f"AI QC failed: {str(e)}"],
                metadata={'error': str(e)}
            )

    def _parse_agent_output(self, raw_output) -> Dict:
        """Parse agent output to dict"""

        output_text = str(raw_output)
        if hasattr(raw_output, 'raw_output'):
            output_text = str(raw_output.raw_output)
        elif hasattr(raw_output, 'output'):
            output_obj = raw_output.output
            for attr in ('raw_output', 'final_result', 'value', 'content'):
                if hasattr(output_obj, attr):
                    data = getattr(output_obj, attr)
                    if data:
                        output_text = str(data)
                        break

        # Clean markdown
        cleaned = output_text.strip()
        if '```' in cleaned:
            cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = cleaned.rsplit('```', 1)[0]

        return json.loads(cleaned)


class ConfidenceScoring(QCLayer):
    """
    Layer 3: Overall confidence calculation
    - Aggregates all layer scores
    - Weights by importance
    - Considers source authority
    """

    def __init__(self, thresholds: Dict[str, float] = None):
        super().__init__("confidence", thresholds)
        self.weights = {
            'automated': 0.3,
            'ai_agent': 0.5,
            'source_authority': 0.2
        }

    def check(self, item: Dict, layer_results: List[QCResult]) -> QCResult:
        """Calculate overall confidence score"""

        scores = {}
        all_issues = []
        all_strengths = []
        all_recommendations = []

        # Aggregate layer results
        for result in layer_results:
            weight = self.weights.get(result.layer, 0.1)
            scores[result.layer] = result.confidence * weight
            all_issues.extend(result.issues)
            all_strengths.extend(result.strengths)
            all_recommendations.extend(result.recommendations)

        # Source authority bonus
        source_authority = self._calculate_source_authority(item)
        scores['source_authority'] = source_authority * self.weights['source_authority']

        # Final confidence
        confidence = sum(scores.values())

        # Pass threshold
        min_confidence = self.thresholds.get('min_confidence', 0.75)
        passed = confidence >= min_confidence

        if not passed:
            all_recommendations.append(f"Confidence {confidence:.2f} below threshold {min_confidence}")

        return QCResult(
            passed=passed,
            confidence=confidence,
            layer=self.name,
            scores=scores,
            issues=all_issues,
            strengths=all_strengths,
            recommendations=all_recommendations,
            metadata={
                'min_confidence': min_confidence,
                'weights': self.weights
            }
        )

    def _calculate_source_authority(self, item: Dict) -> float:
        """Calculate source authority score"""

        # For YouTube: consider view count, subscriber count (if available)
        if item.get('source_type') == 'youtube':
            view_count = item.get('metadata', {}).get('view_count', 0)

            # Rough authority scoring based on views
            if view_count > 1_000_000:
                return 1.0
            elif view_count > 100_000:
                return 0.9
            elif view_count > 10_000:
                return 0.8
            elif view_count > 1_000:
                return 0.7
            else:
                return 0.6

        # Default moderate authority
        return 0.7


class QualityControlSystem:
    """
    Multi-layer quality control system

    Orchestrates all QC layers in sequence
    """

    def __init__(self, config: Dict[str, Any] = None):
        config = config or {}

        thresholds = config.get('thresholds', {})

        self.layers = [
            AutomatedQC(thresholds),
            AIAgentQC(thresholds),
        ]

        self.confidence_layer = ConfidenceScoring(thresholds)

        self.stats = {
            'total_checked': 0,
            'passed': 0,
            'failed': 0,
            'avg_confidence': 0.0
        }

    def validate(self, item: Dict, enable_ai_qc: bool = True) -> QCResult:
        """
        Run full QC validation

        Args:
            item: Item to validate
            enable_ai_qc: Enable AI agent QC (slower but more thorough)

        Returns:
            Final QC result with confidence score
        """

        layer_results = []

        # Run automated QC first (fast)
        automated_result = self.layers[0].check(item)
        layer_results.append(automated_result)

        # If automated QC fails badly, skip AI QC
        if automated_result.confidence < 0.3:
            print(f"   ⚠️  Skipping AI QC (automated confidence too low: {automated_result.confidence:.2f})")
            enable_ai_qc = False

        # Run AI QC if enabled
        if enable_ai_qc:
            ai_result = self.layers[1].check(item)
            layer_results.append(ai_result)

        # Calculate final confidence
        final_result = self.confidence_layer.check(item, layer_results)

        # Update stats
        self.stats['total_checked'] += 1
        if final_result.passed:
            self.stats['passed'] += 1
        else:
            self.stats['failed'] += 1

        # Running average confidence
        n = self.stats['total_checked']
        self.stats['avg_confidence'] = (self.stats['avg_confidence'] * (n-1) + final_result.confidence) / n

        return final_result

    def print_stats(self):
        """Print QC statistics"""
        print(f"\n{'='*70}")
        print(f"QC STATISTICS")
        print(f"{'='*70}")
        print(f"Total Checked: {self.stats['total_checked']}")
        print(f"Passed: {self.stats['passed']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Pass Rate: {self.stats['passed'] / max(self.stats['total_checked'], 1) * 100:.1f}%")
        print(f"Avg Confidence: {self.stats['avg_confidence']:.2f}")
        print(f"{'='*70}\n")


def main():
    """Test QC system"""

    # Sample item
    test_item = {
        'id': 'test123',
        'title': 'How to Build AI Agents',
        'source_type': 'youtube',
        'source_name': 'AI Channel',
        'source_url': 'https://youtube.com/watch?v=test123',
        'content': 'This is a test transcript about building AI agents. ' * 50,
        'metadata': {
            'duration': 600,
            'view_count': 50000
        }
    }

    # Create QC system
    qc = QualityControlSystem()

    # Validate
    print("Running QC validation...")
    result = qc.validate(test_item, enable_ai_qc=True)

    # Print results
    print(f"\n{'='*70}")
    print(f"QC RESULT")
    print(f"{'='*70}")
    print(f"Passed: {result.passed}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"\nScores:")
    for name, score in result.scores.items():
        print(f"  {name}: {score:.2f}")

    if result.issues:
        print(f"\nIssues:")
        for issue in result.issues:
            print(f"  - {issue}")

    if result.strengths:
        print(f"\nStrengths:")
        for strength in result.strengths:
            print(f"  - {strength}")


if __name__ == '__main__':
    main()

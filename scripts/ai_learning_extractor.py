#!/usr/bin/env python3
"""
AI Learning Extractor
Intelligently extracts learnings, patterns, and insights from coding sessions
Builds a personalized knowledge base of YOUR coding style and decisions
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import Counter, defaultdict

from ai_session_logger_core import (
    AISessionDB, Learning, CodingPattern, generate_id
)


class LearningExtractor:
    """
    Extracts meaningful learnings from coding activity
    Learns YOUR patterns, mistakes, and solutions
    """

    def __init__(self):
        self.db = AISessionDB()

    def extract_error_solution(self,
                               error_text: str,
                               solution_text: str,
                               session_id: str) -> Optional[Learning]:
        """Extract learning from error + solution pair"""

        # Common error patterns
        error_patterns = {
            r"ModuleNotFoundError: No module named '(\w+)'": "missing-dependency",
            r"ImportError": "import-error",
            r"SyntaxError": "syntax-error",
            r"TypeError": "type-error",
            r"AttributeError": "attribute-error",
            r"KeyError": "key-error",
            r"IndexError": "index-error",
            r"ValueError": "value-error",
            r"NameError": "undefined-variable",
            r"IndentationError": "indentation",
            r"RuntimeError": "runtime-error",
            r"ConnectionError": "connection-issue",
            r"TimeoutError": "timeout",
            r"PermissionError": "permissions",
        }

        # Detect error type
        error_category = "general-error"
        for pattern, category in error_patterns.items():
            if re.search(pattern, error_text):
                error_category = category
                break

        # Extract error title
        error_lines = error_text.strip().split('\n')
        title = error_lines[-1] if error_lines else "Unknown error"
        title = title[:100]  # Truncate

        # Create learning
        learning = Learning(
            learning_id=generate_id("learn", session_id, title),
            session_id=session_id,
            timestamp=datetime.now(),
            category="error-solution",
            title=f"Fixed: {title}",
            description=f"Error: {error_text[:200]}\n\nSolution: {solution_text[:300]}",
            code_snippet=solution_text[:500] if solution_text else None,
            tags=[error_category, "fix", "troubleshooting"],
            context={"error_type": error_category},
            confidence=0.9
        )

        return learning

    def detect_decision_pattern(self,
                                decision_description: str,
                                rationale: str,
                                session_id: str) -> Learning:
        """Record an architectural or technical decision"""

        # Detect decision types
        decision_types = {
            "database": ["database", "db", "postgres", "mysql", "sqlite", "mongodb"],
            "architecture": ["architecture", "pattern", "design", "structure"],
            "library": ["library", "package", "npm", "pip", "dependency"],
            "api": ["api", "endpoint", "route", "rest", "graphql"],
            "frontend": ["ui", "frontend", "react", "vue", "component"],
            "backend": ["backend", "server", "service", "microservice"],
            "testing": ["test", "testing", "unit", "integration", "e2e"],
            "security": ["security", "auth", "authentication", "authorization"],
            "performance": ["performance", "optimization", "speed", "caching"],
        }

        tags = ["decision"]
        for category, keywords in decision_types.items():
            if any(kw in decision_description.lower() for kw in keywords):
                tags.append(category)

        return Learning(
            learning_id=generate_id("decision", session_id, decision_description[:30]),
            session_id=session_id,
            timestamp=datetime.now(),
            category="decision",
            title=decision_description[:100],
            description=rationale,
            code_snippet=None,
            tags=tags,
            context={"decision_type": tags[1] if len(tags) > 1 else "general"},
            confidence=0.8
        )

    def extract_coding_pattern(self,
                               git_commits: List[Dict],
                               files_modified: List[str]) -> List[CodingPattern]:
        """
        Detect patterns in YOUR coding behavior
        Examples:
        - Always creating tests before implementation
        - Preference for certain libraries
        - File naming conventions
        - Commit message patterns
        """
        patterns = []

        # Pattern 1: Test-driven development
        test_files = [f for f in files_modified if 'test' in f.lower()]
        if test_files:
            patterns.append(CodingPattern(
                pattern_id="tdd_approach",
                pattern_type="problem-solving-approach",
                description="Creates tests alongside implementation",
                frequency=1,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                examples=[],
                is_beneficial=True,
                suggestions=["Keep maintaining test coverage"]
            ))

        # Pattern 2: Commit message style
        if git_commits:
            commit_styles = defaultdict(int)
            for commit in git_commits:
                msg = commit.get("message", "")
                if msg.startswith(("feat:", "fix:", "docs:", "refactor:")):
                    commit_styles["conventional-commits"] += 1
                elif msg[0].isupper():
                    commit_styles["capitalized"] += 1
                else:
                    commit_styles["casual"] += 1

            if commit_styles:
                most_common = max(commit_styles, key=commit_styles.get)
                patterns.append(CodingPattern(
                    pattern_id=f"commit_style_{most_common}",
                    pattern_type="code-style",
                    description=f"Uses {most_common} commit message style",
                    frequency=commit_styles[most_common],
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    examples=[],
                    is_beneficial=most_common == "conventional-commits",
                    suggestions=[] if most_common == "conventional-commits"
                               else ["Consider using conventional commits for better git history"]
                ))

        # Pattern 3: File organization preferences
        file_extensions = Counter()
        for f in files_modified:
            if '.' in f:
                ext = f.split('.')[-1]
                file_extensions[ext] += 1

        if file_extensions:
            top_ext = file_extensions.most_common(1)[0][0]
            patterns.append(CodingPattern(
                pattern_id=f"prefers_{top_ext}",
                pattern_type="code-style",
                description=f"Primarily works with .{top_ext} files",
                frequency=file_extensions[top_ext],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                examples=[],
                is_beneficial=None,  # Neutral
                suggestions=[]
            ))

        return patterns

    def extract_insight(self,
                       text: str,
                       session_id: str,
                       confidence: float = 0.7) -> Optional[Learning]:
        """Extract general insights from text"""

        # Look for insight markers
        insight_markers = [
            "learned that",
            "discovered",
            "realized",
            "found out",
            "figured out",
            "important to",
            "key is to",
            "should always",
            "should never",
            "best practice",
            "gotcha",
            "tip:",
            "note:",
            "remember",
        ]

        text_lower = text.lower()
        contains_insight = any(marker in text_lower for marker in insight_markers)

        if not contains_insight:
            return None

        # Extract sentences containing insights
        sentences = re.split(r'[.!?]\s+', text)
        insight_sentences = []

        for sentence in sentences:
            if any(marker in sentence.lower() for marker in insight_markers):
                insight_sentences.append(sentence.strip())

        if not insight_sentences:
            return None

        description = ". ".join(insight_sentences[:3])

        return Learning(
            learning_id=generate_id("insight", session_id, description[:30]),
            session_id=session_id,
            timestamp=datetime.now(),
            category="insight",
            title=insight_sentences[0][:100],
            description=description,
            code_snippet=None,
            tags=["insight", "learning"],
            context={},
            confidence=confidence
        )

    def analyze_session(self, session_snapshot: Dict, session_id: str):
        """
        Analyze a complete session and extract all learnings
        This is the main entry point for learning extraction
        """
        learnings = []
        patterns = []

        # Extract patterns from git commits and file changes
        if session_snapshot.get("git_commits") or session_snapshot.get("modified_files"):
            coding_patterns = self.extract_coding_pattern(
                session_snapshot.get("git_commits", []),
                session_snapshot.get("modified_files", [])
            )
            patterns.extend(coding_patterns)

        # Analyze coding activity from history
        for activity in session_snapshot.get("coding_activity", []):
            # Check for error patterns
            outcome = activity.get("outcome", "")
            if "error" in outcome.lower():
                # This was an error that was fixed
                learning = self.extract_error_solution(
                    error_text=outcome,
                    solution_text=activity.get("actions", ""),
                    session_id=session_id
                )
                if learning:
                    learnings.append(learning)

            # Extract insights from prompts and outcomes
            prompt = activity.get("prompt", "")
            if prompt:
                insight = self.extract_insight(prompt, session_id)
                if insight:
                    learnings.append(insight)

        # Save to database
        for learning in learnings:
            self.db.add_learning(learning)

        for pattern in patterns:
            self.db.record_pattern(pattern)

        return {
            "learnings_extracted": len(learnings),
            "patterns_detected": len(patterns),
            "learnings": [l.title for l in learnings],
            "patterns": [p.description for p in patterns]
        }

    def get_personalized_suggestions(self) -> List[str]:
        """
        Generate personalized coding suggestions based on YOUR patterns
        This builds the "coding bot that knows you better than you do"
        """
        suggestions = []

        # Get all patterns
        patterns = self.db.get_patterns()

        # Analyze beneficial vs problematic patterns
        good_patterns = [p for p in patterns if p.get("is_beneficial") == 1]
        bad_patterns = [p for p in patterns if p.get("is_beneficial") == 0]

        if good_patterns:
            suggestions.append(
                f"✅ You're doing well: {good_patterns[0]['description']}"
            )

        if bad_patterns:
            suggestions.append(
                f"⚠️ Consider improving: {bad_patterns[0]['description']}"
            )

        # Get common errors
        learnings = self.db.get_learnings(category="error-solution", limit=10)
        if learnings:
            error_types = Counter()
            for l in learnings:
                context = json.loads(l.get("context", "{}"))
                error_type = context.get("error_type", "unknown")
                error_types[error_type] += 1

            if error_types:
                common_error = error_types.most_common(1)[0]
                suggestions.append(
                    f"🐛 Your most common error: {common_error[0]} ({common_error[1]}x). "
                    f"Check learnings for solutions."
                )

        # Decision insights
        decisions = self.db.get_learnings(category="decision", limit=5)
        if len(decisions) >= 3:
            suggestions.append(
                f"📋 You've made {len(decisions)} documented decisions. "
                f"Great for future reference!"
            )

        return suggestions if suggestions else [
            "Keep coding! I'll learn your patterns as you work."
        ]


if __name__ == "__main__":
    extractor = LearningExtractor()

    print("🧠 Testing Learning Extractor...")
    print()

    # Test error extraction
    error = "ModuleNotFoundError: No module named 'requests'"
    solution = "pip install requests"
    learning = extractor.extract_error_solution(error, solution, "test_session")
    if learning:
        print(f"✅ Extracted learning: {learning.title}")

    # Get personalized suggestions
    print("\n💡 Personalized suggestions:")
    suggestions = extractor.get_personalized_suggestions()
    for s in suggestions:
        print(f"  {s}")

    print("\n✅ Learning extractor ready!")

#!/usr/bin/env python3
"""
Step 3: Best Practice Extractor
Extract AI implementation best practices, guidelines, and lessons learned using Claude 3 Haiku
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv('/Users/yourox/AI-Workspace/.env')

# Initialize Claude client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
MODEL = "claude-3-haiku-20240307"

class BestPracticeExtractor:
    """Extract best practices and guidelines from text"""

    def __init__(self):
        self.extraction_count = 0
        self.total_cost = 0.0
        self.total_tokens = {"input": 0, "output": 0}

    def extract_best_practice(self, text: str, source: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        Extract a best practice from text

        Args:
            text: Document text to extract from
            source: Source of the document (for citation)

        Returns:
            Dictionary with extracted best practice or None if extraction failed
        """

        prompt = f"""Extract AI implementation best practice or guideline from the following text.

A best practice should be actionable advice, do's and don'ts, lessons learned, or implementation guidelines.

Text:
{text}

Respond with valid JSON only, no other text. Use this exact structure:
{{
  "practice_name": "Brief name (e.g., 'Start with Simple Models Before Complex Ones')",
  "category": "Category (e.g., 'implementation', 'data-preparation', 'model-selection', 'deployment', 'governance', 'security')",
  "description": "Detailed explanation of the practice",
  "why_important": "Why this matters and the impact if ignored",
  "dos": ["Do 1", "Do 2", ...],
  "donts": ["Don't 1", "Don't 2", ...],
  "example": "Concrete example of applying this practice",
  "common_pitfalls": ["Pitfall 1", "Pitfall 2", ...],
  "tools_or_techniques": ["Tool/Technique 1", "Tool/Technique 2", ...],
  "when_to_apply": "Context or situations where this applies",
  "effort_level": "low, medium, or high",
  "impact_level": "low, medium, or high",
  "source": "{source}",
  "confidence_score": 0.0-1.0
}}

If no clear best practice is found, respond with: {{"practice_name": null, "confidence_score": 0.0}}
"""

        try:
            start_time = time.time()

            response = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            elapsed = time.time() - start_time
            result_text = response.content[0].text

            # Track usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = (input_tokens / 1_000_000) * 0.25 + (output_tokens / 1_000_000) * 1.25

            self.extraction_count += 1
            self.total_cost += cost
            self.total_tokens['input'] += input_tokens
            self.total_tokens['output'] += output_tokens

            # Parse JSON
            try:
                extracted = json.loads(result_text)

                # Skip if no practice found
                if not extracted.get('practice_name'):
                    return None

                # Add metadata
                extracted['extracted_at'] = time.time()
                extracted['extraction_latency'] = elapsed
                extracted['extraction_cost'] = cost
                extracted['model'] = MODEL

                return extracted

            except json.JSONDecodeError as e:
                print(f"   ⚠️  JSON parse error: {e}")
                print(f"   Raw response: {result_text[:200]}...")
                return None

        except Exception as e:
            print(f"   ❌ Extraction error: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        return {
            "total_extractions": self.extraction_count,
            "total_cost": self.total_cost,
            "avg_cost_per_extraction": self.total_cost / max(self.extraction_count, 1),
            "total_input_tokens": self.total_tokens['input'],
            "total_output_tokens": self.total_tokens['output'],
            "model": MODEL
        }


def test_best_practice_extractor():
    """Test the best practice extractor on sample texts"""

    print("\n" + "="*80)
    print(" "*20 + "BEST PRACTICE EXTRACTOR TEST")
    print("="*80)

    extractor = BestPracticeExtractor()

    # Test samples
    test_samples = [
        {
            "name": "Model Complexity Best Practice",
            "text": """
            Lesson Learned: Start Simple, Then Iterate

            One of the biggest mistakes teams make when implementing AI is jumping straight
            to complex deep learning models without validating simpler approaches first.

            Best Practice: Always start with the simplest model that could reasonably work,
            then gradually increase complexity only if needed.

            Why this matters:
            - Simple models are faster to train and deploy
            - Easier to debug and explain
            - Often perform surprisingly well
            - Establish a baseline for comparison

            DO:
            - Start with logistic regression or random forests
            - Benchmark performance against simple heuristics
            - Document why you need more complexity
            - A/B test simple vs complex models in production

            DON'T:
            - Jump to deep learning without trying simpler models
            - Add complexity for the sake of using "cool" technology
            - Assume complex = better performance
            - Skip establishing a simple baseline

            Example: A retail company wanted to predict customer churn. They started with
            logistic regression (3 days to implement) which achieved 82% accuracy. The
            deep learning model took 6 weeks and achieved only 85% accuracy. They shipped
            the simple model and saved months of engineering time.

            Common Pitfalls:
            - Over-engineering the solution
            - Ignoring maintenance costs of complex models
            - Not considering inference latency
            - Difficulty in explaining predictions to stakeholders

            When to apply: Always, at the start of any new AI project.
            Effort: Low
            Impact: High (saves time, reduces risk)
            """,
            "source": "AI Implementation Guide 2024"
        },
        {
            "name": "Data Quality Best Practice",
            "text": """
            Critical Practice: Invest in Data Quality Before Models

            The quality of your AI model is limited by the quality of your data. Yet many
            teams rush to modeling without ensuring their data is clean and reliable.

            Guideline: Spend 60-70% of your time on data cleaning, validation, and
            feature engineering. Only 30-40% should be on modeling.

            Why it matters:
            - Garbage in = garbage out
            - Poor data quality is the #1 cause of AI project failure
            - Clean data enables faster iteration
            - Better explainability and trust

            DO:
            - Establish data quality metrics (completeness, accuracy, consistency)
            - Implement automated data validation pipelines
            - Document data lineage and transformations
            - Set up alerts for data drift
            - Involve domain experts in data review

            DON'T:
            - Assume your data is correct
            - Skip exploratory data analysis (EDA)
            - Ignore outliers and missing values
            - Trust data without validation
            - Treat data cleaning as a one-time task

            Tools: Great Expectations, dbt, Pandas Profiling, Apache Griffin

            Example: A healthcare AI team spent 2 months building a diagnostic model with
            70% accuracy. After discovering data quality issues (mislabeled images, missing
            metadata), they spent 3 weeks cleaning data. The same model then achieved 94%
            accuracy with no algorithm changes.

            Red flags:
            - Missing values >10%
            - Inconsistent formats across sources
            - Unexplained outliers
            - Data created after target event (data leakage)
            - Imbalanced classes with no business justification
            """,
            "source": "Data Science Best Practices 2024"
        },
        {
            "name": "Product Announcement",
            "text": """
            Exciting News from TechCorp!

            We're thrilled to announce the launch of our new AI product dashboard.
            This new feature will help teams visualize their AI models in real-time.

            Available now for all Enterprise customers. Contact sales for details.
            """,
            "source": "TechCorp Newsletter"
        }
    ]

    results = []

    for i, sample in enumerate(test_samples, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_samples)}: {sample['name']}")
        print(f"{'='*80}")
        print(f"Text length: {len(sample['text'])} characters")

        result = extractor.extract_best_practice(sample['text'], sample['source'])

        if result:
            print(f"✅ Best practice extracted!")
            print(f"   Name: {result['practice_name']}")
            print(f"   Category: {result['category']}")
            print(f"   Do's: {len(result.get('dos', []))} items")
            print(f"   Don'ts: {len(result.get('donts', []))} items")
            print(f"   Pitfalls: {len(result.get('common_pitfalls', []))} items")
            print(f"   Effort: {result.get('effort_level', 'N/A')}")
            print(f"   Impact: {result.get('impact_level', 'N/A')}")
            print(f"   Confidence: {result['confidence_score']}")
            print(f"   Cost: ${result['extraction_cost']:.6f}")
            print(f"   Latency: {result['extraction_latency']:.2f}s")

            results.append(result)
        else:
            print(f"⚠️  No best practice found (expected for non-practice content)")

    # Show statistics
    stats = extractor.get_stats()
    print(f"\n{'='*80}")
    print("EXTRACTION STATISTICS")
    print(f"{'='*80}")
    print(f"Total extractions: {stats['total_extractions']}")
    print(f"Successful: {len(results)}")
    print(f"Total cost: ${stats['total_cost']:.6f}")
    print(f"Avg cost per extraction: ${stats['avg_cost_per_extraction']:.6f}")
    print(f"Total tokens: {stats['total_input_tokens']} in, {stats['total_output_tokens']} out")
    print(f"Model: {stats['model']}")

    # Cost projection
    print(f"\n💰 COST PROJECTION:")
    print(f"   Cost for 100 extractions: ${stats['avg_cost_per_extraction'] * 100:.2f}")
    print(f"   Cost for 1,000 extractions: ${stats['avg_cost_per_extraction'] * 1000:.2f}")
    print(f"   Cost for 10,000 extractions: ${stats['avg_cost_per_extraction'] * 10000:.2f}")

    # Save results
    output_file = '/tmp/intelligence_logs/best_practice_extraction_test.json'
    with open(output_file, 'w') as f:
        json.dump({
            "results": results,
            "stats": stats,
            "timestamp": time.time()
        }, f, indent=2)

    print(f"\n📄 Results saved to: {output_file}")
    print("="*80 + "\n")

    return results, stats


if __name__ == "__main__":
    results, stats = test_best_practice_extractor()

    print("\n✅ Best practice extractor test complete!")
    print(f"✅ Extracted {len(results)} best practices successfully")
    print(f"✅ Average cost: ${stats['avg_cost_per_extraction']:.6f} per practice")
    print(f"✅ Ready for production use!\n")

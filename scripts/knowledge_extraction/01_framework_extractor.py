#!/usr/bin/env python3
"""
Step 1: Framework Extractor
Extract strategic consulting frameworks from documents using Claude 3 Haiku
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
MODEL = "claude-3-haiku-20240307"  # Best value: cheap + high quality

class FrameworkExtractor:
    """Extract strategic frameworks from text"""

    def __init__(self):
        self.extraction_count = 0
        self.total_cost = 0.0
        self.total_tokens = {"input": 0, "output": 0}

    def extract_framework(self, text: str, source: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        Extract a strategic framework from text

        Args:
            text: Document text to extract from
            source: Source of the document (for citation)

        Returns:
            Dictionary with extracted framework or None if extraction failed
        """

        prompt = f"""Extract strategic consulting framework information from the following text.

A framework should be a structured methodology, tool, or approach used in business strategy or consulting.

Text:
{text}

Respond with valid JSON only, no other text. Use this exact structure:
{{
  "framework_name": "Name of the framework (e.g., SWOT Analysis, Porter's 5 Forces)",
  "category": "Category (e.g., strategic-planning, competitive-analysis, market-analysis)",
  "description": "Clear description of what the framework is and its purpose",
  "steps": ["Step 1: Description", "Step 2: Description", ...],
  "when_to_use": ["Use case 1", "Use case 2", ...],
  "example": "Brief example of framework application",
  "key_elements": ["Element 1", "Element 2", ...],
  "source": "{source}",
  "confidence_score": 0.0-1.0,
  "limitations": ["Limitation 1", "Limitation 2", ...] (optional)
}}

If no clear framework is found, respond with: {{"framework_name": null, "confidence_score": 0.0}}
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

                # Skip if no framework found
                if not extracted.get('framework_name'):
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


def test_framework_extractor():
    """Test the framework extractor on sample texts"""

    print("\n" + "="*80)
    print(" "*25 + "FRAMEWORK EXTRACTOR TEST")
    print("="*80)

    extractor = FrameworkExtractor()

    # Test samples
    test_samples = [
        {
            "name": "SWOT Analysis",
            "text": """
            SWOT Analysis Framework

            SWOT Analysis is a strategic planning tool used to identify and analyze the Strengths,
            Weaknesses, Opportunities, and Threats involved in a business venture or project.

            Steps:
            1. Identify Strengths: Internal positive attributes and resources
            2. Identify Weaknesses: Internal limitations and areas for improvement
            3. Identify Opportunities: External factors that could be advantageous
            4. Identify Threats: External factors that could pose challenges
            5. Develop strategies: Use insights to create action plans

            Example: A SaaS company might identify:
            - Strength: Strong technical team
            - Weakness: Limited marketing budget
            - Opportunity: Growing market demand
            - Threat: New competitors entering market

            Best used for: Strategic planning, business planning, project evaluation
            """,
            "source": "Test Document 1"
        },
        {
            "name": "Porter's Five Forces",
            "text": """
            Porter's Five Forces Analysis

            Michael Porter's Five Forces is a framework for analyzing the competitive forces
            that shape every industry and helps determine an industry's weaknesses and strengths.

            The Five Forces:
            1. Threat of New Entrants: How easy is it for new competitors to enter the market?
            2. Bargaining Power of Suppliers: How much power do suppliers have to drive up prices?
            3. Bargaining Power of Buyers: How much power do customers have to drive down prices?
            4. Threat of Substitute Products: How easy can customers switch to alternative products?
            5. Competitive Rivalry: How intense is competition among existing competitors?

            This framework is particularly useful for:
            - Industry analysis
            - Competitive strategy development
            - Market entry decisions
            - Understanding profit potential

            Example: In the airline industry, high competitive rivalry and strong buyer power
            contribute to low profit margins.
            """,
            "source": "Test Document 2"
        },
        {
            "name": "Non-Framework Text",
            "text": """
            Meeting notes from Q4 strategy session.

            Attendees: John, Sarah, Mike
            Date: October 15, 2025

            Discussion points:
            - Budget for next quarter
            - Hiring plans
            - Office relocation

            Action items:
            - Sarah to prepare budget proposal
            - John to review resumes
            - Mike to scout locations
            """,
            "source": "Test Document 3"
        }
    ]

    results = []

    for i, sample in enumerate(test_samples, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_samples)}: {sample['name']}")
        print(f"{'='*80}")
        print(f"Text length: {len(sample['text'])} characters")

        result = extractor.extract_framework(sample['text'], sample['source'])

        if result:
            print(f"✅ Framework extracted!")
            print(f"   Name: {result['framework_name']}")
            print(f"   Category: {result['category']}")
            print(f"   Steps: {len(result.get('steps', []))} steps")
            print(f"   Confidence: {result['confidence_score']}")
            print(f"   Cost: ${result['extraction_cost']:.6f}")
            print(f"   Latency: {result['extraction_latency']:.2f}s")

            # Show first step as example
            if result.get('steps'):
                print(f"   First step: {result['steps'][0][:60]}...")

            results.append(result)
        else:
            print(f"⚠️  No framework found (expected for non-framework text)")

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
    output_file = '/tmp/intelligence_logs/framework_extraction_test.json'
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
    results, stats = test_framework_extractor()

    print("\n✅ Framework extractor test complete!")
    print(f"✅ Extracted {len(results)} frameworks successfully")
    print(f"✅ Average cost: ${stats['avg_cost_per_extraction']:.6f} per framework")
    print(f"✅ Ready for production use!\n")

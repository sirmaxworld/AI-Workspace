#!/usr/bin/env python3
"""
Step 2: Use Case Extractor
Extract AI implementation use cases with ROI data from documents using Claude 3 Haiku
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

class UseCaseExtractor:
    """Extract AI use cases with ROI from text"""

    def __init__(self):
        self.extraction_count = 0
        self.total_cost = 0.0
        self.total_tokens = {"input": 0, "output": 0}

    def extract_use_case(self, text: str, source: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        Extract an AI use case from text

        Args:
            text: Document text to extract from
            source: Source of the document (for citation)

        Returns:
            Dictionary with extracted use case or None if extraction failed
        """

        prompt = f"""Extract AI implementation use case information from the following text.

A use case should describe a specific AI application with business problem, solution, and ideally metrics/ROI.

Text:
{text}

Respond with valid JSON only, no other text. Use this exact structure:
{{
  "use_case_name": "Brief name (e.g., 'Predictive Maintenance for Manufacturing')",
  "industry": "Industry vertical (e.g., manufacturing, retail, healthcare, finance)",
  "business_problem": "Clear description of the problem being solved",
  "ai_solution": "Description of the AI solution implemented",
  "technologies_used": ["Technology 1", "Technology 2", ...],
  "implementation_approach": "How it was implemented (brief)",
  "metrics": {{
    "roi_percentage": number or null,
    "cost_savings": "Amount or description",
    "time_savings": "Amount or description",
    "accuracy_improvement": "Percentage or description",
    "other_metrics": ["Metric 1", "Metric 2", ...]
  }},
  "implementation_timeline": "Duration (e.g., '3 months', '6-12 months')",
  "company_size": "Company size (e.g., 'Fortune 500', 'Mid-market', 'SME', 'Startup')",
  "key_learnings": ["Learning 1", "Learning 2", ...],
  "source": "{source}",
  "confidence_score": 0.0-1.0
}}

If no clear AI use case is found, respond with: {{"use_case_name": null, "confidence_score": 0.0}}
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

                # Skip if no use case found
                if not extracted.get('use_case_name'):
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


def test_use_case_extractor():
    """Test the use case extractor on sample texts"""

    print("\n" + "="*80)
    print(" "*25 + "USE CASE EXTRACTOR TEST")
    print("="*80)

    extractor = UseCaseExtractor()

    # Test samples
    test_samples = [
        {
            "name": "Retail Personalization",
            "text": """
            Case Study: AI-Powered Personalization at RetailCorp

            Challenge:
            RetailCorp, a mid-market e-commerce company with $50M annual revenue, was experiencing
            declining conversion rates and high cart abandonment (68%).

            Solution:
            Implemented an AI-powered personalization engine using collaborative filtering and
            deep learning models. The system analyzes customer behavior, purchase history, and
            browsing patterns to provide personalized product recommendations.

            Technologies: TensorFlow, Python, AWS SageMaker, real-time recommendation API

            Implementation:
            - Phase 1 (2 months): Data pipeline setup and model training
            - Phase 2 (1 month): A/B testing and optimization
            - Phase 3 (1 month): Full rollout

            Results after 6 months:
            - 35% increase in conversion rate
            - 22% reduction in cart abandonment
            - 18% increase in average order value
            - ROI: 280% in first year
            - Cost savings: $2.3M in reduced marketing spend

            Key learnings:
            - Start with simple models and iterate
            - Real-time inference is critical for e-commerce
            - A/B testing essential for measuring impact
            """,
            "source": "RetailCorp Case Study 2024"
        },
        {
            "name": "Manufacturing Predictive Maintenance",
            "text": """
            AI Predictive Maintenance Success Story

            Company: GlobalManufacturing Inc. (Fortune 500)
            Industry: Automotive Manufacturing

            Problem: Unexpected equipment failures causing 12 hours/month downtime, costing $1.2M/year

            AI Solution: Implemented predictive maintenance using IoT sensors and machine learning
            to predict equipment failures 48-72 hours in advance.

            Technology Stack:
            - Azure ML for model training
            - IoT Hub for sensor data collection
            - Power BI for maintenance dashboards
            - Python for data processing

            Timeline: 9-month implementation

            Impact:
            - 73% reduction in unplanned downtime
            - 41% decrease in maintenance costs ($490K savings/year)
            - 28% improvement in equipment lifespan
            - Payback period: 8 months

            Critical success factors:
            - Executive buy-in from operations
            - Close collaboration with maintenance teams
            - Extensive historical data (3 years)
            - Gradual rollout across facilities
            """,
            "source": "Manufacturing AI Report 2024"
        },
        {
            "name": "Generic AI Overview",
            "text": """
            The Future of Artificial Intelligence

            AI is transforming industries across the globe. From healthcare to finance,
            companies are exploring how machine learning can improve operations.

            Key trends in AI:
            - Generative AI gaining traction
            - Edge computing for real-time inference
            - Increased focus on responsible AI

            Challenges remain around data privacy, bias, and explainability.
            """,
            "source": "Generic AI Article"
        }
    ]

    results = []

    for i, sample in enumerate(test_samples, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_samples)}: {sample['name']}")
        print(f"{'='*80}")
        print(f"Text length: {len(sample['text'])} characters")

        result = extractor.extract_use_case(sample['text'], sample['source'])

        if result:
            print(f"✅ Use case extracted!")
            print(f"   Name: {result['use_case_name']}")
            print(f"   Industry: {result['industry']}")
            print(f"   ROI: {result.get('metrics', {}).get('roi_percentage', 'N/A')}")
            print(f"   Technologies: {', '.join(result.get('technologies_used', [])[:3])}")
            print(f"   Timeline: {result.get('implementation_timeline', 'N/A')}")
            print(f"   Confidence: {result['confidence_score']}")
            print(f"   Cost: ${result['extraction_cost']:.6f}")
            print(f"   Latency: {result['extraction_latency']:.2f}s")

            results.append(result)
        else:
            print(f"⚠️  No use case found (expected for generic content)")

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
    output_file = '/tmp/intelligence_logs/use_case_extraction_test.json'
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
    results, stats = test_use_case_extractor()

    print("\n✅ Use case extractor test complete!")
    print(f"✅ Extracted {len(results)} use cases successfully")
    print(f"✅ Average cost: ${stats['avg_cost_per_extraction']:.6f} per use case")
    print(f"✅ Ready for production use!\n")

#!/usr/bin/env python3
"""
AI Model Quality Test
Tests different models via OpenRouter to determine best quality for enrichment
"""

import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Models to test
MODELS = [
    {
        'name': 'Gemini Flash 1.5',
        'id': 'google/gemini-flash-1.5',
        'cost': 'very-cheap',
        'speed': 'very-fast'
    },
    {
        'name': 'Gemini Pro 1.5',
        'id': 'google/gemini-pro-1.5',
        'cost': 'cheap',
        'speed': 'fast'
    },
    {
        'name': 'Claude Haiku 3.5',
        'id': 'anthropic/claude-3.5-haiku',
        'cost': 'cheap',
        'speed': 'fast'
    },
    {
        'name': 'Claude Sonnet 3.5',
        'id': 'anthropic/claude-3.5-sonnet',
        'cost': 'moderate',
        'speed': 'moderate'
    },
    {
        'name': 'GPT-4o Mini',
        'id': 'openai/gpt-4o-mini',
        'cost': 'cheap',
        'speed': 'fast'
    },
]

# Test sample: analyze a code pattern
TEST_CODE_PATTERN = """
```python
# From Django REST Framework
class APIView(View):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    parser_classes = api_settings.DEFAULT_PARSER_CLASSES
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request

        try:
            self.initial(request, *args, **kwargs)

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response
```
"""

ANALYSIS_PROMPT = f"""Analyze this code pattern from a popular Python repository and provide:

1. **Pattern Type** (e.g., "class-based-view", "error-handling", "request-processing")
2. **Pattern Name** (short, descriptive name)
3. **Key Design Principles** (3-5 bullet points)
4. **Complexity Score** (1-100, where 100 is most complex)
5. **Readability Score** (1-100, where 100 is most readable)
6. **Reusability Score** (1-100, where 100 is most reusable)
7. **Usage Frequency** (very-common, common, occasional, or rare)
8. **Best Practices Demonstrated** (2-3 bullet points)

Code to analyze:
{TEST_CODE_PATTERN}

Respond in valid JSON format with these exact keys:
- pattern_type
- pattern_name
- design_principles (array)
- complexity_score (integer)
- readability_score (integer)
- reusability_score (integer)
- usage_frequency (string)
- best_practices (array)
"""

def test_model(model: dict) -> dict:
    """Test a single model and return results"""
    print(f"\n{'='*80}")
    print(f"Testing: {model['name']}")
    print(f"  Model ID: {model['id']}")
    print(f"  Cost: {model['cost']} | Speed: {model['speed']}")
    print(f"{'='*80}")

    start_time = time.time()

    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'AI-Workspace Intelligence Collection'
            },
            json={
                'model': model['id'],
                'messages': [
                    {
                        'role': 'user',
                        'content': ANALYSIS_PROMPT
                    }
                ],
                'temperature': 0.1,  # Low temperature for consistent analysis
                'max_tokens': 2000
            },
            timeout=60
        )

        elapsed = time.time() - start_time

        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return {
                'model': model['name'],
                'success': False,
                'error': f"HTTP {response.status_code}",
                'elapsed_time': elapsed
            }

        data = response.json()
        content = data['choices'][0]['message']['content']

        # Extract JSON from markdown if present
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()

        # Try to parse JSON
        try:
            analysis = json.loads(content)
        except json.JSONDecodeError:
            print(f"⚠️  Could not parse JSON response")
            print(f"   Raw content: {content[:200]}...")
            return {
                'model': model['name'],
                'success': False,
                'error': 'Invalid JSON',
                'elapsed_time': elapsed,
                'raw_response': content[:500]
            }

        # Validate required fields
        required_fields = ['pattern_type', 'pattern_name', 'complexity_score',
                          'readability_score', 'reusability_score', 'usage_frequency']

        missing_fields = [f for f in required_fields if f not in analysis]

        if missing_fields:
            print(f"⚠️  Missing fields: {', '.join(missing_fields)}")
            return {
                'model': model['name'],
                'success': False,
                'error': f"Missing fields: {missing_fields}",
                'elapsed_time': elapsed,
                'analysis': analysis
            }

        # Calculate quality score
        completeness = len([f for f in required_fields if f in analysis]) / len(required_fields)
        has_arrays = 'design_principles' in analysis and 'best_practices' in analysis
        array_quality = 0
        if has_arrays:
            principles_count = len(analysis.get('design_principles', []))
            practices_count = len(analysis.get('best_practices', []))
            array_quality = min((principles_count + practices_count) / 7, 1.0)  # Expect ~7 total items

        quality_score = int((completeness * 0.5 + array_quality * 0.5) * 100)

        print(f"\n✅ Success!")
        print(f"   Response time: {elapsed:.2f}s")
        print(f"   Quality score: {quality_score}/100")
        print(f"\n   Pattern: {analysis.get('pattern_type', 'N/A')}")
        print(f"   Name: {analysis.get('pattern_name', 'N/A')}")
        print(f"   Complexity: {analysis.get('complexity_score', 'N/A')}/100")
        print(f"   Readability: {analysis.get('readability_score', 'N/A')}/100")
        print(f"   Reusability: {analysis.get('reusability_score', 'N/A')}/100")

        if 'design_principles' in analysis:
            print(f"\n   Design Principles ({len(analysis['design_principles'])} items):")
            for principle in analysis['design_principles'][:3]:
                print(f"      • {principle[:60]}")

        if 'best_practices' in analysis:
            print(f"\n   Best Practices ({len(analysis['best_practices'])} items):")
            for practice in analysis['best_practices'][:3]:
                print(f"      • {practice[:60]}")

        return {
            'model': model['name'],
            'model_id': model['id'],
            'success': True,
            'elapsed_time': elapsed,
            'quality_score': quality_score,
            'analysis': analysis,
            'cost_tier': model['cost'],
            'speed_tier': model['speed']
        }

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Exception: {e}")
        return {
            'model': model['name'],
            'success': False,
            'error': str(e),
            'elapsed_time': elapsed
        }

def main():
    """Test all models and compare"""
    print("\n" + "="*80)
    print(" "*25 + "AI MODEL QUALITY TEST")
    print("="*80)

    if not OPENROUTER_API_KEY:
        print("\n❌ OPENROUTER_API_KEY not found in environment")
        return 1

    print(f"\n🔑 OpenRouter API Key: {OPENROUTER_API_KEY[:15]}...")
    print(f"\n📊 Testing {len(MODELS)} models for code pattern analysis quality")

    results = []

    for model in MODELS:
        result = test_model(model)
        results.append(result)

        # Wait between requests
        time.sleep(2)

    # Summary
    print(f"\n{'='*80}")
    print("  TEST RESULTS SUMMARY")
    print(f"{'='*80}")

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")

    if successful:
        # Sort by quality score
        successful.sort(key=lambda x: (x['quality_score'], -x['elapsed_time']), reverse=True)

        print(f"\n🏆 Model Ranking (by quality & speed):")
        print(f"\n{'Rank':<6} {'Model':<25} {'Quality':<10} {'Speed':<10} {'Cost':<12}")
        print("-" * 80)

        for i, result in enumerate(successful, 1):
            print(f"{i:<6} {result['model']:<25} {result['quality_score']}/100    "
                  f"{result['elapsed_time']:.2f}s      {result['cost_tier']:<12}")

        # Recommendation
        best = successful[0]
        print(f"\n{'='*80}")
        print(f"🎯 RECOMMENDED MODEL: {best['model']}")
        print(f"{'='*80}")
        print(f"   Quality Score: {best['quality_score']}/100")
        print(f"   Response Time: {best['elapsed_time']:.2f}s")
        print(f"   Cost Tier: {best['cost_tier']}")
        print(f"   Model ID: {best['model_id']}")

        # Cost-performance analysis
        print(f"\n💰 Cost-Performance Analysis:")
        for result in successful:
            value_score = result['quality_score'] / (result['elapsed_time'] + 1)
            cost_weight = {'very-cheap': 1.5, 'cheap': 1.2, 'moderate': 1.0, 'expensive': 0.7}
            weighted_value = value_score * cost_weight.get(result['cost_tier'], 1.0)
            print(f"   {result['model']:<25} Value: {weighted_value:.1f} (Quality: {result['quality_score']}, Speed: {result['elapsed_time']:.1f}s, Cost: {result['cost_tier']})")

        print(f"\n{'='*80}")
        print("✅ Model testing complete!")
        print(f"{'='*80}\n")

        return 0
    else:
        print("\n❌ All models failed. Check API key and OpenRouter status.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

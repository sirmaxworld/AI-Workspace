#!/usr/bin/env python3
"""
Compare AI Models for Knowledge Extraction
Test quality vs cost for framework/use case extraction
"""

import os
import json
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

# Model configurations with pricing (as of Oct 2025)
MODELS = {
    # Claude Models (Anthropic)
    "claude-3-5-sonnet": {
        "provider": "anthropic",
        "api_name": "claude-3-5-sonnet-20241022",
        "input_cost": 3.00,   # per 1M tokens
        "output_cost": 15.00,  # per 1M tokens
        "context": 200000,
        "description": "Latest Claude, excellent reasoning",
        "best_for": "Complex analysis, high quality extraction"
    },
    "claude-3-5-haiku": {
        "provider": "anthropic",
        "api_name": "claude-3-5-haiku-20241022",
        "input_cost": 1.00,   # per 1M tokens
        "output_cost": 5.00,  # per 1M tokens
        "context": 200000,
        "description": "Fast, intelligent, cost-effective",
        "best_for": "Structured extraction, batch processing"
    },
    "claude-3-haiku": {
        "provider": "anthropic",
        "api_name": "claude-3-haiku-20240307",
        "input_cost": 0.25,   # per 1M tokens
        "output_cost": 1.25,  # per 1M tokens
        "context": 200000,
        "description": "Fastest Claude, very cheap",
        "best_for": "Simple extraction, high volume"
    },

    # GPT Models (OpenAI)
    "gpt-4o": {
        "provider": "openai",
        "api_name": "gpt-4o",
        "input_cost": 2.50,   # per 1M tokens
        "output_cost": 10.00,  # per 1M tokens
        "context": 128000,
        "description": "Latest GPT-4, multimodal",
        "best_for": "Complex extraction, image analysis"
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "api_name": "gpt-4o-mini",
        "input_cost": 0.15,   # per 1M tokens
        "output_cost": 0.60,  # per 1M tokens
        "context": 128000,
        "description": "Fast, cheap, smart",
        "best_for": "High volume, structured extraction"
    },
    "gpt-3.5-turbo": {
        "provider": "openai",
        "api_name": "gpt-3.5-turbo",
        "input_cost": 0.50,   # per 1M tokens
        "output_cost": 1.50,  # per 1M tokens
        "context": 16000,
        "description": "Cheap, fast, lower quality",
        "best_for": "Simple tasks, high volume"
    },

    # Via OpenRouter (cheaper access to multiple models)
    "gemini-flash": {
        "provider": "openrouter",
        "api_name": "google/gemini-flash-1.5",
        "input_cost": 0.075,  # per 1M tokens
        "output_cost": 0.30,  # per 1M tokens
        "context": 1000000,
        "description": "Very cheap, huge context",
        "best_for": "Large documents, budget-conscious"
    },
    "gemini-pro": {
        "provider": "openrouter",
        "api_name": "google/gemini-pro-1.5",
        "input_cost": 1.25,   # per 1M tokens
        "output_cost": 5.00,  # per 1M tokens
        "context": 2000000,
        "description": "Massive context, good quality",
        "best_for": "Huge documents, deep analysis"
    },
    "llama-70b": {
        "provider": "openrouter",
        "api_name": "meta-llama/llama-3.1-70b-instruct",
        "input_cost": 0.52,   # per 1M tokens
        "output_cost": 0.75,  # per 1M tokens
        "context": 131000,
        "description": "Open source, good quality",
        "best_for": "Cost-effective, privacy-conscious"
    },
    "mixtral-8x7b": {
        "provider": "openrouter",
        "api_name": "mistralai/mixtral-8x7b-instruct",
        "input_cost": 0.24,   # per 1M tokens
        "output_cost": 0.24,  # per 1M tokens
        "context": 32000,
        "description": "Very cheap, decent quality",
        "best_for": "Budget extraction, high volume"
    }
}

def print_model_comparison():
    """Print comparison table of all models"""
    print("\n" + "="*120)
    print(" "*40 + "AI MODEL COMPARISON FOR KNOWLEDGE EXTRACTION")
    print("="*120)
    print(f"\n{'Model':<20} {'Provider':<12} {'Input $/1M':<12} {'Output $/1M':<12} {'Context':<12} {'Best For':<40}")
    print("-"*120)

    # Sort by total cost (estimate 1K input, 500 output tokens per extraction)
    models_sorted = sorted(
        MODELS.items(),
        key=lambda x: (x[1]['input_cost'] * 0.001 + x[1]['output_cost'] * 0.0005)
    )

    for name, config in models_sorted:
        est_cost = (config['input_cost'] * 0.001 + config['output_cost'] * 0.0005) * 1000  # per 1000 extractions
        print(f"{name:<20} {config['provider']:<12} ${config['input_cost']:<11.2f} ${config['output_cost']:<11.2f} {config['context']:<12,} {config['best_for']:<40}")

    print("\n" + "="*120)
    print("💡 Cost Estimates (per 1,000 extractions, assuming 1K input + 500 output tokens):")
    print("-"*120)

    for name, config in models_sorted:
        cost_per_1k = (config['input_cost'] * 0.001 + config['output_cost'] * 0.0005) * 1000
        print(f"  {name:<30} ${cost_per_1k:>8.2f}")

    print("\n" + "="*120)


def test_extraction(model_config: Dict, sample_text: str, task: str) -> Dict[str, Any]:
    """Test extraction with a specific model"""
    provider = model_config['provider']
    model_name = model_config['api_name']

    prompt = f"""Extract structured information from the following text.

Task: {task}

Text:
{sample_text}

Respond with valid JSON only, no other text. Use this structure:
{{
  "framework_name": "...",
  "category": "...",
  "description": "...",
  "steps": ["...", "..."],
  "examples": ["...", "..."],
  "source": "...",
  "confidence_score": 0.0-1.0
}}
"""

    start_time = time.time()

    try:
        if provider == "anthropic":
            from anthropic import Anthropic
            client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

            response = client.messages.create(
                model=model_name,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

        elif provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )

            result = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

        elif provider == "openrouter":
            import requests

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "HTTP-Referer": "https://ai-workspace.local",
                    "X-Title": "AI Workspace Knowledge Extraction"
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.3
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                result = data['choices'][0]['message']['content']
                input_tokens = data.get('usage', {}).get('prompt_tokens', 0)
                output_tokens = data.get('usage', {}).get('completion_tokens', 0)
            else:
                raise Exception(f"OpenRouter error: {response.status_code} - {response.text}")

        elapsed = time.time() - start_time

        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * model_config['input_cost']
        output_cost = (output_tokens / 1_000_000) * model_config['output_cost']
        total_cost = input_cost + output_cost

        # Try to parse JSON
        try:
            parsed = json.loads(result)
            json_valid = True
        except:
            parsed = None
            json_valid = False

        return {
            "success": True,
            "result": result,
            "parsed": parsed,
            "json_valid": json_valid,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost,
            "latency": elapsed,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "result": None,
            "parsed": None,
            "json_valid": False,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0,
            "latency": time.time() - start_time,
            "error": str(e)
        }


def run_extraction_tests():
    """Run extraction tests on multiple models"""

    # Sample consulting framework text
    sample_text = """
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

    Best used for: Strategic planning, business planning, project evaluation, market analysis
    """

    task = "Extract the strategic framework details including name, steps, examples, and use cases"

    print("\n" + "="*120)
    print(" "*40 + "EXTRACTION QUALITY TEST")
    print("="*120)
    print("\nTesting extraction on sample SWOT analysis text...")
    print(f"Sample length: {len(sample_text)} characters\n")

    # Test subset of models (cheap, mid, expensive)
    test_models = [
        "claude-3-haiku",       # Cheapest Claude
        "claude-3-5-haiku",     # Mid Claude
        "claude-3-5-sonnet",    # Best Claude
        "gpt-4o-mini",          # Cheap GPT
        "gpt-4o",               # Best GPT
        "gemini-flash",         # Cheapest overall
        "mixtral-8x7b"          # Open source
    ]

    results = {}

    for model_name in test_models:
        if model_name not in MODELS:
            continue

        print(f"\n{'='*120}")
        print(f"🧪 Testing: {model_name} ({MODELS[model_name]['description']})")
        print(f"{'='*120}")

        model_config = MODELS[model_name]
        result = test_extraction(model_config, sample_text, task)
        results[model_name] = result

        if result['success']:
            print(f"✅ Success!")
            print(f"   Latency: {result['latency']:.2f}s")
            print(f"   Cost: ${result['cost']:.6f}")
            print(f"   Tokens: {result['input_tokens']} in, {result['output_tokens']} out")
            print(f"   JSON Valid: {'✅' if result['json_valid'] else '❌'}")

            if result['json_valid'] and result['parsed']:
                print(f"\n   Extracted Data:")
                print(f"   - Name: {result['parsed'].get('framework_name', 'N/A')}")
                print(f"   - Steps: {len(result['parsed'].get('steps', []))} steps")
                print(f"   - Confidence: {result['parsed'].get('confidence_score', 'N/A')}")
        else:
            print(f"❌ Failed: {result['error']}")

    # Summary comparison
    print("\n\n" + "="*120)
    print(" "*40 + "RESULTS SUMMARY")
    print("="*120)
    print(f"\n{'Model':<25} {'Success':<10} {'JSON Valid':<12} {'Cost':<12} {'Latency':<12} {'Quality':<15}")
    print("-"*120)

    for model_name, result in results.items():
        if result['success']:
            success = "✅"
            json_valid = "✅" if result['json_valid'] else "❌"
            cost = f"${result['cost']:.6f}"
            latency = f"{result['latency']:.2f}s"

            # Simple quality score based on confidence and completeness
            if result['json_valid'] and result['parsed']:
                conf = result['parsed'].get('confidence_score', 0)
                steps = len(result['parsed'].get('steps', []))
                quality = f"{conf:.2f} / {steps} steps"
            else:
                quality = "N/A"
        else:
            success = "❌"
            json_valid = "N/A"
            cost = "N/A"
            latency = f"{result['latency']:.2f}s"
            quality = "N/A"

        print(f"{model_name:<25} {success:<10} {json_valid:<12} {cost:<12} {latency:<12} {quality:<15}")

    print("\n" + "="*120)
    print("💡 RECOMMENDATIONS")
    print("="*120)

    # Find best value (quality per dollar)
    successful_results = [(name, r) for name, r in results.items() if r['success'] and r['json_valid']]

    if successful_results:
        # Best quality
        best_quality = max(successful_results,
                          key=lambda x: x[1]['parsed'].get('confidence_score', 0) if x[1]['parsed'] else 0)
        print(f"\n🏆 Best Quality: {best_quality[0]}")

        # Cheapest working
        cheapest = min(successful_results, key=lambda x: x[1]['cost'])
        print(f"💰 Cheapest: {cheapest[0]} (${cheapest[1]['cost']:.6f} per extraction)")

        # Best value (quality/cost ratio)
        best_value = max(successful_results,
                        key=lambda x: (x[1]['parsed'].get('confidence_score', 0) if x[1]['parsed'] else 0) / max(x[1]['cost'], 0.000001))
        print(f"⚖️  Best Value: {best_value[0]}")

        # Fastest
        fastest = min(successful_results, key=lambda x: x[1]['latency'])
        print(f"⚡ Fastest: {fastest[0]} ({fastest[1]['latency']:.2f}s)")

    print("\n" + "="*120)

    # Save results
    output_file = '/tmp/intelligence_logs/model_comparison_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'models_tested': list(results.keys()),
            'results': results,
            'timestamp': time.time()
        }, f, indent=2, default=str)

    print(f"\n📄 Detailed results saved to: {output_file}")
    print("="*120 + "\n")

    return results


def main():
    """Main comparison process"""
    print("\n" + "="*120)
    print(" "*30 + "AI MODEL COMPARISON FOR KNOWLEDGE EXTRACTION")
    print("="*120)

    # Step 1: Show pricing comparison
    print_model_comparison()

    # Step 2: Run quality tests
    print("\n\n🧪 Running extraction quality tests...")
    print("This will test actual extraction quality on sample consulting framework text.\n")

    try:
        results = run_extraction_tests()

        print("\n✅ Comparison complete!")
        print("\nNext step: Use the recommended model for building extraction pipeline")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

    return 0


if __name__ == "__main__":
    exit(main())

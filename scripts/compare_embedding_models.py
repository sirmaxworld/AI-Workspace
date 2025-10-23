#!/usr/bin/env python3
"""
Compare Embedding Models
Tests quality, speed, and cost of different embedding providers
"""

import os
import time
import json
import psycopg2
import psycopg2.extras
import numpy as np
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

load_dotenv('/Users/yourox/AI-Workspace/.env')

# Test sample - representative coding intelligence
TEST_SAMPLES = [
    {
        "text": "Jest Testing Framework (JavaScript, testing): Uses Jest for testing with snapshot support and mocking capabilities",
        "category": "pattern",
        "expected_similar": ["pytest", "mocha", "testing", "unit test", "mock"]
    },
    {
        "text": "Always validate user input (best-practice, Python): Never trust user input, always sanitize and validate before processing",
        "category": "rule",
        "expected_similar": ["security", "validation", "sanitize", "input checking"]
    },
    {
        "text": "dayjs (JavaScript, MIT): Fast 2kB alternative to Moment.js with same API",
        "category": "oss",
        "expected_similar": ["date library", "moment", "time formatting", "lightweight"]
    },
]

# Embedding models to compare
MODELS_TO_TEST = {
    "openai-small": {
        "provider": "openai",
        "model": "text-embedding-3-small",
        "dimension": 1536,
        "cost_per_1k_tokens": 0.00002,
        "description": "OpenAI's small embedding model"
    },
    "openai-large": {
        "provider": "openai",
        "model": "text-embedding-3-large",
        "dimension": 3072,
        "cost_per_1k_tokens": 0.00013,
        "description": "OpenAI's large embedding model (higher quality)"
    },
    "openrouter-jina": {
        "provider": "openrouter",
        "model": "jina-ai/jina-embeddings-v3",
        "dimension": 1024,
        "cost_per_1k_tokens": 0.00002,
        "description": "Jina AI embeddings via OpenRouter"
    },
    "local-sentence-transformers": {
        "provider": "local",
        "model": "all-MiniLM-L6-v2",
        "dimension": 384,
        "cost_per_1k_tokens": 0.0,
        "description": "Local Sentence Transformers (free, fast)"
    }
}

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a_np = np.array(a)
    b_np = np.array(b)
    return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))

def get_openai_embedding(text: str, model: str) -> Optional[List[float]]:
    """Generate embedding using OpenAI"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"      ❌ OpenAI error: {e}")
        return None

def get_openrouter_embedding(text: str, model: str) -> Optional[List[float]]:
    """Generate embedding using OpenRouter"""
    try:
        import requests

        response = requests.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "https://ai-workspace.local",
                "X-Title": "AI Workspace Embeddings"
            },
            json={
                "model": model,
                "input": text
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data['data'][0]['embedding']
        else:
            print(f"      ❌ OpenRouter error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"      ❌ OpenRouter error: {e}")
        return None

def get_local_embedding(text: str, model: str) -> Optional[List[float]]:
    """Generate embedding using local Sentence Transformers"""
    try:
        from sentence_transformers import SentenceTransformer

        # Load model (cached after first load)
        st_model = SentenceTransformer(model)
        embedding = st_model.encode(text)
        return embedding.tolist()
    except ImportError:
        print(f"      ⚠️  sentence-transformers not installed. Install with: pip install sentence-transformers")
        return None
    except Exception as e:
        print(f"      ❌ Local model error: {e}")
        return None

def get_embedding(text: str, model_config: Dict) -> Optional[List[float]]:
    """Generate embedding using specified provider"""
    provider = model_config['provider']
    model = model_config['model']

    if provider == 'openai':
        return get_openai_embedding(text, model)
    elif provider == 'openrouter':
        return get_openrouter_embedding(text, model)
    elif provider == 'local':
        return get_local_embedding(text, model)
    else:
        print(f"      ❌ Unknown provider: {provider}")
        return None

def test_model(model_name: str, model_config: Dict) -> Dict:
    """Test a single embedding model"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {model_name}")
    print(f"   Provider: {model_config['provider']}")
    print(f"   Model: {model_config['model']}")
    print(f"   Dimension: {model_config['dimension']}")
    print(f"   Cost: ${model_config['cost_per_1k_tokens']:.5f} per 1K tokens")
    print(f"{'='*80}")

    results = {
        "model_name": model_name,
        "config": model_config,
        "embeddings_generated": 0,
        "avg_time": 0,
        "success": False,
        "errors": []
    }

    embeddings = []
    times = []

    # Generate embeddings for test samples
    for i, sample in enumerate(TEST_SAMPLES):
        print(f"\n   Sample {i+1}/{len(TEST_SAMPLES)}: {sample['category']}")
        print(f"   Text: {sample['text'][:80]}...")

        start_time = time.time()
        embedding = get_embedding(sample['text'], model_config)
        elapsed = time.time() - start_time

        if embedding:
            embeddings.append(embedding)
            times.append(elapsed)
            results['embeddings_generated'] += 1
            print(f"   ✅ Generated in {elapsed:.2f}s (dimension: {len(embedding)})")
        else:
            results['errors'].append(f"Failed to generate embedding for sample {i+1}")
            print(f"   ❌ Failed to generate embedding")

    if times:
        results['avg_time'] = sum(times) / len(times)
        results['success'] = True

    # Test semantic similarity
    if len(embeddings) >= 2:
        print(f"\n   📊 Similarity Tests:")

        # Pattern vs Pattern (should be high)
        if len(embeddings) > 0:
            pattern_pattern_sim = cosine_similarity(embeddings[0], embeddings[0])
            print(f"   • Pattern vs itself: {pattern_pattern_sim:.4f} (expect ~1.0)")

        # Pattern vs Rule (should be medium)
        if len(embeddings) >= 2:
            pattern_rule_sim = cosine_similarity(embeddings[0], embeddings[1])
            print(f"   • Pattern vs Rule: {pattern_rule_sim:.4f} (expect ~0.3-0.6)")

        # Pattern vs OSS (should be medium-low)
        if len(embeddings) >= 3:
            pattern_oss_sim = cosine_similarity(embeddings[0], embeddings[2])
            print(f"   • Pattern vs OSS: {pattern_oss_sim:.4f} (expect ~0.2-0.5)")

        results['similarity_tests'] = {
            'pattern_self': pattern_pattern_sim if len(embeddings) > 0 else None,
            'pattern_rule': pattern_rule_sim if len(embeddings) >= 2 else None,
            'pattern_oss': pattern_oss_sim if len(embeddings) >= 3 else None
        }

    return results

def estimate_total_cost(model_config: Dict, total_items: int = 2344, avg_tokens: int = 200) -> float:
    """Estimate cost for embedding all our data"""
    total_tokens = total_items * avg_tokens
    cost = (total_tokens / 1000) * model_config['cost_per_1k_tokens']
    return cost

def main():
    """Main comparison process"""
    print("\n" + "="*80)
    print(" "*20 + "EMBEDDING MODEL COMPARISON")
    print("="*80)

    print(f"\n📋 Testing {len(MODELS_TO_TEST)} embedding models:")
    for name, config in MODELS_TO_TEST.items():
        print(f"   • {name}: {config['description']}")

    # Test each model
    results = {}

    for model_name, model_config in MODELS_TO_TEST.items():
        try:
            result = test_model(model_name, model_config)
            results[model_name] = result

            # Brief pause between tests
            time.sleep(1)
        except Exception as e:
            print(f"\n❌ Error testing {model_name}: {e}")
            results[model_name] = {
                "model_name": model_name,
                "success": False,
                "error": str(e)
            }

    # Comparison summary
    print(f"\n\n{'='*80}")
    print("📊 COMPARISON SUMMARY")
    print(f"{'='*80}")

    print(f"\n{'Model':<30} {'Success':<10} {'Speed':<12} {'Dimension':<12} {'Cost (est)':<15}")
    print("-" * 80)

    for model_name in MODELS_TO_TEST.keys():
        result = results.get(model_name, {})

        if result.get('success'):
            success = "✅ Yes"
            speed = f"{result['avg_time']:.2f}s"
            dimension = str(MODELS_TO_TEST[model_name]['dimension'])
            cost = estimate_total_cost(MODELS_TO_TEST[model_name])
            cost_str = f"${cost:.4f}"
        else:
            success = "❌ No"
            speed = "N/A"
            dimension = "N/A"
            cost_str = "N/A"

        print(f"{model_name:<30} {success:<10} {speed:<12} {dimension:<12} {cost_str:<15}")

    # Recommendations
    print(f"\n{'='*80}")
    print("💡 RECOMMENDATIONS")
    print(f"{'='*80}")

    # Find best by different criteria
    successful_models = {k: v for k, v in results.items() if v.get('success')}

    if successful_models:
        # Best by speed
        fastest = min(successful_models.items(), key=lambda x: x[1]['avg_time'])
        print(f"\n⚡ Fastest: {fastest[0]} ({fastest[1]['avg_time']:.2f}s per embedding)")

        # Best by cost
        cheapest_model = min(
            [(k, MODELS_TO_TEST[k]) for k, v in successful_models.items()],
            key=lambda x: x[1]['cost_per_1k_tokens']
        )
        cost = estimate_total_cost(cheapest_model[1])
        print(f"\n💰 Cheapest: {cheapest_model[0]} (${cost:.4f} total)")

        # Best balance
        print(f"\n⚖️  Recommended for production:")
        print(f"   • OpenAI text-embedding-3-small: Good quality, low cost, proven")
        print(f"   • Local sentence-transformers: Free, fast, privacy-friendly")
        print(f"   • OpenAI text-embedding-3-large: Highest quality (if budget allows)")
    else:
        print("\n⚠️  No models successfully tested. Check API keys and credentials.")

    # Save results
    results_file = '/tmp/intelligence_logs/embedding_comparison.json'
    with open(results_file, 'w') as f:
        json.dump({
            'models_tested': MODELS_TO_TEST,
            'results': results,
            'timestamp': time.time()
        }, f, indent=2)

    print(f"\n📄 Detailed results saved to: {results_file}")

    print(f"\n{'='*80}")
    print("✅ COMPARISON COMPLETE")
    print(f"{'='*80}\n")

    return 0

if __name__ == "__main__":
    exit(main())

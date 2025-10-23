#!/usr/bin/env python3
"""
AI Intelligence Enricher
Uses Claude Haiku 3.5 via OpenRouter to enrich coding patterns with AI analysis
Based on quality test results: Haiku scored 100/100 quality, 3.81s speed, cheap cost
"""

import os
import json
import time
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv('/Users/yourox/AI-Workspace/.env')

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Use best performing model from tests
MODEL_ID = 'anthropic/claude-3.5-haiku'
MODEL_NAME = 'Claude Haiku 3.5'

def get_db_connection():
    """Get Railway PostgreSQL connection"""
    return psycopg2.connect(
        os.getenv('RAILWAY_DATABASE_URL'),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def analyze_coding_pattern_with_ai(code_example: str, context: Dict) -> Optional[Dict]:
    """
    Analyze a code pattern using AI

    Args:
        code_example: The code to analyze
        context: Additional context (language, repo, file_path)

    Returns:
        Analysis dict or None on error
    """

    prompt = f"""Analyze this code pattern from a popular {context.get('language', 'programming')} repository and provide structured insights.

Repository: {context.get('repo_name', 'N/A')}
Language: {context.get('language', 'N/A')}
File: {context.get('file_path', 'N/A')}

Code:
```{context.get('language', '').lower()}
{code_example}
```

Provide a comprehensive analysis in valid JSON format with these exact keys:

{{
  "pattern_type": "string (e.g., 'error-handling', 'state-management', 'api-design')",
  "pattern_name": "string (short, descriptive name)",
  "description": "string (2-3 sentence description)",
  "design_principles": ["array of 3-5 key design principles"],
  "complexity_score": integer (1-100, where 100 is most complex),
  "readability_score": integer (1-100, where 100 is most readable),
  "reusability_score": integer (1-100, where 100 is most reusable),
  "usage_frequency": "string ('very-common', 'common', 'occasional', or 'rare')",
  "best_practices": ["array of 2-4 best practices demonstrated"],
  "anti_patterns_avoided": ["array of 1-3 anti-patterns that this code avoids"],
  "when_to_use": "string (1-2 sentences on when to use this pattern)",
  "alternatives": ["array of 0-2 alternative patterns"]
}}

Respond ONLY with the JSON object, no markdown formatting."""

    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'AI-Workspace Intelligence Enrichment'
            },
            json={
                'model': MODEL_ID,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.1,
                'max_tokens': 2000
            },
            timeout=60
        )

        if response.status_code != 200:
            print(f"      ⚠️ API Error: {response.status_code}")
            return None

        data = response.json()
        content = data['choices'][0]['message']['content']

        # Clean JSON from markdown
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()

        analysis = json.loads(content)
        return analysis

    except Exception as e:
        print(f"      ❌ Error analyzing pattern: {e}")
        return None

def enrich_github_patterns(limit: int = 100):
    """Enrich coding patterns from GitHub repos with AI analysis"""
    print(f"\n{'='*80}")
    print(f"  ENRICHING GITHUB PATTERNS WITH {MODEL_NAME}")
    print(f"{'='*80}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get patterns without AI analysis
    cursor.execute("""
        SELECT p.id, p.code_example, p.pattern_type, p.pattern_name,
               p.language, p.file_path, r.repo_full_name
        FROM coding_patterns p
        JOIN github_repositories r ON p.repo_id = r.id
        WHERE p.ai_analysis IS NULL AND p.code_example IS NOT NULL
        ORDER BY r.stars DESC
        LIMIT %s;
    """, (limit,))

    patterns = cursor.fetchall()

    if not patterns:
        print("\n✅ All patterns already enriched!")
        cursor.close()
        conn.close()
        return

    print(f"\n📊 Found {len(patterns)} patterns to enrich")

    enriched_count = 0
    skipped_count = 0

    for i, pattern in enumerate(patterns, 1):
        try:
            print(f"\n   [{i}/{len(patterns)}] {pattern['repo_full_name']}")
            print(f"      Pattern: {pattern.get('pattern_name', 'Unnamed')}")

            # Prepare context
            context = {
                'repo_name': pattern['repo_full_name'],
                'language': pattern['language'],
                'file_path': pattern.get('file_path', '')
            }

            # Analyze with AI
            analysis = analyze_coding_pattern_with_ai(pattern['code_example'], context)

            if analysis:
                # Update pattern with AI analysis
                cursor.execute("""
                    UPDATE coding_patterns SET
                        ai_analysis = %s,
                        complexity_score = %s,
                        readability_score = %s,
                        reusability_score = %s
                    WHERE id = %s;
                """, (
                    json.dumps(analysis),
                    analysis.get('complexity_score'),
                    analysis.get('readability_score'),
                    analysis.get('reusability_score'),
                    pattern['id']
                ))

                enriched_count += 1
                print(f"      ✅ Enriched (Complexity: {analysis.get('complexity_score')}, "
                      f"Readability: {analysis.get('readability_score')}, "
                      f"Reusability: {analysis.get('reusability_score')})")

                # Commit every 10 patterns
                if i % 10 == 0:
                    conn.commit()
                    print(f"\n   💾 Committed {i} patterns...")

                # Rate limiting
                time.sleep(1)
            else:
                skipped_count += 1
                print(f"      ⏭️ Skipped (analysis failed)")

        except Exception as e:
            print(f"      ❌ Error: {e}")
            skipped_count += 1
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n{'='*80}")
    print(f"✅ Enrichment complete!")
    print(f"   Enriched: {enriched_count}/{len(patterns)}")
    print(f"   Skipped: {skipped_count}")
    print(f"{'='*80}")

def enrich_coding_rules(limit: int = 50):
    """Enrich coding rules with AI insights"""
    print(f"\n{'='*80}")
    print(f"  ENRICHING CODING RULES WITH {MODEL_NAME}")
    print(f"{'='*80}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get rules without AI analysis
    cursor.execute("""
        SELECT cr.id, cr.rule_title, cr.rule_description, cr.rule_category,
               cr.good_example, cr.bad_example, r.repo_full_name, r.language
        FROM coding_rules cr
        JOIN github_repositories r ON cr.repo_id = r.id
        WHERE cr.rule_data IS NULL
        ORDER BY r.stars DESC
        LIMIT %s;
    """, (limit,))

    rules = cursor.fetchall()

    if not rules:
        print("\n✅ All rules already enriched!")
        cursor.close()
        conn.close()
        return

    print(f"\n📊 Found {len(rules)} rules to enrich")

    enriched_count = 0

    for i, rule in enumerate(rules, 1):
        try:
            print(f"\n   [{i}/{len(rules)}] {rule['rule_title'][:50]}")

            # Create analysis prompt
            prompt = f"""Analyze this coding rule and provide insights in JSON format:

Title: {rule['rule_title']}
Category: {rule['rule_category']}
Description: {rule['rule_description']}
Repository: {rule['repo_full_name']}
Language: {rule['language']}

Provide:
{{
  "impact_assessment": "string (why this rule matters)",
  "enforcement_difficulty": "string ('easy', 'moderate', 'hard')",
  "common_violations": ["array of 2-3 common ways this rule is violated"],
  "benefits": ["array of 2-3 benefits of following this rule"],
  "related_rules": ["array of 0-2 related rules"]
}}"""

            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'http://localhost:3000',
                    'X-Title': 'AI-Workspace Rule Enrichment'
                },
                json={
                    'model': MODEL_ID,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.1,
                    'max_tokens': 1000
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']

                # Clean JSON
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()

                analysis = json.loads(content)

                # Update rule
                cursor.execute("""
                    UPDATE coding_rules SET
                        rule_data = %s
                    WHERE id = %s;
                """, (json.dumps(analysis), rule['id']))

                enriched_count += 1
                print(f"      ✅ Enriched")

                if i % 10 == 0:
                    conn.commit()
                    print(f"\n   💾 Committed {i} rules...")

                time.sleep(0.8)

        except Exception as e:
            print(f"      ⚠️ Error: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n{'='*80}")
    print(f"✅ Rule enrichment complete!")
    print(f"   Enriched: {enriched_count}/{len(rules)}")
    print(f"{'='*80}")

def show_enrichment_summary():
    """Show summary of enriched data"""
    print(f"\n{'='*80}")
    print("  ENRICHMENT SUMMARY")
    print(f"{'='*80}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Patterns enriched
    cursor.execute("SELECT COUNT(*) as count FROM coding_patterns WHERE ai_analysis IS NOT NULL;")
    patterns_enriched = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM coding_patterns;")
    patterns_total = cursor.fetchone()['count']

    # Rules enriched
    cursor.execute("SELECT COUNT(*) as count FROM coding_rules WHERE rule_data IS NOT NULL;")
    rules_enriched = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM coding_rules;")
    rules_total = cursor.fetchone()['count']

    print(f"\n📊 Patterns: {patterns_enriched:,}/{patterns_total:,} enriched "
          f"({patterns_enriched/patterns_total*100:.1f}%)" if patterns_total > 0 else "\n📊 Patterns: 0/0 enriched")
    print(f"📊 Rules: {rules_enriched:,}/{rules_total:,} enriched "
          f"({rules_enriched/rules_total*100:.1f}%)" if rules_total > 0 else "📊 Rules: 0/0 enriched")

    # Top enriched patterns by scores
    cursor.execute("""
        SELECT p.pattern_name, p.complexity_score, p.readability_score,
               p.reusability_score, r.repo_full_name
        FROM coding_patterns p
        JOIN github_repositories r ON p.repo_id = r.id
        WHERE p.ai_analysis IS NOT NULL
        ORDER BY p.reusability_score DESC
        LIMIT 10;
    """)
    top_patterns = cursor.fetchall()

    if top_patterns:
        print(f"\n🏆 Top 10 Most Reusable Patterns:")
        for i, pattern in enumerate(top_patterns, 1):
            print(f"   {i:2d}. {pattern['pattern_name'][:40]:40s} | "
                  f"R:{pattern['reusability_score']:3d} C:{pattern['complexity_score']:3d} "
                  f"RB:{pattern['readability_score']:3d} | {pattern['repo_full_name'][:30]}")

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")

def main():
    """Main enrichment process"""
    print("\n" + "="*80)
    print(" "*20 + "AI INTELLIGENCE ENRICHMENT")
    print("="*80)
    print(f"\nUsing: {MODEL_NAME} (Best quality/speed from tests)")

    if not OPENROUTER_API_KEY:
        print("\n❌ OPENROUTER_API_KEY not found")
        return 1

    start_time = time.time()

    # Enrich patterns
    enrich_github_patterns(limit=100)  # Start with 100

    # Enrich rules
    enrich_coding_rules(limit=50)  # Start with 50

    elapsed = time.time() - start_time

    print(f"\n{'='*80}")
    print(f"✅ AI Enrichment complete in {elapsed/60:.1f} minutes")
    print(f"{'='*80}")

    # Show summary
    show_enrichment_summary()

if __name__ == "__main__":
    import sys
    sys.exit(main())

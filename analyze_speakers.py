#!/usr/bin/env python3
"""
Analyze transcripts for speaker identification possibilities
"""
import json
import re
from pathlib import Path
from collections import defaultdict, Counter

def analyze_speaker_patterns(transcript_file):
    """Analyze a transcript for speaker patterns and dialogue markers"""

    with open(transcript_file, 'r') as f:
        data = json.load(f)

    segments = data.get('transcript', {}).get('segments', [])
    title = data.get('title', 'Unknown')

    print(f"\nAnalyzing: {title[:60]}...")
    print("-" * 60)

    # Check if segments have speaker info
    has_speaker_field = any('speaker' in seg for seg in segments[:10])
    print(f"Has speaker field: {has_speaker_field}")

    if has_speaker_field:
        speakers = Counter([seg.get('speaker', 'Unknown') for seg in segments])
        print(f"Speakers found: {dict(speakers)}")

    # Analyze text patterns for dialogue
    dialogue_patterns = {
        'question_marks': 0,
        'i_statements': 0,
        'you_statements': 0,
        'we_statements': 0,
        'quote_marks': 0,
        'names_mentioned': set()
    }

    # Common podcast/interview patterns
    interview_indicators = []
    consecutive_questions = 0
    last_was_question = False

    for i, seg in enumerate(segments[:100]):  # Check first 100 segments
        text = seg['text'].lower()

        # Check for questions
        if '?' in text:
            dialogue_patterns['question_marks'] += 1
            consecutive_questions = consecutive_questions + 1 if last_was_question else 1
            last_was_question = True
            if consecutive_questions >= 2:
                interview_indicators.append(f"Multiple questions at segment {i}")
        else:
            last_was_question = False
            consecutive_questions = 0

        # Personal pronouns (dialogue indicators)
        if re.search(r'\bi\b', text):
            dialogue_patterns['i_statements'] += 1
        if re.search(r'\byou\b', text):
            dialogue_patterns['you_statements'] += 1
        if re.search(r'\bwe\b', text):
            dialogue_patterns['we_statements'] += 1

        # Check for quotes
        if '"' in text or "'" in text:
            dialogue_patterns['quote_marks'] += 1

        # Look for name patterns (capitalized words that might be names)
        words = text.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 2:
                dialogue_patterns['names_mentioned'].add(word)

    # Analyze conversation flow
    print(f"\nDialogue Indicators:")
    print(f"  Questions: {dialogue_patterns['question_marks']}")
    print(f"  'I' statements: {dialogue_patterns['i_statements']}")
    print(f"  'You' statements: {dialogue_patterns['you_statements']}")
    print(f"  'We' statements: {dialogue_patterns['we_statements']}")

    # Detect conversation type
    total_segments_checked = min(100, len(segments))
    question_ratio = dialogue_patterns['question_marks'] / total_segments_checked
    you_ratio = dialogue_patterns['you_statements'] / total_segments_checked

    print(f"\nConversation Type Analysis:")
    if question_ratio > 0.1 and you_ratio > 0.15:
        print("  ✓ Likely an INTERVIEW/PODCAST (high question + 'you' ratio)")
        conversation_type = "interview"
    elif dialogue_patterns['i_statements'] > 30:
        print("  ✓ Likely a MONOLOGUE/PRESENTATION (high 'I' statements)")
        conversation_type = "monologue"
    else:
        print("  ? Unclear conversation type")
        conversation_type = "unknown"

    # Try to identify speaker changes through pattern analysis
    print(f"\nPotential Speaker Changes (heuristic):")
    speaker_changes = []

    for i in range(1, min(50, len(segments))):
        prev_text = segments[i-1]['text']
        curr_text = segments[i]['text']
        time_gap = segments[i]['start'] - (segments[i-1]['start'] + segments[i-1]['duration'])

        # Heuristics for speaker change
        change_indicators = 0

        # Large time gap
        if time_gap > 1.0:
            change_indicators += 1

        # Question followed by answer pattern
        if '?' in prev_text and '?' not in curr_text:
            change_indicators += 2

        # Significant pause after statement
        if prev_text.rstrip().endswith('.') and time_gap > 0.5:
            change_indicators += 1

        if change_indicators >= 2:
            speaker_changes.append({
                'segment': i,
                'time': segments[i]['start'],
                'gap': time_gap,
                'reason': 'Q&A pattern' if '?' in prev_text else 'Pause'
            })

    if speaker_changes[:5]:
        for change in speaker_changes[:5]:
            print(f"  Segment {change['segment']}: {change['reason']} (gap: {change['gap']:.1f}s)")

    return {
        'has_speaker_field': has_speaker_field,
        'conversation_type': conversation_type,
        'dialogue_patterns': dialogue_patterns,
        'speaker_changes': len(speaker_changes)
    }

# Analyze multiple transcripts
print("SPEAKER IDENTIFICATION ANALYSIS")
print("=" * 60)

transcript_files = [
    '/Users/yourox/AI-Workspace/data/transcripts/_2zP6NNHXp0_full.json',
    '/Users/yourox/AI-Workspace/data/transcripts/fDwG02tbaHE_full.json',
    '/Users/yourox/AI-Workspace/data/transcripts/oVjNM18jtgQ_full.json'
]

results = []
for file in transcript_files[:3]:
    try:
        result = analyze_speaker_patterns(file)
        results.append(result)
    except Exception as e:
        print(f"Error analyzing {file}: {e}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("-" * 60)

# Summary
has_speaker_data = sum(1 for r in results if r['has_speaker_field'])
interview_count = sum(1 for r in results if r['conversation_type'] == 'interview')

print(f"Files with speaker metadata: {has_speaker_data}/{len(results)}")
print(f"Detected interviews/podcasts: {interview_count}/{len(results)}")
print(f"Average speaker changes detected: {sum(r['speaker_changes'] for r in results)/len(results):.1f}")

print("\nRECOMMENDATIONS:")
if has_speaker_data == 0:
    print("❌ No native speaker metadata found in transcripts")
    print("✓ Can implement heuristic-based speaker detection:")
    print("  1. Use Q&A patterns to identify interviewer vs guest")
    print("  2. Analyze pause patterns for turn-taking")
    print("  3. Track pronoun usage changes (I/you/we)")
    print("  4. Identify recurring question patterns for interviewer")
else:
    print("✓ Speaker metadata available - can use directly")
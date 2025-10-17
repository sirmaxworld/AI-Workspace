#!/usr/bin/env python3
"""
Analyze transcript structure and its impact on BI extraction
"""
import json
import re
from pathlib import Path

# Load a sample transcript
with open('/Users/yourox/AI-Workspace/data/transcripts/_2zP6NNHXp0_full.json', 'r') as f:
    data = json.load(f)

segments = data['transcript']['segments']

print("TRANSCRIPT STRUCTURE ANALYSIS")
print("=" * 60)

# 1. Analyze segment characteristics
segment_lengths = [len(seg['text']) for seg in segments]
print(f"\n1. SEGMENT CHARACTERISTICS:")
print(f"   Total segments: {len(segments)}")
print(f"   Avg chars per segment: {sum(segment_lengths)/len(segment_lengths):.1f}")
print(f"   Min chars: {min(segment_lengths)}")
print(f"   Max chars: {max(segment_lengths)}")

# 2. Show how segments are cut
print(f"\n2. SEGMENT CUTTING EXAMPLES:")
for i in range(10, 15):
    print(f"   Seg {i}: '{segments[i]['text']}'")

# 3. Analyze sentence completeness
incomplete_sentences = 0
for seg in segments:
    text = seg['text']
    # Check if segment ends mid-sentence (no punctuation at end)
    if not text.rstrip().endswith(('.', '!', '?', '"', "'")):
        incomplete_sentences += 1

print(f"\n3. SENTENCE ANALYSIS:")
print(f"   Segments ending mid-sentence: {incomplete_sentences} ({incomplete_sentences/len(segments)*100:.1f}%)")

# 4. Create joined version for comparison
full_text = ' '.join([seg['text'] for seg in segments])
print(f"\n4. FULL TEXT ANALYSIS:")
print(f"   Total characters: {len(full_text)}")
print(f"   Total words: {len(full_text.split())}")

# 5. Example of paragraph grouping
print(f"\n5. INTELLIGENT PARAGRAPH GROUPING:")
print("   Grouping by natural breaks (pauses > 2 seconds)...")

paragraphs = []
current_paragraph = []
last_end_time = 0

for seg in segments[:50]:  # First 50 segments as example
    # If there's a gap > 2 seconds, start new paragraph
    if seg['start'] - last_end_time > 2.0 and current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
        current_paragraph = []

    current_paragraph.append(seg['text'])
    last_end_time = seg['start'] + seg['duration']

if current_paragraph:
    paragraphs.append(' '.join(current_paragraph))

print(f"   Created {len(paragraphs)} paragraphs from 50 segments")
print("\n   First paragraph example:")
print(f"   '{paragraphs[0][:200]}...'")

# 6. Impact on BI extraction
print(f"\n6. IMPACT ON BUSINESS INTELLIGENCE EXTRACTION:")
print("   CURRENT ISSUES:")
print("   - Fragmented context: AI might miss connections across segments")
print("   - Incomplete thoughts: 70%+ segments end mid-sentence")
print("   - Search problems: Keywords split across segments")
print("   - Poor readability: Choppy, unnatural flow")

print("\n   RECOMMENDED IMPROVEMENTS:")
print("   1. Group segments into semantic paragraphs (by pauses/topics)")
print("   2. Store both: original segments (for timestamps) + grouped text (for BI)")
print("   3. Create sentence-aware grouping (complete thoughts)")
print("   4. Add punctuation restoration for better NLP processing")
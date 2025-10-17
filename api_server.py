#!/usr/bin/env python3
"""
Business Intelligence API Server
Serves business insights data to the BI-HUB frontend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import glob
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
DATA_DIR = Path("data/business_insights")
TRANSCRIPTS_DIR = Path("data/transcripts")
CACHE = {}  # Simple in-memory cache

def load_all_insights():
    """Load all business insights from JSON files"""
    if "all_data" in CACHE:
        return CACHE["all_data"]

    all_data = defaultdict(list)
    meta_info = []

    # Load all JSON files
    json_files = glob.glob(str(DATA_DIR / "*.json"))

    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

                # Aggregate data by category
                for key, value in data.items():
                    if key == "meta":
                        meta_info.append(value)
                    elif key == "market_intelligence":
                        # Handle nested structure
                        if "target_markets" in value:
                            all_data["target_markets"].extend(value["target_markets"])
                        if "problems_validated" in value:
                            all_data["problems_validated"].extend(value["problems_validated"])
                    elif isinstance(value, list):
                        all_data[key].extend(value)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    # Add metadata
    all_data["meta"] = meta_info

    # Cache the result
    CACHE["all_data"] = dict(all_data)
    return dict(all_data)

def filter_data(items: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """Apply filters to a list of items"""
    if not filters:
        return items

    filtered = items

    for key, value in filters.items():
        if value and value != "all":
            filtered = [item for item in filtered if item.get(key) == value]

    return filtered

def search_items(items: List[Dict], query: str, search_fields: List[str]) -> List[Dict]:
    """Search items based on query and specified fields"""
    if not query:
        return items

    query_lower = query.lower()
    results = []

    for item in items:
        for field in search_fields:
            if field in item:
                value = str(item[field])
                if query_lower in value.lower():
                    results.append(item)
                    break

    return results

def detect_speaker_turns(segments: List[Dict]) -> List[Dict]:
    """
    Detect speaker turns using heuristic analysis of patterns, pauses, and dialogue markers.

    Since we don't have native speaker metadata, we use:
    - Question/Answer patterns
    - Significant pauses
    - Pronoun usage changes
    - Sentence structure patterns
    """
    if not segments:
        return []

    speaker_turns = []
    current_turn = []
    current_speaker = "Speaker 1"
    last_speaker = "Speaker 1"
    turn_start = segments[0]['start'] if segments else 0

    # Track patterns for speaker identification
    speaker_patterns = {
        "Speaker 1": {"questions": 0, "statements": 0, "avg_length": 0},
        "Speaker 2": {"questions": 0, "statements": 0, "avg_length": 0}
    }

    for i, seg in enumerate(segments):
        text = seg['text'].strip()

        # Calculate features for speaker change detection
        is_question = '?' in text
        starts_with_well = text.lower().startswith(('well', 'so', 'yeah', 'yes', 'no', 'right'))

        # Time gap from previous segment
        time_gap = 0
        if i > 0:
            prev_end = segments[i-1]['start'] + segments[i-1]['duration']
            time_gap = seg['start'] - prev_end

        # Heuristics for speaker change
        should_change_speaker = False

        if i > 0:
            prev_text = segments[i-1]['text'].strip()
            prev_is_question = '?' in prev_text

            # Strong indicators of speaker change
            if prev_is_question and not is_question and time_gap > 0.3:
                # Question followed by answer with pause
                should_change_speaker = True
            elif time_gap > 2.0:
                # Long pause usually indicates speaker change
                should_change_speaker = True
            elif starts_with_well and time_gap > 0.5:
                # Response markers with pause
                should_change_speaker = True
            elif len(current_turn) > 10 and time_gap > 1.0:
                # Long turn followed by pause
                should_change_speaker = True

        # Handle speaker change
        if should_change_speaker and current_turn:
            # Save current turn
            turn_text = ' '.join([s['text'] for s in current_turn])

            # Update speaker patterns
            questions_in_turn = sum(1 for s in current_turn if '?' in s['text'])
            speaker_patterns[current_speaker]["questions"] += questions_in_turn
            speaker_patterns[current_speaker]["statements"] += len(current_turn) - questions_in_turn

            speaker_turns.append({
                'speaker': current_speaker,
                'text': turn_text,
                'start': turn_start,
                'end': current_turn[-1]['start'] + current_turn[-1]['duration'],
                'segment_count': len(current_turn),
                'segments': current_turn  # Keep original segments for reference
            })

            # Switch speakers
            current_speaker = "Speaker 2" if current_speaker == "Speaker 1" else "Speaker 1"
            current_turn = [seg]
            turn_start = seg['start']
        else:
            current_turn.append(seg)

    # Add final turn
    if current_turn:
        turn_text = ' '.join([s['text'] for s in current_turn])
        speaker_turns.append({
            'speaker': current_speaker,
            'text': turn_text,
            'start': turn_start,
            'end': current_turn[-1]['start'] + current_turn[-1]['duration'],
            'segment_count': len(current_turn),
            'segments': current_turn
        })

    # Post-processing: Try to identify interviewer vs guest
    if speaker_turns:
        # Count questions per speaker
        speaker1_questions = sum(1 for turn in speaker_turns if turn['speaker'] == 'Speaker 1' and '?' in turn['text'])
        speaker2_questions = sum(1 for turn in speaker_turns if turn['speaker'] == 'Speaker 2' and '?' in turn['text'])

        # Rename speakers based on role
        if speaker1_questions > speaker2_questions * 1.5:
            # Speaker 1 asks more questions, likely the interviewer
            for turn in speaker_turns:
                if turn['speaker'] == 'Speaker 1':
                    turn['speaker'] = 'Interviewer'
                else:
                    turn['speaker'] = 'Guest'
        elif speaker2_questions > speaker1_questions * 1.5:
            # Speaker 2 asks more questions
            for turn in speaker_turns:
                if turn['speaker'] == 'Speaker 2':
                    turn['speaker'] = 'Interviewer'
                else:
                    turn['speaker'] = 'Guest'
        # Otherwise keep as Speaker 1/2

    return speaker_turns

def group_segments_into_paragraphs(segments: List[Dict], max_pause: float = 1.5, min_segments: int = 3) -> List[Dict]:
    """
    Group transcript segments into semantic paragraphs based on pauses and sentence boundaries.

    Args:
        segments: List of transcript segments with text, start, and duration
        max_pause: Maximum pause (seconds) before starting new paragraph
        min_segments: Minimum segments per paragraph (to avoid too many tiny paragraphs)

    Returns:
        List of paragraph dictionaries with combined text and timing info
    """
    if not segments:
        return []

    paragraphs = []
    current_para = []
    current_start = segments[0]['start'] if segments else 0
    last_end_time = 0

    for i, seg in enumerate(segments):
        segment_start = seg['start']
        segment_end = seg['start'] + seg['duration']

        # Check for natural break (pause or sentence end)
        pause_duration = segment_start - last_end_time if last_end_time > 0 else 0
        is_sentence_end = current_para and current_para[-1].rstrip().endswith(('.', '!', '?'))

        # Start new paragraph if:
        # 1. Significant pause detected AND we have enough segments
        # 2. Natural sentence ending with moderate pause
        should_break = (
            (pause_duration > max_pause and len(current_para) >= min_segments) or
            (pause_duration > 0.8 and is_sentence_end and len(current_para) >= min_segments)
        )

        if should_break and current_para:
            # Save current paragraph
            para_text = ' '.join(current_para)
            # Clean up spacing issues
            para_text = ' '.join(para_text.split())

            paragraphs.append({
                'text': para_text,
                'start': current_start,
                'end': last_end_time,
                'segment_count': len(current_para)
            })

            # Start new paragraph
            current_para = [seg['text']]
            current_start = segment_start
        else:
            current_para.append(seg['text'])

        last_end_time = segment_end

    # Add final paragraph
    if current_para:
        para_text = ' '.join(current_para)
        para_text = ' '.join(para_text.split())
        paragraphs.append({
            'text': para_text,
            'start': current_start,
            'end': last_end_time,
            'segment_count': len(current_para)
        })

    return paragraphs

# ==================== API ENDPOINTS ====================

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/overview')
def get_overview():
    """Get overview statistics for dashboard"""
    data = load_all_insights()

    # Calculate statistics
    stats = {
        "products": len(data.get("products_tools", [])),
        "ideas": len(data.get("startup_ideas", [])),
        "trends": len(data.get("trends_signals", [])),
        "markets": len(data.get("target_markets", [])),
        "problems": len(data.get("problems_solutions", [])),
        "tactics": len(data.get("growth_tactics", [])),
        "workflows": len(data.get("ai_workflows", [])),
        "strategies": len(data.get("business_strategies", []))
    }

    return jsonify(stats)

@app.route('/api/products')
def get_products():
    """Get products and tools with optional filtering"""
    data = load_all_insights()
    products = data.get("products_tools", [])

    # Apply filters
    category = request.args.get('category')
    sentiment = request.args.get('sentiment')
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    # Filter by category and sentiment
    filters = {}
    if category and category != "all":
        filters["category"] = category
    if sentiment and sentiment != "all":
        filters["sentiment"] = sentiment

    products = filter_data(products, filters)

    # Search
    if query:
        products = search_items(products, query, ["name", "use_case", "metrics"])

    # Limit results
    products = products[:limit]

    return jsonify(products)

@app.route('/api/startup-ideas')
def get_startup_ideas():
    """Get startup ideas"""
    data = load_all_insights()
    ideas = data.get("startup_ideas", [])

    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    if query:
        ideas = search_items(ideas, query, ["idea", "target_market", "problem_solved"])

    return jsonify(ideas[:limit])

@app.route('/api/problems')
def get_problems():
    """Get problems and solutions"""
    data = load_all_insights()
    problems = data.get("problems_solutions", [])

    # Apply filters
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    filters = {}
    if category and category != "all":
        filters["category"] = category
    if difficulty and difficulty != "all":
        filters["difficulty"] = difficulty

    problems = filter_data(problems, filters)

    if query:
        problems = search_items(problems, query, ["problem", "solution"])

    return jsonify(problems[:limit])

@app.route('/api/growth-tactics')
def get_growth_tactics():
    """Get growth tactics"""
    data = load_all_insights()
    tactics = data.get("growth_tactics", [])

    channel = request.args.get('channel')
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    if channel and channel != "all":
        tactics = filter_data(tactics, {"channel": channel})

    if query:
        tactics = search_items(tactics, query, ["tactic", "results_expected"])

    return jsonify(tactics[:limit])

@app.route('/api/ai-workflows')
def get_ai_workflows():
    """Get AI workflows"""
    data = load_all_insights()
    workflows = data.get("ai_workflows", [])

    automation = request.args.get('automation_level')
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    if automation and automation != "all":
        workflows = filter_data(workflows, {"automation_level": automation})

    if query:
        workflows = search_items(workflows, query, ["workflow_name", "use_case"])

    return jsonify(workflows[:limit])

@app.route('/api/target-markets')
def get_target_markets():
    """Get target markets"""
    data = load_all_insights()
    markets = data.get("target_markets", [])

    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    if query:
        markets = search_items(markets, query, ["market_description", "demographics", "pain_points"])

    return jsonify(markets[:limit])

@app.route('/api/trends')
def get_trends():
    """Get trends and signals"""
    data = load_all_insights()
    trends = data.get("trends_signals", [])

    category = request.args.get('category')
    stage = request.args.get('stage')
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    filters = {}
    if category and category != "all":
        filters["category"] = category
    if stage and stage != "all":
        filters["stage"] = stage

    trends = filter_data(trends, filters)

    if query:
        trends = search_items(trends, query, ["trend", "opportunity"])

    return jsonify(trends[:limit])

@app.route('/api/business-strategies')
def get_business_strategies():
    """Get business strategies"""
    data = load_all_insights()
    strategies = data.get("business_strategies", [])

    strategy_type = request.args.get('strategy_type')
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    if strategy_type and strategy_type != "all":
        strategies = filter_data(strategies, {"strategy_type": strategy_type})

    if query:
        strategies = search_items(strategies, query, ["strategy", "implementation", "case_study"])

    return jsonify(strategies[:limit])

@app.route('/api/mistakes')
def get_mistakes():
    """Get mistakes to avoid"""
    data = load_all_insights()
    mistakes = data.get("mistakes_to_avoid", [])

    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    if query:
        mistakes = search_items(mistakes, query, ["mistake", "prevention", "example"])

    return jsonify(mistakes[:limit])

@app.route('/api/quotes')
def get_quotes():
    """Get actionable quotes"""
    data = load_all_insights()
    quotes = data.get("actionable_quotes", [])

    category = request.args.get('category')
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    if category and category != "all":
        quotes = filter_data(quotes, {"category": category})

    if query:
        quotes = search_items(quotes, query, ["quote", "context", "actionability"])

    return jsonify(quotes[:limit])

@app.route('/api/metrics')
def get_metrics():
    """Get metrics and KPIs"""
    data = load_all_insights()
    metrics = data.get("metrics_kpis", [])

    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    if query:
        metrics = search_items(metrics, query, ["metric", "benchmark", "optimization_tip"])

    return jsonify(metrics[:limit])

@app.route('/api/statistics')
def get_statistics():
    """Get key statistics"""
    data = load_all_insights()
    stats = data.get("key_statistics", [])

    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    if query:
        stats = search_items(stats, query, ["statistic", "context"])

    return jsonify(stats[:limit])

@app.route('/api/videos')
def get_videos():
    """Get list of all videos with their metadata and insights"""
    videos = []

    # Get all insight files
    insight_files = glob.glob(str(DATA_DIR / "*.json"))

    for file_path in insight_files:
        video_id = Path(file_path).stem.replace('_insights', '')

        try:
            # Load insights data
            with open(file_path, 'r') as f:
                insights = json.load(f)

            # Check if transcript exists
            transcript_path = TRANSCRIPTS_DIR / f"{video_id}_full.json"
            has_transcript = transcript_path.exists()

            # Get video metadata from insights
            meta = insights.get('meta', {})

            video_info = {
                "video_id": video_id,
                "title": meta.get('title', 'Unknown Title'),
                "has_transcript": has_transcript,
                "extracted_at": meta.get('extracted_at', ''),
                "transcript_length": meta.get('transcript_length', 0),
                "insights_summary": {
                    "products": len(insights.get('products_tools', [])),
                    "ideas": len(insights.get('startup_ideas', [])),
                    "problems": len(insights.get('problems_solutions', [])),
                    "trends": len(insights.get('trends_signals', [])),
                    "tactics": len(insights.get('growth_tactics', [])),
                    "workflows": len(insights.get('ai_workflows', []))
                }
            }
            videos.append(video_info)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Sort by title
    videos.sort(key=lambda x: x.get('title', ''))

    return jsonify(videos)

@app.route('/api/videos/<video_id>')
def get_video_detail(video_id):
    """Get detailed information for a specific video including transcript and all insights"""

    # Load insights
    insights_path = DATA_DIR / f"{video_id}_insights.json"
    if not insights_path.exists():
        return jsonify({"error": "Video insights not found"}), 404

    with open(insights_path, 'r') as f:
        insights = json.load(f)

    # Load transcript if available
    transcript_path = TRANSCRIPTS_DIR / f"{video_id}_full.json"
    transcript_data = None

    if transcript_path.exists():
        with open(transcript_path, 'r') as f:
            transcript_json = json.load(f)

            # Combine transcript segments into readable text
            segments = transcript_json.get('transcript', {}).get('segments', [])
            full_text = ' '.join([seg['text'] for seg in segments])

            # Create intelligently grouped paragraphs
            paragraphs = group_segments_into_paragraphs(segments)

            # Detect speaker turns
            speaker_turns = detect_speaker_turns(segments)

            # Calculate speaker statistics
            speaker_stats = {}
            for turn in speaker_turns:
                speaker = turn['speaker']
                if speaker not in speaker_stats:
                    speaker_stats[speaker] = {
                        'total_time': 0,
                        'turn_count': 0,
                        'avg_turn_length': 0,
                        'total_words': 0
                    }

                duration = turn['end'] - turn['start']
                words = len(turn['text'].split())

                speaker_stats[speaker]['total_time'] += duration
                speaker_stats[speaker]['turn_count'] += 1
                speaker_stats[speaker]['total_words'] += words

            # Calculate averages
            for speaker, stats in speaker_stats.items():
                if stats['turn_count'] > 0:
                    stats['avg_turn_length'] = stats['total_time'] / stats['turn_count']

            transcript_data = {
                "full_text": full_text,
                "segments": segments,  # All segments
                "paragraphs": paragraphs,  # Grouped paragraphs
                "speaker_turns": speaker_turns,  # Speaker-based grouping
                "speaker_stats": speaker_stats,  # Speaker statistics
                "language": transcript_json.get('transcript', {}).get('language', 'en'),
                "duration": segments[-1]['start'] + segments[-1]['duration'] if segments else 0
            }

    # Prepare response
    response = {
        "video_id": video_id,
        "title": insights.get('meta', {}).get('title', 'Unknown Title'),
        "transcript": transcript_data,
        "insights": insights,
        "youtube_url": f"https://www.youtube.com/watch?v={video_id}"
    }

    return jsonify(response)

@app.route('/api/videos/<video_id>/transcript')
def get_video_transcript(video_id):
    """Get just the transcript for a specific video"""

    transcript_path = TRANSCRIPTS_DIR / f"{video_id}_full.json"

    if not transcript_path.exists():
        return jsonify({"error": "Transcript not found"}), 404

    with open(transcript_path, 'r') as f:
        transcript_json = json.load(f)

    segments = transcript_json.get('transcript', {}).get('segments', [])
    full_text = ' '.join([seg['text'] for seg in segments])

    return jsonify({
        "video_id": video_id,
        "title": transcript_json.get('title', ''),
        "full_text": full_text,
        "segments": segments,
        "language": transcript_json.get('transcript', {}).get('language', 'en')
    })

@app.route('/api/search')
def search():
    """Global search across all data"""
    query = request.args.get('q', '')
    data_type = request.args.get('type', 'all')
    limit = int(request.args.get('limit', 20))

    if not query:
        return jsonify({"error": "Query parameter required"}), 400

    data = load_all_insights()
    results = []

    # Define search configurations for each type
    search_config = {
        "products": ("products_tools", ["name", "use_case", "metrics"]),
        "ideas": ("startup_ideas", ["idea", "target_market", "problem_solved"]),
        "problems": ("problems_solutions", ["problem", "solution"]),
        "tactics": ("growth_tactics", ["tactic", "results_expected"]),
        "workflows": ("ai_workflows", ["workflow_name", "use_case"]),
        "markets": ("target_markets", ["market_description", "demographics"]),
        "trends": ("trends_signals", ["trend", "opportunity"]),
        "strategies": ("business_strategies", ["strategy", "implementation"])
    }

    # Search in specified type or all types
    if data_type != "all" and data_type in search_config:
        key, fields = search_config[data_type]
        items = data.get(key, [])
        found = search_items(items, query, fields)
        for item in found[:limit]:
            results.append({
                "type": data_type,
                "data": item
            })
    else:
        # Search all types
        for type_name, (key, fields) in search_config.items():
            items = data.get(key, [])
            found = search_items(items, query, fields)
            for item in found[:max(3, limit // len(search_config))]:
                results.append({
                    "type": type_name,
                    "data": item
                })

    return jsonify(results[:limit])

@app.route('/api/charts/products-by-category')
def get_products_by_category():
    """Get product distribution by category for charts"""
    data = load_all_insights()
    products = data.get("products_tools", [])

    category_counts = defaultdict(int)
    for product in products:
        category = product.get("category", "unknown")
        category_counts[category] += 1

    # Format for recharts
    chart_data = [
        {"category": cat, "count": count}
        for cat, count in category_counts.items()
    ]

    return jsonify(sorted(chart_data, key=lambda x: x["count"], reverse=True)[:10])

@app.route('/api/charts/trends-by-stage')
def get_trends_by_stage():
    """Get trends distribution by stage"""
    data = load_all_insights()
    trends = data.get("trends_signals", [])

    stage_counts = defaultdict(int)
    for trend in trends:
        stage = trend.get("stage", "unknown")
        stage_counts[stage] += 1

    chart_data = [
        {"stage": stage, "count": count}
        for stage, count in stage_counts.items()
    ]

    return jsonify(chart_data)

@app.route('/api/charts/growth-tactics-by-channel')
def get_growth_tactics_by_channel():
    """Get growth tactics distribution by channel"""
    data = load_all_insights()
    tactics = data.get("growth_tactics", [])

    channel_counts = defaultdict(int)
    for tactic in tactics:
        channel = tactic.get("channel", "unknown")
        channel_counts[channel] += 1

    chart_data = [
        {"channel": chan, "value": count}
        for chan, count in channel_counts.items()
    ]

    return jsonify(chart_data)

# ==================== YC COMPANIES ENDPOINTS ====================

@app.route('/api/yc-companies')
def get_yc_companies():
    """Get Y Combinator companies with filtering and search"""
    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            return jsonify({"error": "Supabase not configured"}), 500

        supabase = create_client(supabase_url, supabase_key)

        # Get query parameters
        query = request.args.get('q', '')
        batch = request.args.get('batch')
        industry = request.args.get('industry')
        status = request.args.get('status')
        stage = request.args.get('stage')
        is_hiring = request.args.get('is_hiring')
        top_company = request.args.get('top_company')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        # Build query
        query_builder = supabase.table('yc_companies').select('*')

        # Apply filters
        if batch:
            query_builder = query_builder.eq('batch', batch)
        if industry:
            query_builder = query_builder.eq('industry', industry)
        if status:
            query_builder = query_builder.eq('status', status)
        if stage:
            query_builder = query_builder.eq('stage', stage)
        if is_hiring == 'true':
            query_builder = query_builder.eq('is_hiring', True)
        if top_company == 'true':
            query_builder = query_builder.eq('top_company', True)

        # Text search (if provided)
        if query:
            query_builder = query_builder.or_(f"name.ilike.%{query}%,one_liner.ilike.%{query}%")

        # Apply pagination
        query_builder = query_builder.range(offset, offset + limit - 1)

        # Execute query
        response = query_builder.execute()

        return jsonify({
            "data": response.data,
            "count": len(response.data),
            "limit": limit,
            "offset": offset
        })

    except ImportError:
        return jsonify({"error": "supabase-py not installed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/yc-companies/<slug>')
def get_yc_company_detail(slug):
    """Get detailed information for a specific YC company by slug"""
    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            return jsonify({"error": "Supabase not configured"}), 500

        supabase = create_client(supabase_url, supabase_key)

        # Query by slug
        response = supabase.table('yc_companies').select('*').eq('slug', slug).execute()

        if not response.data:
            return jsonify({"error": "Company not found"}), 404

        return jsonify(response.data[0])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/yc-companies/stats/overview')
def get_yc_companies_stats():
    """Get overview statistics for YC companies"""
    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            return jsonify({"error": "Supabase not configured"}), 500

        supabase = create_client(supabase_url, supabase_key)

        # Get all companies
        response = supabase.table('yc_companies').select('batch,status,industry,is_hiring,top_company,nonprofit,team_size').execute()

        companies = response.data

        # Calculate statistics
        stats = {
            "total": len(companies),
            "hiring": sum(1 for c in companies if c.get('is_hiring')),
            "top_companies": sum(1 for c in companies if c.get('top_company')),
            "nonprofit": sum(1 for c in companies if c.get('nonprofit')),
            "by_status": {},
            "by_industry": {},
            "by_batch": {},
            "avg_team_size": 0
        }

        # Status breakdown
        for company in companies:
            status = company.get('status', 'unknown')
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        # Industry breakdown (top 10)
        industry_counts = {}
        for company in companies:
            industry = company.get('industry', 'unknown')
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        stats["by_industry"] = dict(sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:10])

        # Batch breakdown (recent 10)
        batch_counts = {}
        for company in companies:
            batch = company.get('batch', 'unknown')
            batch_counts[batch] = batch_counts.get(batch, 0) + 1

        stats["by_batch"] = dict(sorted(batch_counts.items(), reverse=True)[:10])

        # Average team size
        team_sizes = [c.get('team_size', 0) for c in companies if c.get('team_size')]
        if team_sizes:
            stats["avg_team_size"] = round(sum(team_sizes) / len(team_sizes), 1)

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/yc-companies/batches')
def get_yc_batches():
    """Get list of all YC batches"""
    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            return jsonify({"error": "Supabase not configured"}), 500

        supabase = create_client(supabase_url, supabase_key)

        # Get distinct batches with company count
        response = supabase.table('yc_companies').select('batch').execute()

        batch_counts = {}
        for company in response.data:
            batch = company.get('batch', 'unknown')
            batch_counts[batch] = batch_counts.get(batch, 0) + 1

        batches = [
            {"batch": batch, "count": count}
            for batch, count in batch_counts.items()
        ]

        # Sort by batch (most recent first)
        batches.sort(key=lambda x: x['batch'], reverse=True)

        return jsonify(batches)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/yc-companies/industries')
def get_yc_industries():
    """Get list of all YC industries"""
    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            return jsonify({"error": "Supabase not configured"}), 500

        supabase = create_client(supabase_url, supabase_key)

        # Get distinct industries with company count
        response = supabase.table('yc_companies').select('industry').execute()

        industry_counts = {}
        for company in response.data:
            industry = company.get('industry', 'unknown')
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        industries = [
            {"industry": industry, "count": count}
            for industry, count in industry_counts.items()
        ]

        # Sort by count (most companies first)
        industries.sort(key=lambda x: x['count'], reverse=True)

        return jsonify(industries)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/yc-companies/search/semantic')
def semantic_search_yc_companies():
    """Semantic search for YC companies using embeddings"""
    try:
        from supabase import create_client
        from openai import OpenAI

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not supabase_url or not supabase_key:
            return jsonify({"error": "Supabase not configured"}), 500

        if not openai_api_key:
            return jsonify({"error": "OpenAI API key not configured"}), 500

        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "Query parameter required"}), 400

        limit = int(request.args.get('limit', 10))
        threshold = float(request.args.get('threshold', 0.5))

        # Generate embedding for query
        openai_client = OpenAI(api_key=openai_api_key)
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding

        # Search using the search function
        supabase = create_client(supabase_url, supabase_key)
        result = supabase.rpc(
            'search_yc_companies',
            {
                'query_embedding': query_embedding,
                'match_threshold': threshold,
                'match_count': limit
            }
        ).execute()

        return jsonify({
            "query": query,
            "results": result.data,
            "count": len(result.data)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Business Intelligence API Server...")
    print("Loading data from:", DATA_DIR)

    # Preload data
    data = load_all_insights()
    print(f"Loaded data categories: {list(data.keys())}")

    # Run server
    app.run(host="0.0.0.0", port=5001, debug=True)
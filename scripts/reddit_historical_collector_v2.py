#!/usr/bin/env python3
"""
Reddit Historical Sentiment Analyzer v2
Uses Reddit JSON API (no authentication required for public data)
Collects weekly snapshots for past 52 weeks with 10 core qualifiers
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from typing import Dict, List, Any
import time

# Tier 1 Subreddits (52 weeks history)
TIER_1_SUBREDDITS = {
    "Entrepreneur": {
        "name": "r/Entrepreneur",
        "category": "ENTREPRENEURSHIP",
        "priority": "critical"
    },
    "ChatGPT": {
        "name": "r/ChatGPT",
        "category": "AI_NEWS",
        "priority": "critical"
    },
    "ArtificialIntelligence": {
        "name": "r/ArtificialIntelligence",
        "category": "AI_NEWS",
        "priority": "critical"
    },
    "MachineLearning": {
        "name": "r/MachineLearning",
        "category": "AI_NEWS",
        "priority": "critical"
    },
    "Meditation": {
        "name": "r/Meditation",
        "category": "MEDITATION",
        "priority": "critical"
    },
    "marketing": {
        "name": "r/marketing",
        "category": "MARKETING",
        "priority": "critical"
    },
    "smallbusiness": {
        "name": "r/smallbusiness",
        "category": "SME",
        "priority": "critical"
    },
    "lawofattraction": {
        "name": "r/lawofattraction",
        "category": "MANIFESTATION",
        "priority": "critical"
    },
    "startups": {
        "name": "r/startups",
        "category": "ENTREPRENEURSHIP",
        "priority": "critical"
    },
    "business": {
        "name": "r/business",
        "category": "BUSINESS",
        "priority": "critical"
    }
}


class RedditHistoricalAnalyzer:
    """Collect and analyze Reddit data for sentiment and trends"""

    def __init__(self):
        """Initialize analyzer"""
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.data_dir = "/Users/yourox/AI-Workspace/data/reddit_snapshots"
        os.makedirs(self.data_dir, exist_ok=True)

        # Reddit JSON API doesn't need authentication for public data
        self.headers = {
            'User-Agent': 'python:reddit-sentiment-analyzer:v2.0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_week_date_range(self, weeks_ago: int = 0) -> tuple:
        """Get start and end dates for a week"""
        today = datetime.now()
        week_start = today - timedelta(weeks=weeks_ago, days=today.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start, week_end

    def get_week_identifier(self, date: datetime) -> str:
        """Get ISO week identifier (e.g., '2024-W42')"""
        return date.strftime("%Y-W%U")

    def fetch_week_posts(self, subreddit_name: str, week_start: datetime, week_end: datetime, limit: int = 100) -> List[Dict]:
        """Fetch top posts from a specific week using Reddit JSON API"""
        print(f"   📅 Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")

        try:
            posts = []

            # Convert to timestamps
            start_timestamp = int(week_start.timestamp())
            end_timestamp = int(week_end.timestamp())

            # Fetch posts from Reddit JSON API
            # We'll fetch "top" posts and filter by date
            url = f"https://www.reddit.com/r/{subreddit_name}/top/.json"
            params = {
                't': 'year',  # top of the year
                'limit': 100
            }

            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            if 'data' not in data or 'children' not in data['data']:
                print(f"   ⚠️  Unexpected response format")
                return []

            # Filter posts by week
            for item in data['data']['children']:
                post_data = item['data']
                post_time = int(post_data['created_utc'])

                if start_timestamp <= post_time <= end_timestamp:
                    # Fetch top comments
                    comments = self.fetch_post_comments(subreddit_name, post_data['id'], limit=3)

                    post = {
                        'id': post_data['id'],
                        'title': post_data['title'],
                        'selftext': post_data.get('selftext', ''),
                        'score': post_data['score'],
                        'upvote_ratio': post_data['upvote_ratio'],
                        'num_comments': post_data['num_comments'],
                        'created_utc': post_data['created_utc'],
                        'author': post_data['author'],
                        'url': post_data['url'],
                        'permalink': f"https://reddit.com{post_data['permalink']}",
                        'link_flair_text': post_data.get('link_flair_text', ''),
                        'is_self': post_data['is_self'],
                        'gilded': post_data['gilded'],
                        'comments': comments
                    }
                    posts.append(post)

                    if len(posts) >= limit:
                        break

            # If we didn't get enough posts from "top", try "hot"
            if len(posts) < limit // 2:
                url = f"https://www.reddit.com/r/{subreddit_name}/hot/.json"
                params = {'limit': 100}
                response = self.session.get(url, params=params, timeout=20)
                response.raise_for_status()
                data = response.json()

                for item in data['data']['children']:
                    post_data = item['data']
                    post_time = int(post_data['created_utc'])

                    if start_timestamp <= post_time <= end_timestamp:
                        if post_data['id'] not in [p['id'] for p in posts]:  # Avoid duplicates
                            comments = self.fetch_post_comments(subreddit_name, post_data['id'], limit=3)

                            post = {
                                'id': post_data['id'],
                                'title': post_data['title'],
                                'selftext': post_data.get('selftext', ''),
                                'score': post_data['score'],
                                'upvote_ratio': post_data['upvote_ratio'],
                                'num_comments': post_data['num_comments'],
                                'created_utc': post_data['created_utc'],
                                'author': post_data['author'],
                                'url': post_data['url'],
                                'permalink': f"https://reddit.com{post_data['permalink']}",
                                'link_flair_text': post_data.get('link_flair_text', ''),
                                'is_self': post_data['is_self'],
                                'gilded': post_data['gilded'],
                                'comments': comments
                            }
                            posts.append(post)

                            if len(posts) >= limit:
                                break

            print(f"   ✅ Fetched {len(posts)} posts")
            return posts

        except Exception as e:
            print(f"   ❌ Error fetching posts: {e}")
            return []

    def fetch_post_comments(self, subreddit_name: str, post_id: str, limit: int = 3) -> List[Dict]:
        """Fetch top comments for a post"""
        try:
            url = f"https://www.reddit.com/r/{subreddit_name}/comments/{post_id}/.json"
            params = {'limit': limit, 'sort': 'top'}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if len(data) < 2:
                return []

            comments = []
            comment_listing = data[1]['data']['children']

            for item in comment_listing[:limit]:
                if item['kind'] == 't1':  # Comment
                    comment_data = item['data']
                    comments.append({
                        'body': comment_data.get('body', ''),
                        'score': comment_data.get('score', 0),
                        'author': comment_data.get('author', '[deleted]')
                    })

            time.sleep(0.5)  # Rate limiting
            return comments

        except Exception as e:
            return []

    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        if not text or len(text.strip()) == 0:
            return {'score': 0, 'label': 'neutral', 'confidence': 0}

        scores = self.sentiment_analyzer.polarity_scores(text)
        compound = scores['compound']

        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'score': compound,
            'label': label,
            'confidence': max(scores['pos'], scores['neg'], scores['neu'])
        }

    def extract_topics(self, posts: List[Dict]) -> Dict:
        """Extract trending topics from posts"""
        word_freq = Counter()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                     'i', 'you', 'we', 'they', 'my', 'your', 'our', 'their', 'this', 'that',
                     'how', 'what', 'when', 'where', 'why', 'do', 'does', 'did', 'can', 'should'}

        for post in posts:
            title = post.get('title', '')
            words = re.findall(r'\b[a-z]{3,}\b', title.lower())
            word_freq.update([w for w in words if w not in stop_words])

        top_words = word_freq.most_common(20)

        topics = []
        for word, count in top_words[:10]:
            topics.append({
                'topic': word,
                'mentions': count,
                'growth': None
            })

        return {'top_topics': topics}

    def extract_pain_points(self, posts: List[Dict]) -> List[Dict]:
        """Extract pain points and challenges from posts"""
        pain_keywords = ['problem', 'issue', 'struggle', 'difficult', 'challenge', 'frustrat',
                        'stuck', 'fail', 'help', 'advice', 'how to', 'can\'t', 'unable']

        pain_points = []
        for post in posts:
            title = post.get('title', '').lower()
            text = post.get('selftext', '').lower()
            combined = title + ' ' + text

            if any(keyword in combined for keyword in pain_keywords):
                sentiment = self.analyze_sentiment(combined)

                pain_points.append({
                    'text': post.get('title', ''),
                    'score': post.get('score', 0),
                    'severity': abs(sentiment['score']) if sentiment['label'] == 'negative' else 0.5,
                    'url': post.get('permalink', '')
                })

        pain_points.sort(key=lambda x: x['score'] * x['severity'], reverse=True)
        return pain_points[:10]

    def extract_solutions(self, posts: List[Dict]) -> Dict:
        """Extract tools, solutions, and recommendations"""
        tool_pattern = r'\b(?:using|use|used|try|recommend|love|hate|prefer|switch|migrate)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'

        tools_mentioned = Counter()
        for post in posts:
            text = post.get('title', '') + ' ' + post.get('selftext', '')
            for comment in post.get('comments', []):
                text += ' ' + comment.get('body', '')

            matches = re.findall(tool_pattern, text)
            tools_mentioned.update(matches)

        return {
            'top_tools_mentioned': [
                {'tool': tool, 'mentions': count}
                for tool, count in tools_mentioned.most_common(10)
            ]
        }

    def extract_questions(self, posts: List[Dict]) -> List[Dict]:
        """Extract top questions from posts"""
        questions = []

        for post in posts:
            title = post.get('title', '')
            if '?' in title:
                questions.append({
                    'question': title,
                    'upvotes': post.get('score', 0),
                    'answers': post.get('num_comments', 0),
                    'url': post.get('permalink', '')
                })

        questions.sort(key=lambda x: x['upvotes'], reverse=True)
        return questions[:10]

    def analyze_week(self, subreddit_name: str, week_start: datetime, week_end: datetime) -> Dict:
        """Analyze a single week of data"""
        week_id = self.get_week_identifier(week_start)

        print(f"\n📊 Analyzing {subreddit_name} - {week_id}")

        # Fetch posts
        posts = self.fetch_week_posts(subreddit_name, week_start, week_end)

        if len(posts) == 0:
            print(f"   ⚠️  No posts found for this week")
            return None

        # Calculate engagement metrics
        total_upvotes = sum(p.get('score', 0) for p in posts)
        total_comments = sum(p.get('num_comments', 0) for p in posts)
        avg_upvotes = total_upvotes / len(posts) if posts else 0
        avg_comments = total_comments / len(posts) if posts else 0
        gilded_posts = sum(1 for p in posts if p.get('gilded', 0) > 0)

        # Sentiment analysis
        sentiments = []
        for post in posts:
            text = post.get('title', '') + ' ' + post.get('selftext', '')
            sentiment = self.analyze_sentiment(text)
            sentiments.append(sentiment)

        positive = sum(1 for s in sentiments if s['label'] == 'positive')
        negative = sum(1 for s in sentiments if s['label'] == 'negative')
        neutral = sum(1 for s in sentiments if s['label'] == 'neutral')

        avg_sentiment = sum(s['score'] for s in sentiments) / len(sentiments) if sentiments else 0

        # Extract insights
        topics = self.extract_topics(posts)
        pain_points = self.extract_pain_points(posts)
        solutions = self.extract_solutions(posts)
        questions = self.extract_questions(posts)

        # Most engaged posts
        top_posts = sorted(posts, key=lambda x: x.get('score', 0), reverse=True)[:5]

        # Build snapshot
        snapshot = {
            'snapshot_id': f"{subreddit_name.lower()}_{week_id.replace('-', '_')}",
            'subreddit': f"r/{subreddit_name}",
            'week': week_id,
            'date_range': {
                'start': week_start.strftime('%Y-%m-%d'),
                'end': week_end.strftime('%Y-%m-%d')
            },
            'metadata': {
                'posts_analyzed': len(posts),
                'data_quality_score': min(len(posts) / 100, 1.0)
            },

            # Qualifier 1: Engagement
            'engagement': {
                'total_posts': len(posts),
                'total_comments': total_comments,
                'avg_upvotes_per_post': round(avg_upvotes, 1),
                'avg_comments_per_post': round(avg_comments, 1),
                'gilded_posts': gilded_posts
            },

            # Qualifier 2: Sentiment
            'sentiment': {
                'overall_sentiment': {
                    'score': round(avg_sentiment, 3),
                    'label': 'positive' if avg_sentiment > 0.05 else 'negative' if avg_sentiment < -0.05 else 'neutral',
                    'confidence': round(sum(s['confidence'] for s in sentiments) / len(sentiments), 2) if sentiments else 0
                },
                'sentiment_distribution': {
                    'positive': round(positive / len(sentiments), 2) if sentiments else 0,
                    'neutral': round(neutral / len(sentiments), 2) if sentiments else 0,
                    'negative': round(negative / len(sentiments), 2) if sentiments else 0
                }
            },

            # Qualifier 3: Topics
            'trending_topics': topics,

            # Qualifier 4: Pain Points
            'pain_points': {
                'top_pain_points': pain_points
            },

            # Qualifier 5: Solutions
            'solutions': solutions,

            # Qualifier 6: Questions
            'questions': {
                'top_questions': questions
            },

            # Qualifier 7: Top Posts (Influencers)
            'influencers': {
                'most_engaged_posts': [
                    {
                        'title': p.get('title', ''),
                        'author': p.get('author', ''),
                        'upvotes': p.get('score', 0),
                        'comments': p.get('num_comments', 0),
                        'awards': p.get('gilded', 0),
                        'url': p.get('permalink', '')
                    }
                    for p in top_posts
                ]
            }
        }

        return snapshot

    def save_snapshot(self, snapshot: Dict, subreddit_name: str):
        """Save snapshot to JSON file"""
        if not snapshot:
            return

        subreddit_dir = os.path.join(self.data_dir, subreddit_name.lower())
        os.makedirs(subreddit_dir, exist_ok=True)

        filename = f"{snapshot['snapshot_id']}.json"
        filepath = os.path.join(subreddit_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)

        print(f"   💾 Saved: {filepath}")

    def collect_historical_data(self, subreddit_name: str, weeks: int = 52, limit_per_week: int = 100):
        """Collect historical data for a subreddit"""
        print("\n" + "=" * 70)
        print(f"📡 COLLECTING: r/{subreddit_name}")
        print("=" * 70)
        print(f"   Weeks: {weeks}")
        print(f"   Posts per week: {limit_per_week}")

        snapshots_created = 0

        for week_num in range(weeks):
            week_start, week_end = self.get_week_date_range(week_num)

            # Check if snapshot already exists
            week_id = self.get_week_identifier(week_start)
            snapshot_id = f"{subreddit_name.lower()}_{week_id.replace('-', '_')}".replace(' ', '_')
            subreddit_dir = os.path.join(self.data_dir, subreddit_name.lower())
            filepath = os.path.join(subreddit_dir, f"{snapshot_id}.json")

            if os.path.exists(filepath):
                print(f"\n⏭️  Week {week_num + 1}/{weeks}: {week_id} - Already exists, skipping")
                continue

            print(f"\n📅 Week {week_num + 1}/{weeks}: {week_id}")

            # Analyze week
            snapshot = self.analyze_week(subreddit_name, week_start, week_end)

            if snapshot:
                self.save_snapshot(snapshot, subreddit_name)
                snapshots_created += 1

            # Rate limiting - be nice to Reddit (avoid 429)
            time.sleep(5)

        print(f"\n✅ Completed: {snapshots_created} snapshots created for r/{subreddit_name}")
        return snapshots_created


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Reddit Historical Sentiment Analyzer v2')
    parser.add_argument('--subreddit', type=str, help='Specific subreddit to analyze')
    parser.add_argument('--weeks', type=int, default=52, help='Number of weeks to analyze (default: 52)')
    parser.add_argument('--limit', type=int, default=100, help='Posts per week (default: 100)')
    parser.add_argument('--tier1', action='store_true', help='Analyze all Tier 1 subreddits')

    args = parser.parse_args()

    print("=" * 70)
    print("🔍 REDDIT HISTORICAL SENTIMENT ANALYZER V2")
    print("=" * 70)
    print("Using Reddit JSON API (no authentication required)")
    print()

    analyzer = RedditHistoricalAnalyzer()

    if args.tier1:
        # Analyze all Tier 1 subreddits
        print(f"📊 Analyzing {len(TIER_1_SUBREDDITS)} Tier 1 subreddits")
        print(f"   {args.weeks} weeks each = {len(TIER_1_SUBREDDITS) * args.weeks} total snapshots")
        print()

        total_snapshots = 0
        for subreddit_name in TIER_1_SUBREDDITS.keys():
            snapshots = analyzer.collect_historical_data(subreddit_name, args.weeks, args.limit)
            total_snapshots += snapshots

        print("\n" + "=" * 70)
        print("📊 COLLECTION COMPLETE")
        print("=" * 70)
        print(f"   Total snapshots created: {total_snapshots}")
        print(f"   Total subreddits: {len(TIER_1_SUBREDDITS)}")
        print(f"   Data directory: {analyzer.data_dir}")

    elif args.subreddit:
        # Analyze specific subreddit
        analyzer.collect_historical_data(args.subreddit, args.weeks, args.limit)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

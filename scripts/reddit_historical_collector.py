#!/usr/bin/env python3
"""
Reddit Historical Sentiment Analyzer
Collects weekly snapshots for past 52 weeks with 10 core qualifiers
"""

import os
import sys
import json
import praw
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
        """Initialize Reddit API client"""
        self.reddit = None
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.data_dir = "/Users/yourox/AI-Workspace/data/reddit_snapshots"
        os.makedirs(self.data_dir, exist_ok=True)

    def setup_reddit_client(self):
        """Set up Reddit API client with credentials"""
        print("=" * 70)
        print("🔑 REDDIT API SETUP")
        print("=" * 70)
        print()
        print("To use Reddit API, you need to create an app at:")
        print("https://www.reddit.com/prefs/apps")
        print()
        print("1. Click 'create app' or 'create another app'")
        print("2. Choose 'script' type")
        print("3. Set redirect uri to: http://localhost:8080")
        print()

        # Check for environment variables first
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'python:reddit-sentiment-analyzer:v1.0')

        if not client_id or not client_secret:
            print("No Reddit credentials found in environment variables.")
            print("Please enter your Reddit API credentials:")
            print()
            client_id = input("Client ID: ").strip()
            client_secret = input("Client Secret: ").strip()
            user_agent = input("User Agent (press Enter for default): ").strip() or user_agent

            # Offer to save to .env
            save = input("\nSave credentials to .env file? (y/n): ").strip().lower()
            if save == 'y':
                with open('/Users/yourox/AI-Workspace/.env', 'a') as f:
                    f.write(f"\n# Reddit API\n")
                    f.write(f"REDDIT_CLIENT_ID={client_id}\n")
                    f.write(f"REDDIT_CLIENT_SECRET={client_secret}\n")
                    f.write(f"REDDIT_USER_AGENT={user_agent}\n")
                print("✅ Credentials saved to .env")

        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            # Test connection with read-only access
            # For public subreddit data, we don't need user authentication
            test_sub = self.reddit.subreddit('python')
            _ = test_sub.display_name  # Test API access

            print(f"\n✅ Connected to Reddit API")
            print(f"   User Agent: {user_agent}")
            print(f"   Access Mode: Read-only (public data)")
            return True
        except Exception as e:
            print(f"\n❌ Failed to connect to Reddit API: {e}")
            print("Please check your credentials and try again.")
            return False

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
        """Fetch top posts from a specific week"""
        print(f"   📅 Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            # Convert to timestamps
            start_timestamp = int(week_start.timestamp())
            end_timestamp = int(week_end.timestamp())

            # Fetch posts using time-based search
            # Note: Reddit API doesn't support exact time ranges, so we'll filter
            for submission in subreddit.top(time_filter='year', limit=limit * 4):  # Fetch more, filter later
                post_time = submission.created_utc

                if start_timestamp <= post_time <= end_timestamp:
                    # Fetch top 3 comments
                    submission.comments.replace_more(limit=0)
                    top_comments = submission.comments[:3]

                    post_data = {
                        'id': submission.id,
                        'title': submission.title,
                        'selftext': submission.selftext,
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'created_utc': submission.created_utc,
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'url': submission.url,
                        'permalink': f"https://reddit.com{submission.permalink}",
                        'link_flair_text': submission.link_flair_text,
                        'is_self': submission.is_self,
                        'gilded': submission.gilded,
                        'comments': [
                            {
                                'body': comment.body,
                                'score': comment.score,
                                'author': str(comment.author) if comment.author else '[deleted]'
                            }
                            for comment in top_comments
                        ]
                    }
                    posts.append(post_data)

                    if len(posts) >= limit:
                        break

                # Rate limiting
                time.sleep(0.1)

            print(f"   ✅ Fetched {len(posts)} posts")
            return posts

        except Exception as e:
            print(f"   ❌ Error fetching posts: {e}")
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
        # Simple topic extraction using title analysis
        word_freq = Counter()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                     'i', 'you', 'we', 'they', 'my', 'your', 'our', 'their', 'this', 'that',
                     'how', 'what', 'when', 'where', 'why', 'do', 'does', 'did', 'can', 'should'}

        all_text = []
        for post in posts:
            title = post.get('title', '')
            text = post.get('selftext', '')
            all_text.append(title + ' ' + text)

            # Extract words from title
            words = re.findall(r'\b[a-z]{3,}\b', title.lower())
            word_freq.update([w for w in words if w not in stop_words])

        # Get top topics
        top_words = word_freq.most_common(20)

        # Create topic clusters (simple 2-word phrases)
        topics = []
        for word, count in top_words[:10]:
            topics.append({
                'topic': word,
                'mentions': count,
                'growth': None  # Would need historical comparison
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

            # Check if post mentions pain points
            if any(keyword in combined for keyword in pain_keywords):
                sentiment = self.analyze_sentiment(combined)

                pain_points.append({
                    'text': post.get('title', ''),
                    'score': post.get('score', 0),
                    'severity': abs(sentiment['score']) if sentiment['label'] == 'negative' else 0.5,
                    'url': post.get('permalink', '')
                })

        # Sort by score and severity
        pain_points.sort(key=lambda x: x['score'] * x['severity'], reverse=True)
        return pain_points[:10]

    def extract_solutions(self, posts: List[Dict]) -> Dict:
        """Extract tools, solutions, and recommendations"""
        # Common tool/platform patterns
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
            snapshot_id = f"{subreddit_name.lower()}_{week_id.replace('-', '_')}"
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

            # Rate limiting - be nice to Reddit API
            time.sleep(2)

        print(f"\n✅ Completed: {snapshots_created} snapshots created for r/{subreddit_name}")
        return snapshots_created


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Reddit Historical Sentiment Analyzer')
    parser.add_argument('--subreddit', type=str, help='Specific subreddit to analyze')
    parser.add_argument('--weeks', type=int, default=52, help='Number of weeks to analyze (default: 52)')
    parser.add_argument('--limit', type=int, default=100, help='Posts per week (default: 100)')
    parser.add_argument('--tier1', action='store_true', help='Analyze all Tier 1 subreddits')

    args = parser.parse_args()

    print("=" * 70)
    print("🔍 REDDIT HISTORICAL SENTIMENT ANALYZER")
    print("=" * 70)
    print()

    analyzer = RedditHistoricalAnalyzer()

    # Setup Reddit client
    if not analyzer.setup_reddit_client():
        print("\n❌ Failed to setup Reddit API client. Exiting.")
        sys.exit(1)

    print()

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

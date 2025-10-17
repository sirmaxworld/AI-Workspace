#!/usr/bin/env python3
"""
Social Media Collector for Domain Knowledge Bases
Collects discussions from Reddit and analyzes sentiment
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    import praw
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    print("⚠️  Missing dependencies. Installing...")
    os.system("pip install praw vaderSentiment")
    import praw
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load environment
load_dotenv(project_root / '.env')


class DomainSocialCollector:
    """Collects social media content for a specific domain"""
    
    def __init__(self, domain_path: Path):
        self.domain_path = Path(domain_path)
        self.config = self._load_config()
        self.reddit = self._init_reddit()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Directories
        self.social_dir = self.domain_path / 'social'
        self.reddit_dir = self.social_dir / 'reddit'
        self.reddit_posts_file = self.reddit_dir / 'posts.json'
        self.sentiment_file = self.social_dir / 'sentiment.json'
        
        # Ensure directories exist
        self.reddit_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"💬 Social Collector for: {self.config['display_name']}")
    
    def _load_config(self) -> Dict:
        """Load domain configuration"""
        config_file = self.domain_path / 'config.json'
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def _init_reddit(self):
        """Initialize Reddit API (PRAW)"""
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'AI-Workspace Knowledge Collector v1.0')
        
        if not client_id or not client_secret:
            print("⚠️  Reddit API credentials not found in .env")
            print("   Get them at: https://www.reddit.com/prefs/apps")
            print("   Running in read-only mode (no authentication)")
            return praw.Reddit(
                client_id='temp',
                client_secret='temp',
                user_agent=user_agent,
                check_for_async=False
            )
        
        return praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        scores = self.sentiment_analyzer.polarity_scores(text)
        
        # Classify sentiment
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'compound': compound,
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }
    
    def collect_reddit_posts(self, subreddit_name: str, max_posts: int = 50) -> List[Dict]:
        """Collect posts from a subreddit"""
        print(f"  📋 Collecting from r/{subreddit_name}")
        
        posts = []
        config = self.config['social']['reddit']
        sort = config.get('sort', 'hot')
        time_filter = config.get('time_filter', 'week')
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get posts based on sort type
            if sort == 'hot':
                post_list = subreddit.hot(limit=max_posts)
            elif sort == 'top':
                post_list = subreddit.top(time_filter=time_filter, limit=max_posts)
            elif sort == 'new':
                post_list = subreddit.new(limit=max_posts)
            else:
                post_list = subreddit.hot(limit=max_posts)
            
            for post in post_list:
                # Analyze sentiment
                sentiment = self.analyze_sentiment(post.title + ' ' + post.selftext)
                
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'text': post.selftext,
                    'score': post.score,
                    'url': post.url,
                    'created_utc': post.created_utc,
                    'num_comments': post.num_comments,
                    'subreddit': subreddit_name,
                    'sentiment': sentiment
                }
                posts.append(post_data)
            
            print(f"    Found {len(posts)} posts")
            
        except Exception as e:
            print(f"    ✗ Error collecting from r/{subreddit_name}: {e}")
        
        return posts
    
    def collect_all(self) -> Dict:
        """Collect from all configured social sources"""
        print(f"\n{'='*60}")
        print(f"Starting social collection for: {self.config['display_name']}")
        print(f"{'='*60}\n")
        
        all_posts = []
        stats = {
            'subreddits_processed': 0,
            'posts_collected': 0,
            'sentiment_positive': 0,
            'sentiment_neutral': 0,
            'sentiment_negative': 0
        }
        
        # Collect from Reddit
        print("💬 Collecting from Reddit...")
        for subreddit in self.config['social']['reddit']['subreddits']:
            max_posts = self.config['social']['reddit'].get('max_posts_per_sub', 50)
            posts = self.collect_reddit_posts(subreddit, max_posts)
            all_posts.extend(posts)
            stats['subreddits_processed'] += 1
            stats['posts_collected'] += len(posts)
        
        # Calculate sentiment stats
        for post in all_posts:
            sentiment = post['sentiment']['sentiment']
            if sentiment == 'positive':
                stats['sentiment_positive'] += 1
            elif sentiment == 'negative':
                stats['sentiment_negative'] += 1
            else:
                stats['sentiment_neutral'] += 1
        
        # Save posts
        with open(self.reddit_posts_file, 'w') as f:
            json.dump(all_posts, f, indent=2)
        
        # Save sentiment summary
        sentiment_summary = {
            'collected_at': datetime.now().isoformat(),
            'total_posts': len(all_posts),
            'sentiment_distribution': {
                'positive': stats['sentiment_positive'],
                'neutral': stats['sentiment_neutral'],
                'negative': stats['sentiment_negative']
            },
            'sentiment_percentages': {
                'positive': round(stats['sentiment_positive'] / len(all_posts) * 100, 1) if all_posts else 0,
                'neutral': round(stats['sentiment_neutral'] / len(all_posts) * 100, 1) if all_posts else 0,
                'negative': round(stats['sentiment_negative'] / len(all_posts) * 100, 1) if all_posts else 0
            }
        }
        
        with open(self.sentiment_file, 'w') as f:
            json.dump(sentiment_summary, f, indent=2)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"✅ Social Collection Complete!")
        print(f"{'='*60}")
        print(f"Subreddits processed: {stats['subreddits_processed']}")
        print(f"Posts collected: {stats['posts_collected']}")
        print(f"\nSentiment Analysis:")
        print(f"  Positive: {stats['sentiment_positive']} ({sentiment_summary['sentiment_percentages']['positive']}%)")
        print(f"  Neutral: {stats['sentiment_neutral']} ({sentiment_summary['sentiment_percentages']['neutral']}%)")
        print(f"  Negative: {stats['sentiment_negative']} ({sentiment_summary['sentiment_percentages']['negative']}%)")
        print(f"\n📁 Posts saved to: {self.reddit_posts_file}")
        print(f"📊 Sentiment saved to: {self.sentiment_file}")
        print(f"{'='*60}\n")
        
        return stats


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python social_collector.py <domain_path>")
        print("Example: python social_collector.py /Users/yourox/AI-Workspace/domains/ai_trends")
        sys.exit(1)
    
    domain_path = Path(sys.argv[1])
    
    if not domain_path.exists():
        print(f"✗ Domain path does not exist: {domain_path}")
        sys.exit(1)
    
    collector = DomainSocialCollector(domain_path)
    collector.collect_all()


if __name__ == '__main__':
    main()

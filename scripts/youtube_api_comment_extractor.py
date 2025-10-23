#!/usr/bin/env python3
"""
YouTube Data API v3 Comment & Metadata Extractor
Free tier: 10,000 quota units/day
- Video metadata: 1 unit
- Comments: 1 unit per request (100 comments per request)
"""

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv('/Users/yourox/AI-Workspace/.env')


class YouTubeAPIExtractor:
    """Extract comments and metadata using YouTube Data API v3"""

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env")

        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.quota_used = 0

    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """
        Get video metadata (1 quota unit)
        Returns: title, channel, views, likes, duration, description, tags
        """
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            self.quota_used += 1

            if not response.get('items'):
                return None

            video = response['items'][0]
            snippet = video['snippet']
            statistics = video['statistics']
            content_details = video['contentDetails']

            metadata = {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'channel': snippet.get('channelTitle', ''),
                'channel_id': snippet.get('channelId', ''),
                'description': snippet.get('description', ''),
                'published_at': snippet.get('publishedAt', ''),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId', ''),
                'duration': content_details.get('duration', ''),
                'views': int(statistics.get('viewCount', 0)),
                'likes': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', '')
            }

            return metadata

        except HttpError as e:
            print(f"❌ API Error getting metadata: {e}")
            return None

    def get_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """
        Get top comments (1 quota unit per 100 comments)
        Returns: list of {author, text, likes, published_at, reply_count}
        """
        comments = []

        try:
            # Get top-level comments (sorted by relevance)
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_results, 100),
                order='relevance',  # Get most relevant comments
                textFormat='plainText'
            )

            response = request.execute()
            self.quota_used += 1

            for item in response.get('items', []):
                top_comment = item['snippet']['topLevelComment']['snippet']

                comments.append({
                    'author': top_comment.get('authorDisplayName', ''),
                    'author_channel_id': top_comment.get('authorChannelId', {}).get('value', ''),
                    'text': top_comment.get('textDisplay', ''),
                    'likes': int(top_comment.get('likeCount', 0)),
                    'published_at': top_comment.get('publishedAt', ''),
                    'reply_count': int(item['snippet'].get('totalReplyCount', 0))
                })

            # Get next page if we want more than 100 comments
            while 'nextPageToken' in response and len(comments) < max_results:
                request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(max_results - len(comments), 100),
                    pageToken=response['nextPageToken'],
                    order='relevance',
                    textFormat='plainText'
                )
                response = request.execute()
                self.quota_used += 1

                for item in response.get('items', []):
                    top_comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'author': top_comment.get('authorDisplayName', ''),
                        'author_channel_id': top_comment.get('authorChannelId', {}).get('value', ''),
                        'text': top_comment.get('textDisplay', ''),
                        'likes': int(top_comment.get('likeCount', 0)),
                        'published_at': top_comment.get('publishedAt', ''),
                        'reply_count': int(item['snippet'].get('totalReplyCount', 0))
                    })

            print(f"✅ Extracted {len(comments)} comments via API")
            return comments

        except HttpError as e:
            if 'commentsDisabled' in str(e):
                print(f"⚠️  Comments disabled for video {video_id}")
            else:
                print(f"❌ API Error getting comments: {e}")
            return []

    def get_video_full_data(self, video_id: str, max_comments: int = 100) -> Dict:
        """
        Get complete video data: metadata + comments
        Total cost: 2-3 quota units
        """
        print(f"🔍 Fetching video data for {video_id}...")

        metadata = self.get_video_metadata(video_id)
        if not metadata:
            return {
                'video_id': video_id,
                'error': 'Video not found or private',
                'status': 'error'
            }

        comments = self.get_comments(video_id, max_comments)

        result = {
            **metadata,
            'comments': comments,
            'comments_extracted': len(comments),
            'quota_used': self.quota_used,
            'status': 'success'
        }

        print(f"📊 Metadata: {metadata['title'][:50]}...")
        print(f"💬 Comments: {len(comments)} (from {metadata['comment_count']} total)")
        print(f"📈 Quota used: {self.quota_used} units")

        return result

    def enrich_existing_transcript(self, transcript_file: str, max_comments: int = 100) -> Dict:
        """
        Enrich existing transcript file with API metadata and comments
        """
        from pathlib import Path

        # Load existing transcript
        with open(transcript_file) as f:
            data = json.load(f)

        video_id = data.get('video_id')
        if not video_id:
            print(f"⚠️  No video_id in {transcript_file}")
            return data

        # Get API data
        api_data = self.get_video_full_data(video_id, max_comments)

        if api_data.get('status') == 'error':
            print(f"⚠️  Could not enrich {video_id}")
            return data

        # Merge API data into existing transcript
        enriched = {
            **data,  # Keep existing transcript data
            'metadata': {
                'title': api_data.get('title', data.get('title', '')),
                'channel': api_data.get('channel', data.get('channel', '')),
                'channel_id': api_data.get('channel_id', ''),
                'description': api_data.get('description', ''),
                'published_at': api_data.get('published_at', ''),
                'tags': api_data.get('tags', []),
                'duration': api_data.get('duration', ''),
                'views': api_data.get('views', 0),
                'likes': api_data.get('likes', 0),
                'comment_count_total': api_data.get('comment_count', 0),
                'thumbnail': api_data.get('thumbnail', '')
            },
            'comments': api_data.get('comments', []),
            'comments_extracted': len(api_data.get('comments', [])),
            'extraction_method': 'youtube_api_v3'
        }

        # Save enriched data
        with open(transcript_file, 'w') as f:
            json.dump(enriched, f, indent=2)

        print(f"💾 Enriched {transcript_file}")
        return enriched


def test_extractor(video_id: str = 'dQw4w9WgXcQ'):
    """Test the extractor on a sample video"""
    print(f"\n{'='*70}")
    print(f"🧪 TESTING YOUTUBE API EXTRACTOR")
    print(f"{'='*70}\n")

    extractor = YouTubeAPIExtractor()
    result = extractor.get_video_full_data(video_id, max_comments=50)

    print(f"\n{'='*70}")
    print(f"📋 RESULT:")
    print(json.dumps(result, indent=2, default=str))
    print(f"{'='*70}\n")

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python youtube_api_comment_extractor.py VIDEO_ID [MAX_COMMENTS]")
        print("\nTesting with default video...")
        test_extractor()
    else:
        video_id = sys.argv[1]
        max_comments = int(sys.argv[2]) if len(sys.argv) > 2 else 100

        extractor = YouTubeAPIExtractor()
        result = extractor.get_video_full_data(video_id, max_comments)

        if result.get('status') == 'success':
            print(f"\n✅ SUCCESS!")
        else:
            print(f"\n❌ FAILED: {result.get('error')}")

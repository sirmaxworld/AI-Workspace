#!/usr/bin/env python3.11
"""
Professional YouTube Transcription System with Hybrid Approach
- Tries youtube-transcript-api first (free, existing captions)
- Falls back to Whisper transcription (for videos without captions)
- Includes proxy rotation to avoid IP blocking
- Parallel processing with rate limiting
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# YouTube transcript retrieval
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound,
    VideoUnavailable
)

# Whisper for actual transcription
from openai import OpenAI

# Chunking and storage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from mem0 import Memory

# Video download (for Whisper transcription)
import yt_dlp

# Load environment variables
load_dotenv('/Users/yourox/AI-Workspace/.env')


class ProxyRotator:
    """
    Manages proxy rotation to avoid IP blocking
    Supports multiple proxy providers
    """
    
    def __init__(self, proxies: Optional[List[str]] = None):
        """
        Initialize with list of proxy URLs
        Format: ['http://user:pass@ip:port', ...]
        """
        self.proxies = proxies or []
        self.current_index = 0
        self.failed_proxies = set()
        
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next working proxy in rotation"""
        if not self.proxies:
            return None
            
        attempts = 0
        while attempts < len(self.proxies):
            proxy_url = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            if proxy_url not in self.failed_proxies:
                return {
                    'http': proxy_url,
                    'https': proxy_url
                }
            attempts += 1
            
        return None
    
    def mark_failed(self, proxy_url: str):
        """Mark proxy as failed"""
        self.failed_proxies.add(proxy_url)
    
    @classmethod
    def from_file(cls, filepath: str) -> 'ProxyRotator':
        """Load proxies from file (one per line)"""
        proxies = []
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        return cls(proxies)


class TranscriptionMethod:
    """Enum for transcription methods"""
    YOUTUBE_CAPTIONS = "youtube_captions"
    WHISPER_API = "whisper_api"
    WHISPER_LOCAL = "whisper_local"


class YouTubeTranscriberPro:
    """
    Professional YouTube Transcriber with hybrid approach and proxy support
    """
    
    def __init__(
        self, 
        user_id: str = "yourox_default",
        proxy_rotator: Optional[ProxyRotator] = None,
        use_whisper_fallback: bool = True,
        cache_dir: str = "/Users/yourox/AI-Workspace/data/transcripts"
    ):
        self.user_id = user_id
        self.proxy_rotator = proxy_rotator
        self.use_whisper_fallback = use_whisper_fallback
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize services
        self.memory = Memory()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=60,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            length_function=len
        )
        
        # Statistics
        self.stats = {
            'videos_processed': 0,
            'youtube_captions_used': 0,
            'whisper_transcriptions': 0,
            'failed': 0,
            'total_chunks': 0
        }
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats"""
        # Handle youtu.be short links
        if 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
        
        # Handle standard youtube.com links
        parsed = urlparse(url)
        if parsed.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed.path == '/watch':
                query_params = parse_qs(parsed.query)
                return query_params.get('v', [None])[0]
            elif parsed.path.startswith('/embed/'):
                return parsed.path.split('/')[2]
        
        # If it's just a video ID
        import re
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        return None
    
    def get_cached_transcript(self, video_id: str) -> Optional[Dict]:
        """Check if transcript is already cached"""
        cache_file = self.cache_dir / f"{video_id}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def cache_transcript(self, video_id: str, data: Dict):
        """Cache transcript data"""
        cache_file = self.cache_dir / f"{video_id}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def try_youtube_captions(
        self, 
        video_id: str, 
        languages: List[str] = ['en']
    ) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Try to get captions from YouTube
        Returns: (transcript_data, error_message)
        """
        try:
            # TODO: Add proxy support if needed
            # For now, using direct connection
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=languages
            )
            
            self.stats['youtube_captions_used'] += 1
            return transcript, None
            
        except TranscriptsDisabled:
            return None, "Transcripts are disabled for this video"
        except NoTranscriptFound:
            return None, "No transcript available in requested languages"
        except VideoUnavailable:
            return None, "Video is unavailable"
        except Exception as e:
            return None, f"Error retrieving transcript: {str(e)}"
    
    def download_audio(self, video_id: str) -> Optional[str]:
        """
        Download video audio for Whisper transcription
        Returns path to audio file
        """
        output_path = self.cache_dir / f"{video_id}_audio.mp3"
        
        if output_path.exists():
            return str(output_path)
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(self.cache_dir / f"{video_id}_audio.%(ext)s"),
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            
            return str(output_path) if output_path.exists() else None
            
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None
    
    def transcribe_with_whisper(
        self, 
        video_id: str,
        audio_path: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Transcribe using OpenAI Whisper API
        Returns transcript in same format as YouTube captions
        """
        try:
            if not audio_path:
                audio_path = self.download_audio(video_id)
                
            if not audio_path:
                return None
            
            print(f"  🎙️  Transcribing with Whisper: {video_id}")
            
            with open(audio_path, 'rb') as audio_file:
                transcript_response = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            # Convert Whisper format to YouTube transcript format
            transcript = []
            for segment in transcript_response.segments:
                transcript.append({
                    'text': segment['text'].strip(),
                    'start': segment['start'],
                    'duration': segment['end'] - segment['start']
                })
            
            self.stats['whisper_transcriptions'] += 1
            return transcript
            
        except Exception as e:
            print(f"Error with Whisper transcription: {e}")
            return None
    
    def get_video_metadata(self, video_id: str) -> Dict:
        """
        Get video metadata using yt-dlp
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f'https://www.youtube.com/watch?v={video_id}',
                    download=False
                )
                
                return {
                    'video_id': video_id,
                    'title': info.get('title', 'Unknown'),
                    'channel': info.get('channel', 'Unknown'),
                    'upload_date': info.get('upload_date', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', '')[:500],  # First 500 chars
                    'tags': info.get('tags', [])[:10],  # First 10 tags
                    'thumbnail': info.get('thumbnail', ''),
                }
        except Exception as e:
            print(f"Error getting metadata: {e}")
            return {
                'video_id': video_id,
                'title': 'Unknown',
                'channel': 'Unknown'
            }
    
    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def chunk_transcript(
        self, 
        transcript: List[Dict],
        metadata: Dict
    ) -> List[Dict]:
        """
        Chunk transcript with semantic awareness and metadata
        """
        # Combine all text with timestamps
        full_text = ""
        timestamp_map = []
        
        for entry in transcript:
            text = entry['text']
            start_time = entry['start']
            
            timestamp_map.append({
                'char_pos': len(full_text),
                'start': start_time
            })
            
            full_text += text + " "
        
        # Split into chunks
        chunks = self.text_splitter.split_text(full_text)
        
        # Map chunks back to timestamps
        chunked_data = []
        for chunk_text in chunks:
            # Find approximate start time
            chunk_pos = full_text.find(chunk_text)
            start_time = 0
            
            for tm in timestamp_map:
                if tm['char_pos'] <= chunk_pos:
                    start_time = tm['start']
                else:
                    break
            
            chunked_data.append({
                'text': chunk_text.strip(),
                'start_time': start_time,
                'timestamp_url': f"https://youtube.com/watch?v={metadata['video_id']}&t={int(start_time)}s",
                'formatted_time': self.format_timestamp(start_time)
            })
        
        return chunked_data
    
    def store_in_mem0(
        self, 
        chunks: List[Dict], 
        metadata: Dict,
        transcription_method: str
    ):
        """Store chunks in Mem0 with rich metadata"""
        print(f"  💾 Storing {len(chunks)} chunks in Mem0...")
        
        for i, chunk in enumerate(chunks):
            memory_text = f"""
Video: {metadata['title']}
Channel: {metadata['channel']}
Timestamp: {chunk['formatted_time']}
Link: {chunk['timestamp_url']}

Content: {chunk['text']}
"""
            
            self.memory.add(
                memory_text,
                user_id=self.user_id,
                metadata={
                    "type": "youtube_transcript",
                    "video_id": metadata['video_id'],
                    "video_title": metadata['title'],
                    "channel": metadata['channel'],
                    "timestamp": chunk['start_time'],
                    "timestamp_url": chunk['timestamp_url'],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "transcription_method": transcription_method,
                    "upload_date": metadata.get('upload_date', ''),
                    "tags": ','.join(metadata.get('tags', [])[:5])
                }
            )
        
        self.stats['total_chunks'] += len(chunks)
    
    async def process_video(
        self, 
        video_url: str,
        languages: List[str] = ['en']
    ) -> Dict:
        """
        Main method: Process a single YouTube video
        
        Returns dict with status and details
        """
        print(f"\n{'='*60}")
        print(f"Processing: {video_url}")
        print(f"{'='*60}")
        
        # Extract video ID
        video_id = self.extract_video_id(video_url)
        if not video_id:
            return {"status": "error", "message": "Invalid YouTube URL"}
        
        print(f"Video ID: {video_id}")
        
        # Check cache
        cached = self.get_cached_transcript(video_id)
        if cached:
            print(f"  ✓ Using cached transcript")
            transcript = cached['transcript']
            metadata = cached['metadata']
            method = cached.get('method', TranscriptionMethod.YOUTUBE_CAPTIONS)
        else:
            # Get metadata first
            print(f"  📊 Fetching metadata...")
            metadata = self.get_video_metadata(video_id)
            print(f"  Title: {metadata['title']}")
            print(f"  Channel: {metadata['channel']}")
            
            # Try Method 1: YouTube captions (fast & free)
            print(f"  🔍 Trying YouTube captions...")
            transcript, error = self.try_youtube_captions(video_id, languages)
            
            if transcript:
                method = TranscriptionMethod.YOUTUBE_CAPTIONS
                print(f"  ✓ Got YouTube captions ({len(transcript)} segments)")
            
            # Method 2: Whisper transcription (fallback)
            elif self.use_whisper_fallback:
                print(f"  ⚠️  No captions available: {error}")
                print(f"  🎙️  Falling back to Whisper transcription...")
                
                transcript = self.transcribe_with_whisper(video_id)
                method = TranscriptionMethod.WHISPER_API
                
                if not transcript:
                    self.stats['failed'] += 1
                    return {
                        "status": "error",
                        "message": "Failed to transcribe video",
                        "video_id": video_id
                    }
            else:
                self.stats['failed'] += 1
                return {
                    "status": "error", 
                    "message": error,
                    "video_id": video_id
                }
            
            # Cache the results
            self.cache_transcript(video_id, {
                'transcript': transcript,
                'metadata': metadata,
                'method': method,
                'cached_at': datetime.now().isoformat()
            })
        
        # Chunk transcript
        print(f"  ✂️  Chunking transcript...")
        chunks = self.chunk_transcript(transcript, metadata)
        print(f"  ✓ Created {len(chunks)} chunks")
        
        # Store in Mem0
        self.store_in_mem0(chunks, metadata, method)
        
        self.stats['videos_processed'] += 1
        
        return {
            "status": "success",
            "video_id": video_id,
            "title": metadata['title'],
            "channel": metadata['channel'],
            "chunks": len(chunks),
            "method": method,
            "transcript_segments": len(transcript)
        }
    
    async def process_multiple_videos(
        self,
        video_urls: List[str],
        max_concurrent: int = 3,
        delay_between: float = 2.0
    ) -> List[Dict]:
        """
        Process multiple videos with rate limiting
        """
        results = []
        
        for i, url in enumerate(video_urls):
            print(f"\n[{i+1}/{len(video_urls)}]")
            
            result = await self.process_video(url)
            results.append(result)
            
            # Rate limiting delay
            if i < len(video_urls) - 1:
                await asyncio.sleep(delay_between)
        
        return results
    
    def print_stats(self):
        """Print processing statistics"""
        print(f"\n{'='*60}")
        print(f"PROCESSING STATISTICS")
        print(f"{'='*60}")
        print(f"Videos Processed: {self.stats['videos_processed']}")
        print(f"  ├─ YouTube Captions: {self.stats['youtube_captions_used']}")
        print(f"  ├─ Whisper Transcriptions: {self.stats['whisper_transcriptions']}")
        print(f"  └─ Failed: {self.stats['failed']}")
        print(f"Total Chunks Stored: {self.stats['total_chunks']}")
        print(f"{'='*60}\n")
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search stored transcripts
        """
        results = self.memory.search(
            query=query,
            user_id=self.user_id,
            limit=limit
        )
        
        enriched = []
        for result in results.get('results', []):
            metadata = result.get('metadata', {})
            enriched.append({
                'content': result['memory'],
                'video_title': metadata.get('video_title', ''),
                'channel': metadata.get('channel', ''),
                'timestamp_url': metadata.get('timestamp_url', ''),
                'transcription_method': metadata.get('transcription_method', ''),
                'relevance': result.get('score', 0)
            })
        
        return enriched


# Example usage and CLI
if __name__ == "__main__":
    import sys
    
    # Initialize transcriber
    transcriber = YouTubeTranscriberPro(
        use_whisper_fallback=True,  # Enable Whisper for videos without captions
        proxy_rotator=None  # Can add proxy rotation later
    )
    
    # Example: Process single video
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        result = asyncio.run(transcriber.process_video(video_url))
        print(f"\nResult: {json.dumps(result, indent=2)}")
        transcriber.print_stats()
    else:
        print("Usage: python youtube_transcriber_pro.py <youtube_url>")
        print("\nExample:")
        print("  python youtube_transcriber_pro.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")

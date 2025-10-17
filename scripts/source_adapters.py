#!/usr/bin/env python3
"""
Universal Source Adapters - Domain-Agnostic Data Extraction
Professional adapter pattern for all knowledge sources
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json

import yt_dlp
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')


@dataclass
class ExtractionConfig:
    """Configuration for source extraction"""
    max_items: int = 50
    filters: Dict[str, Any] = None
    quality_thresholds: Dict[str, float] = None
    cache_enabled: bool = True
    parallel_batch_size: int = 10

    def __post_init__(self):
        if self.filters is None:
            self.filters = {}
        if self.quality_thresholds is None:
            self.quality_thresholds = {
                'min_completeness': 0.7,
                'min_quality': 0.7,
                'min_confidence': 0.75
            }


@dataclass
class SourceItem:
    """Standardized data item from any source"""
    id: str
    title: str
    url: str
    source_type: str  # youtube, research, social, industry
    source_name: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = None
    extracted_at: str = None

    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source_type': self.source_type,
            'source_name': self.source_name,
            'content': self.content,
            'metadata': self.metadata,
            'extracted_at': self.extracted_at
        }


class SourceAdapter(ABC):
    """
    Base adapter for all knowledge sources

    Implements the Adapter pattern for consistent data extraction
    """

    def __init__(self, config: ExtractionConfig = None):
        self.config = config or ExtractionConfig()
        self.cache_dir = Path('/Users/yourox/AI-Workspace/data/adapter_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {
            'discovered': 0,
            'extracted': 0,
            'filtered': 0,
            'failed': 0
        }

    @abstractmethod
    def discover(self, source_config: Dict) -> List[Dict]:
        """
        Discover available items from source

        Args:
            source_config: Source-specific configuration

        Returns:
            List of discovered items (lightweight metadata)
        """
        pass

    @abstractmethod
    def extract(self, item: Dict) -> SourceItem:
        """
        Extract full data from single item

        Args:
            item: Item to extract (from discover())

        Returns:
            Fully populated SourceItem
        """
        pass

    def validate(self, item: SourceItem) -> tuple[bool, List[str]]:
        """
        Validate extracted item against filters

        Args:
            item: Extracted item

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        # Basic validation
        if not item.id:
            issues.append("Missing ID")
        if not item.title:
            issues.append("Missing title")
        if not item.url:
            issues.append("Missing URL")

        # Apply custom filters
        for filter_name, filter_value in self.config.filters.items():
            if not self._apply_filter(item, filter_name, filter_value):
                issues.append(f"Failed filter: {filter_name}")

        return (len(issues) == 0, issues)

    def _apply_filter(self, item: SourceItem, filter_name: str, filter_value: Any) -> bool:
        """Apply individual filter to item"""
        # Override in subclasses for source-specific filters
        return True

    def transform(self, item: SourceItem) -> Dict:
        """
        Transform to standardized knowledge base format

        Args:
            item: Source item

        Returns:
            Standardized dict for knowledge pipeline
        """
        return {
            'id': f"{item.source_type}_{item.id}",
            'title': item.title,
            'content': item.content or '',
            'source_type': item.source_type,
            'source_url': item.url,
            'tags': item.metadata.get('tags', []),
            'timestamp': item.extracted_at,
            'metadata': item.metadata
        }

    def extract_batch(
        self,
        source_config: Dict,
        progress_callback=None
    ) -> List[SourceItem]:
        """
        Full extraction pipeline: discover → extract → validate → transform

        Args:
            source_config: Source-specific configuration
            progress_callback: Optional callback(current, total, item)

        Returns:
            List of validated SourceItems
        """
        print(f"\n{'='*70}")
        print(f"🔍 Starting {self.__class__.__name__} extraction")
        print(f"{'='*70}\n")

        # Step 1: Discover
        print(f"📡 Discovering items...")
        discovered = self.discover(source_config)
        self.stats['discovered'] = len(discovered)
        print(f"   Found {len(discovered)} items\n")

        # Step 2: Extract & Validate
        print(f"📥 Extracting and validating...")
        valid_items = []

        for idx, item_meta in enumerate(discovered[:self.config.max_items], 1):
            try:
                # Extract
                item = self.extract(item_meta)

                # Validate
                is_valid, issues = self.validate(item)

                if is_valid:
                    valid_items.append(item)
                    self.stats['extracted'] += 1
                    status = "✓"
                else:
                    self.stats['filtered'] += 1
                    status = f"⏭ Filtered: {', '.join(issues[:2])}"

                print(f"   [{idx}/{min(len(discovered), self.config.max_items)}] {status} {item.title[:60]}")

                if progress_callback:
                    progress_callback(idx, len(discovered), item)

            except Exception as e:
                self.stats['failed'] += 1
                print(f"   [{idx}/{min(len(discovered), self.config.max_items)}] ❌ Failed: {e}")

        print(f"\n{'='*70}")
        print(f"📊 Extraction Complete")
        print(f"   Discovered: {self.stats['discovered']}")
        print(f"   Extracted: {self.stats['extracted']}")
        print(f"   Filtered: {self.stats['filtered']}")
        print(f"   Failed: {self.stats['failed']}")
        print(f"{'='*70}\n")

        return valid_items


class YouTubeAdapter(SourceAdapter):
    """
    Universal YouTube channel adapter

    Extracts videos from any YouTube channel with advanced filtering
    """

    def __init__(self, config: ExtractionConfig = None):
        super().__init__(config)
        self.shorts_max_duration = 60  # Default threshold

    def discover(self, source_config: Dict) -> List[Dict]:
        """
        Discover videos from YouTube channel

        source_config format:
        {
            'handle': '@ChannelName' or 'channel_url',
            'max_videos': 50,
            'days_back': optional int
        }
        """
        handle = source_config['handle']
        max_videos = source_config.get('max_videos', self.config.max_items)

        # Build channel URL
        if not handle.startswith('http'):
            if handle.startswith('@'):
                channel_url = f"https://www.youtube.com/{handle}/videos"
            else:
                channel_url = f"https://www.youtube.com/c/{handle}/videos"
        else:
            channel_url = handle if '/videos' in handle else f"{handle}/videos"

        # Extract videos
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'playlistend': max_videos * 2,  # Fetch extra for filtering
            'ignoreerrors': True,
        }

        videos = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)

            if not info:
                raise ValueError(f"Could not extract channel info from {channel_url}")

            channel_name = info.get('channel', info.get('uploader', 'Unknown'))
            entries = info.get('entries', [])

            for entry in entries:
                if not entry:
                    continue

                video_id = entry.get('id')
                if not video_id:
                    continue

                videos.append({
                    'id': video_id,
                    'title': entry.get('title', 'Unknown'),
                    'channel': channel_name,
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })

        return videos

    def extract(self, item: Dict) -> SourceItem:
        """Extract full video metadata"""

        video_id = item['id']

        # Get detailed metadata
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False
            )

        duration = info.get('duration', 0)

        return SourceItem(
            id=video_id,
            title=info.get('title', item['title']),
            url=item['url'],
            source_type='youtube',
            source_name=info.get('channel', item.get('channel', 'Unknown')),
            metadata={
                'duration': duration,
                'duration_formatted': self._format_duration(duration),
                'upload_date': info.get('upload_date', ''),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'description': (info.get('description', '') or '')[:500],
                'tags': info.get('tags', [])[:10],
                'thumbnail': info.get('thumbnail', ''),
                'is_short': duration > 0 and duration <= self.shorts_max_duration
            }
        )

    def _apply_filter(self, item: SourceItem, filter_name: str, filter_value: Any) -> bool:
        """Apply YouTube-specific filters"""

        if filter_name == 'exclude_shorts' and filter_value:
            return not item.metadata.get('is_short', False)

        if filter_name == 'min_duration':
            return item.metadata.get('duration', 0) >= filter_value

        if filter_name == 'max_age_days':
            upload_date_str = item.metadata.get('upload_date', '')
            if upload_date_str:
                try:
                    upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
                    cutoff = datetime.now() - timedelta(days=filter_value)
                    return upload_date >= cutoff
                except:
                    pass
            return True

        return True

    def _format_duration(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"


# Factory for creating adapters
class AdapterFactory:
    """Factory for creating source adapters"""

    _adapters = {
        'youtube': YouTubeAdapter,
        # Future: 'research': ResearchAdapter,
        # Future: 'social': SocialAdapter,
        # Future: 'industry': IndustryAdapter,
    }

    @classmethod
    def create(cls, source_type: str, config: ExtractionConfig = None) -> SourceAdapter:
        """Create adapter by type"""
        adapter_class = cls._adapters.get(source_type)
        if not adapter_class:
            raise ValueError(f"Unknown source type: {source_type}")
        return adapter_class(config)

    @classmethod
    def register(cls, source_type: str, adapter_class: type):
        """Register new adapter type"""
        cls._adapters[source_type] = adapter_class


def main():
    """CLI for testing adapters"""
    import argparse

    parser = argparse.ArgumentParser(description='Test source adapters')
    parser.add_argument('source_type', choices=['youtube'], help='Source type')
    parser.add_argument('--handle', required=True, help='Channel handle or URL')
    parser.add_argument('--max-items', type=int, default=10, help='Max items')
    parser.add_argument('--exclude-shorts', action='store_true', help='Exclude YouTube Shorts')
    parser.add_argument('--min-duration', type=int, help='Minimum duration (seconds)')

    args = parser.parse_args()

    # Create config
    config = ExtractionConfig(
        max_items=args.max_items,
        filters={
            'exclude_shorts': args.exclude_shorts,
            'min_duration': args.min_duration or 0
        }
    )

    # Create adapter
    adapter = AdapterFactory.create(args.source_type, config)

    # Extract
    items = adapter.extract_batch({
        'handle': args.handle,
        'max_videos': args.max_items
    })

    # Show results
    print(f"\n{'='*70}")
    print(f"RESULTS")
    print(f"{'='*70}\n")

    for item in items[:5]:
        print(f"✓ {item.title}")
        print(f"  URL: {item.url}")
        print(f"  Duration: {item.metadata.get('duration_formatted', 'N/A')}")
        print()


if __name__ == '__main__':
    main()

'use client';

import { useEffect, useState } from 'react';
import { Video, Library } from 'lucide-react';
import VideoCard from '@/components/video/video-card';
import { Video as VideoType } from '@/lib/types';

export default function LibraryPage() {
  const [videos, setVideos] = useState<VideoType[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('actionability');

  useEffect(() => {
    fetch('/api/batch')
      .then(res => res.json())
      .then(data => {
        setVideos(data.videos || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading videos:', err);
        setLoading(false);
      });
  }, []);

  // Filter videos
  let filteredVideos = videos;
  if (filter !== 'all') {
    filteredVideos = videos.filter(v => v.enrichment?.videoType === filter);
  }

  // Sort videos
  const sortedVideos = [...filteredVideos].sort((a, b) => {
    if (sortBy === 'actionability') {
      return (b.enrichment?.avgActionability || 0) - (a.enrichment?.avgActionability || 0);
    } else if (sortBy === 'opportunities') {
      return (b.summary?.opportunityMap?.total_opportunities || 0) - (a.summary?.opportunityMap?.total_opportunities || 0);
    }
    return 0;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Loading library...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-6 py-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <Library className="w-8 h-8 text-slate-700" />
            <h1 className="text-3xl font-bold text-slate-800">Video Library</h1>
          </div>
          <p className="text-gray-600">Browse all {videos.length} videos with detailed insights</p>
        </div>

        {/* Filters and Sorting */}
        <div className="glass-card p-4 mb-6">
          <div className="flex items-center gap-4 flex-wrap">
            <div>
              <label className="text-sm font-medium text-gray-700 mr-2">Filter:</label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="all">All Types</option>
                <option value="entrepreneurship">Entrepreneurship</option>
                <option value="market_research">Market Research</option>
                <option value="tutorial">Tutorial</option>
                <option value="interview">Interview</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mr-2">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="actionability">Highest Quality</option>
                <option value="opportunities">Most Opportunities</option>
              </select>
            </div>
            <div className="ml-auto text-sm text-gray-600">
              Showing {sortedVideos.length} videos
            </div>
          </div>
        </div>

        {/* Video Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedVideos.map(video => (
            <VideoCard key={video.video_id} video={video} onSelect={() => {}} view="grid" />
          ))}
        </div>
      </div>
    </div>
  );
}

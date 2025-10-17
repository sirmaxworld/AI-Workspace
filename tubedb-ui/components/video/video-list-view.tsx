'use client';

import { useState } from 'react';
import * as Accordion from '@radix-ui/react-accordion';
import { ChevronDown, Target, Sparkles, Star } from 'lucide-react';
import { Video } from '@/lib/types';
import { VideoCategory } from '@/lib/categorization-utils';
import VideoListItem from './video-list-item';

interface VideoListViewProps {
  categories: VideoCategory[];
  onVideoClick: (video: Video) => void;
}

export default function VideoListView({ categories, onVideoClick }: VideoListViewProps) {
  const [expandedItems, setExpandedItems] = useState<string[]>(
    categories.slice(0, 3).map(cat => cat.name) // Open first 3 by default
  );

  return (
    <div className="glass-card">
      <Accordion.Root
        type="multiple"
        value={expandedItems}
        onValueChange={setExpandedItems}
        className="w-full"
      >
        {categories.map((category) => (
          <Accordion.Item
            key={category.name}
            value={category.name}
            className="border-b border-gray-200 last:border-b-0"
          >
            <Accordion.Header>
              <Accordion.Trigger className="flex items-center justify-between w-full px-6 py-4 text-left hover:bg-gray-50 transition-colors group">
                <div className="flex items-center gap-4 flex-1">
                  <ChevronDown
                    className="w-5 h-5 text-gray-500 transition-transform duration-200 group-data-[state=open]:rotate-180"
                  />

                  {/* Category Name & Count */}
                  <div>
                    <h3 className="text-base font-semibold text-slate-800">
                      {category.name}
                    </h3>
                    <p className="text-xs text-gray-600 mt-0.5">
                      {category.count} videos
                    </p>
                  </div>
                </div>

                {/* Category Stats */}
                <div className="flex items-center gap-3">
                  {/* Avg Quality */}
                  <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-blue-50 border border-blue-200">
                    <Sparkles className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-700">
                      {category.avgQuality}% avg
                    </span>
                  </div>

                  {/* Total Opportunities */}
                  {category.totalOpportunities > 0 && (
                    <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-purple-50 border border-purple-200">
                      <Target className="w-4 h-4 text-purple-600" />
                      <span className="text-sm font-medium text-purple-700">
                        {category.totalOpportunities} opps
                      </span>
                    </div>
                  )}

                  {/* High Value Count */}
                  {category.highValueCount > 0 && (
                    <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-yellow-50 border border-yellow-200">
                      <Star className="w-4 h-4 text-yellow-600 fill-yellow-600" />
                      <span className="text-sm font-medium text-yellow-700">
                        {category.highValueCount} HV
                      </span>
                    </div>
                  )}
                </div>
              </Accordion.Trigger>
            </Accordion.Header>

            <Accordion.Content className="overflow-hidden data-[state=open]:animate-accordion-down data-[state=closed]:animate-accordion-up">
              <div className="bg-white">
                {category.videos.map(video => (
                  <VideoListItem
                    key={video.video_id}
                    video={video}
                    onClick={() => onVideoClick(video)}
                  />
                ))}
              </div>
            </Accordion.Content>
          </Accordion.Item>
        ))}
      </Accordion.Root>
    </div>
  );
}

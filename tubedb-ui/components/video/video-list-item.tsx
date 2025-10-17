'use client';

import { Video } from '@/lib/types';
import { Play, Target, Sparkles, Star, Package, Lightbulb, TrendingUp, Eye } from 'lucide-react';

interface VideoListItemProps {
  video: Video;
  onClick?: () => void;
}

export default function VideoListItem({ video, onClick }: VideoListItemProps) {
  const enrichment = video.enrichment;
  const summary = video.summary;
  const opportunityCount = summary?.opportunityMap?.total_opportunities || 0;
  const highValueCount = enrichment?.highValueInsights || 0;
  const totalInsights = video.insights
    ? Object.values(video.insights).reduce((acc: number, val: any) => acc + (val || 0), 0)
    : 0;

  // Get quality color
  const getQualityColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 40) return 'text-amber-600 bg-amber-50 border-amber-200';
    if (score >= 20) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  return (
    <div
      onClick={onClick}
      className="flex items-center justify-between p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors group"
    >
      {/* Left: Video info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3">
          <Play className="w-5 h-5 text-slate-600 flex-shrink-0" />
          <div className="min-w-0 flex-1">
            <h4 className="text-sm font-medium text-slate-800 truncate group-hover:text-slate-900">
              {video.title}
            </h4>
            <div className="flex items-center gap-4 mt-1 text-xs text-gray-600">
              {/* Insight counts */}
              {video.insights?.products > 0 && (
                <span className="flex items-center gap-1">
                  <Package className="w-3 h-3" />
                  {video.insights.products}
                </span>
              )}
              {video.insights?.ideas > 0 && (
                <span className="flex items-center gap-1">
                  <Lightbulb className="w-3 h-3" />
                  {video.insights.ideas}
                </span>
              )}
              {video.insights?.trends > 0 && (
                <span className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  {video.insights.trends}
                </span>
              )}
              <span className="text-gray-400">•</span>
              <span>{totalInsights} total insights</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right: Metrics */}
      <div className="flex items-center gap-2 ml-4 flex-shrink-0">
        {/* Quality Score */}
        {enrichment && (
          <div
            className={`px-2 py-1 rounded-md text-xs font-medium border ${getQualityColor(
              enrichment.avgActionability
            )}`}
          >
            <Sparkles className="w-3 h-3 inline mr-1" />
            {Math.round(enrichment.avgActionability)}%
          </div>
        )}

        {/* Opportunities */}
        {opportunityCount > 0 && (
          <div className="px-2 py-1 rounded-md bg-purple-50 border border-purple-200 text-xs font-medium text-purple-700">
            <Target className="w-3 h-3 inline mr-1" />
            {opportunityCount}
          </div>
        )}

        {/* High Value Badge */}
        {highValueCount > 0 && (
          <div className="px-2 py-1 rounded-md bg-yellow-50 border border-yellow-200 text-xs font-medium text-yellow-700">
            <Star className="w-3 h-3 inline mr-1 fill-yellow-600" />
            {highValueCount}
          </div>
        )}

        {/* View Details Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onClick?.();
          }}
          className="px-3 py-1 text-xs font-medium text-slate-700 bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
        >
          <Eye className="w-3 h-3 inline mr-1" />
          View
        </button>
      </div>
    </div>
  );
}

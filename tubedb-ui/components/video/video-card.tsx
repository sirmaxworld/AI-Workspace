'use client';

import { Play, Lightbulb, TrendingUp, Package, Target, Sparkles, Star } from 'lucide-react';
import { Video } from '@/lib/types';

interface VideoCardProps {
  video: Video;
  onClick?: () => void;
}

export default function VideoCard({ video, onClick }: VideoCardProps) {
  // Calculate total insights
  const totalInsights = video.insights ?
    Object.values(video.insights).reduce((acc: number, val: any) => acc + (val || 0), 0) : 0;

  // Get enrichment data
  const enrichment = video.enrichment;
  const summary = video.summary;
  const opportunityCount = summary?.opportunityMap?.total_opportunities || 0;
  const highValueCount = enrichment?.highValueInsights || 0;

  return (
    <div
      onClick={onClick}
      className="glass-card p-5 cursor-pointer group relative"
    >
      {/* High-Value Badge */}
      {highValueCount > 0 && (
        <div className="absolute top-3 right-3 px-2 py-1 rounded-lg bg-yellow-50 border border-yellow-200 flex items-center gap-1">
          <Star className="w-3 h-3 text-yellow-600 fill-yellow-600" />
          <span className="text-xs font-medium text-yellow-700">{highValueCount} HV</span>
        </div>
      )}

      {/* Video Info */}
      <div className="space-y-4">
        {/* Title */}
        <h3 className="text-lg font-semibold text-slate-800 line-clamp-2 group-hover:text-slate-900 transition-colors pr-16">
          {video.title}
        </h3>

        {/* Insights Summary */}
        <div className="grid grid-cols-3 gap-2 text-sm">
          {video.insights?.products > 0 && (
            <div className="flex items-center gap-1 text-gray-600">
              <Package className="w-4 h-4 text-slate-600" />
              <span>{video.insights.products} products</span>
            </div>
          )}
          {video.insights?.ideas > 0 && (
            <div className="flex items-center gap-1 text-gray-600">
              <Lightbulb className="w-4 h-4 text-blue-700" />
              <span>{video.insights.ideas} ideas</span>
            </div>
          )}
          {video.insights?.trends > 0 && (
            <div className="flex items-center gap-1 text-gray-600">
              <TrendingUp className="w-4 h-4 text-blue-800" />
              <span>{video.insights.trends} trends</span>
            </div>
          )}
        </div>

        {/* Enrichment Metrics */}
        {enrichment && (
          <div className="flex items-center gap-2 flex-wrap">
            <div className="px-2 py-1 rounded-md bg-green-50 border border-green-200 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-green-600" />
              <span className="text-xs font-medium text-green-700">{Math.round(enrichment.avgActionability)}% Action</span>
            </div>
            {opportunityCount > 0 && (
              <div className="px-2 py-1 rounded-md bg-purple-50 border border-purple-200 flex items-center gap-1">
                <Target className="w-3 h-3 text-purple-600" />
                <span className="text-xs font-medium text-purple-700">{opportunityCount} Opps</span>
              </div>
            )}
            <div className="px-2 py-1 rounded-md bg-blue-50 border border-blue-200 flex items-center gap-1">
              <span className="text-xs font-medium text-blue-700">{enrichment.videoType}</span>
            </div>
          </div>
        )}

        {/* Total Insights Badge */}
        <div className="flex items-center justify-between">
          <div className="px-3 py-1 rounded-lg text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
            {totalInsights} Total Insights
          </div>
          {video.hasTranscript && (
            <div className="flex items-center gap-2 text-gray-600">
              <Play className="w-4 h-4 text-slate-600" />
              <span className="text-xs">Transcript Available</span>
            </div>
          )}
        </div>

        {/* Featured Products */}
        {video.featured_products && video.featured_products.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {video.featured_products.slice(0, 2).map((product: any, idx: number) => (
              <span
                key={idx}
                className="px-2 py-1 rounded-md bg-gray-100 text-xs text-gray-700 border border-gray-200"
              >
                {product.name}
              </span>
            ))}
            {video.featured_products.length > 2 && (
              <span className="px-2 py-1 rounded-md bg-gray-50 text-xs text-gray-600 border border-gray-200">
                +{video.featured_products.length - 2} more
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

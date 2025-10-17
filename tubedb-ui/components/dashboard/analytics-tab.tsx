'use client';

import { useEffect, useState } from 'react';
import { Video } from '@/lib/types';
import {
  transformToQualityHeatmap,
  transformToInsightTreemap,
  transformToOpportunityData,
  transformToQualityDistribution,
  transformToVideoTypeRadar,
  getTopVideosByMetric,
} from '@/lib/chart-utils';
import QualityHeatmap from '@/components/charts/QualityHeatmap';
import InsightTreemap from '@/components/charts/InsightTreemap';
import OpportunityChart from '@/components/charts/OpportunityChart';
import QualityDistribution from '@/components/charts/QualityDistribution';
import VideoTypeRadar from '@/components/charts/VideoTypeRadar';
import TopVideosChart from '@/components/charts/TopVideosChart';

export default function AnalyticsTab() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);

  useEffect(() => {
    fetch('/api/batch')
      .then(res => res.json())
      .then(data => {
        setVideos(data.videos || []);
        if (data.videos && data.videos.length > 0) {
          setSelectedVideo(data.videos[0]);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading data:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading analytics...</div>
      </div>
    );
  }

  const heatmapData = transformToQualityHeatmap(videos);
  const treemapData = transformToInsightTreemap(videos);
  const opportunityData = transformToOpportunityData(videos);
  const distributionData = transformToQualityDistribution(videos);
  const radarData = transformToVideoTypeRadar(selectedVideo);
  const topVideos = getTopVideosByMetric(videos, 'opportunities', 10);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Analytics Dashboard</h2>
        <p className="text-gray-600">Deep dive into your video intelligence data</p>
      </div>

      {/* Quality Metrics Heatmap */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">Quality Metrics Matrix</h3>
        <p className="text-sm text-gray-600 mb-4">
          Top 50 videos with quality scores (0-100 scale)
        </p>
        <div className="h-[800px] overflow-auto">
          <QualityHeatmap data={heatmapData} />
        </div>
      </div>

      {/* Two Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Insight Distribution */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Insight Distribution</h3>
          <p className="text-sm text-gray-600 mb-4">
            Distribution of insight types across all videos
          </p>
          <div className="h-[400px]">
            <InsightTreemap data={treemapData} />
          </div>
        </div>

        {/* Opportunity Breakdown */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Opportunity Breakdown</h3>
          <p className="text-sm text-gray-600 mb-4">
            Distribution of {opportunityData.reduce((sum, d) => sum + d.value, 0)} opportunities by type
          </p>
          <div className="h-[400px]">
            <OpportunityChart data={opportunityData} />
          </div>
        </div>
      </div>

      {/* Two Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quality Distribution */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">
            Actionability Score Distribution
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            How videos are distributed across quality ranges
          </p>
          <div className="h-[400px]">
            <QualityDistribution data={distributionData} />
          </div>
        </div>

        {/* Video Type Classification */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">
            Video Type Classification
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Classification scores for: {selectedVideo?.title.substring(0, 50)}...
          </p>
          <div className="h-[400px]">
            <VideoTypeRadar data={radarData} />
          </div>
        </div>
      </div>

      {/* Top Videos by Opportunities */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">
          Top 10 Videos by Opportunities
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Videos with the highest number of identified opportunities
        </p>
        <div className="h-[500px]">
          <TopVideosChart data={topVideos} metric="Opportunities" />
        </div>
      </div>
    </div>
  );
}

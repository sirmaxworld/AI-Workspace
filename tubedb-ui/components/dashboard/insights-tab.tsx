'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, Target, Lightbulb, Zap, AlertCircle, Package, Rocket, Users, Award } from 'lucide-react';
import { getQuickWins } from '@/lib/categorization-utils';
import { Video } from '@/lib/types';

interface MetaIntelligence {
  cross_video_trends?: {
    total_unique_trends: number;
    top_trends: Array<{
      trend: string;
      frequency: number;
      stage: string;
      category: string;
      opportunities: string[];
    }>;
  };
  strategy_playbooks?: {
    total_strategy_mentions: number;
    recurring_playbooks: Array<{
      playbook_name: string;
      frequency: number;
      strategy_type: string;
    }>;
  };
  product_ecosystem?: {
    total_unique_products: number;
    total_product_mentions: number;
    most_recommended_tools: Array<{
      name: string;
      mention_count: number;
      primary_category: string;
      sentiment_score: string;
      common_use_cases: string[];
    }>;
  };
  opportunity_matrix?: {
    total_opportunities: number;
    by_type: {
      startup_ideas: number;
      market_gaps: number;
      trend_opportunities: number;
    };
    top_startup_ideas: Array<{
      title: string;
      target_market: string;
      problem_solved: string;
      business_model: string;
      validation: string;
      video_title: string;
    }>;
  };
  expert_consensus?: {
    [key: string]: {
      total_mentions: number;
      consensus_level: string;
      sentiment_distribution: {
        [key: string]: number;
      };
    };
  };
}

export default function InsightsTab() {
  const [meta, setMeta] = useState<MetaIntelligence | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('/api/meta-intelligence').then(res => res.json()),
      fetch('/api/batch').then(res => res.json())
    ]).then(([metaData, batchData]) => {
      setMeta(metaData);
      setVideos(batchData.videos || []);
      setLoading(false);
    }).catch(err => {
      console.error('Error loading insights:', err);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading insights...</div>
      </div>
    );
  }

  const quickWins = getQuickWins(videos);
  const topTrends = meta?.cross_video_trends?.top_trends?.slice(0, 5) || [];
  const topPlaybooks = meta?.strategy_playbooks?.recurring_playbooks?.slice(0, 5) || [];
  const topProducts = meta?.product_ecosystem?.most_recommended_tools?.slice(0, 8) || [];
  const topStartupIdeas = meta?.opportunity_matrix?.top_startup_ideas?.slice(0, 6) || [];

  // Calculate content performance metrics
  const videosWithDensity = videos
    .filter(v => v.enrichment && v.transcript_length)
    .map(v => ({
      ...v,
      insightDensity: ((v.enrichment?.totalInsights || 0) / ((v.transcript_length || 1) / 1000)).toFixed(2)
    }))
    .sort((a, b) => parseFloat(b.insightDensity) - parseFloat(a.insightDensity))
    .slice(0, 5);

  // Expert consensus topics
  const consensusTopics = meta?.expert_consensus ?
    Object.entries(meta.expert_consensus)
      .filter(([_, data]) => data.total_mentions > 10)
      .sort((a, b) => b[1].total_mentions - a[1].total_mentions)
      .slice(0, 5) : [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Cross-Video Intelligence</h2>
        <p className="text-gray-600">Insights and patterns discovered across all videos</p>
      </div>

      {/* Quick Wins Section */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-6 h-6 text-yellow-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Quick Wins</h3>
            <p className="text-sm text-gray-600">High-quality videos with many opportunities (>80% quality + >10 opportunities)</p>
          </div>
        </div>

        {quickWins.length === 0 ? (
          <p className="text-gray-500 text-sm">No quick wins found. Adjust thresholds or enrich more videos.</p>
        ) : (
          <div className="space-y-2">
            {quickWins.slice(0, 10).map(video => (
              <div key={video.video_id} className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-slate-800">{video.title}</h4>
                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-600">
                    <span>Quality: {video.enrichment?.avgActionability}%</span>
                    <span>"</span>
                    <span>Opportunities: {video.summary?.opportunityMap?.total_opportunities}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Top Trends Section */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <TrendingUp className="w-6 h-6 text-blue-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Top Trending Topics</h3>
            <p className="text-sm text-gray-600">{meta?.cross_video_trends?.total_unique_trends} unique trends identified</p>
          </div>
        </div>

        <div className="space-y-4">
          {topTrends.map((trend, idx) => (
            <div key={idx} className="border-b border-gray-100 pb-4 last:border-b-0">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-semibold text-slate-800">{trend.trend}</h4>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                    trend.stage === 'growing' ? 'bg-green-50 text-green-700 border border-green-200' :
                    trend.stage === 'early' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                    'bg-gray-50 text-gray-700 border border-gray-200'
                  }`}>
                    {trend.stage}
                  </span>
                  <span className="px-2 py-1 rounded-md bg-purple-50 text-purple-700 border border-purple-200 text-xs font-medium">
                    {trend.frequency} mentions
                  </span>
                </div>
              </div>
              {trend.opportunities && trend.opportunities.length > 0 && (
                <div className="space-y-1">
                  {trend.opportunities.slice(0, 2).map((opp, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-gray-600">
                      <Target className="w-3 h-3 text-purple-600 mt-0.5 flex-shrink-0" />
                      <span>{opp}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Strategy Playbooks Section */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Lightbulb className="w-6 h-6 text-amber-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Recurring Strategy Playbooks</h3>
            <p className="text-sm text-gray-600">{meta?.strategy_playbooks?.total_strategy_mentions} total strategy mentions</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {topPlaybooks.map((playbook, idx) => (
            <div key={idx} className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-semibold text-slate-800">{playbook.playbook_name}</h4>
                <span className="px-2 py-1 rounded-md bg-white text-amber-700 border border-amber-300 text-xs font-medium">
                  {playbook.frequency}x
                </span>
              </div>
              <p className="text-xs text-gray-600 capitalize">{playbook.strategy_type}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Category Analytics */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle className="w-6 h-6 text-slate-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Content Distribution</h3>
            <p className="text-sm text-gray-600">How videos are distributed by type and quality</p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-2xl font-bold text-blue-700">{videos.filter(v => v.enrichment?.videoType === 'entrepreneurship').length}</p>
            <p className="text-xs text-gray-600 mt-1">Entrepreneurship</p>
          </div>
          <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-2xl font-bold text-green-700">{videos.filter(v => v.enrichment?.videoType === 'market_research').length}</p>
            <p className="text-xs text-gray-600 mt-1">Market Research</p>
          </div>
          <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <p className="text-2xl font-bold text-purple-700">{videos.filter(v => v.enrichment && v.enrichment.avgActionability >= 80).length}</p>
            <p className="text-xs text-gray-600 mt-1">Excellent Quality</p>
          </div>
          <div className="text-center p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-2xl font-bold text-amber-700">{videos.filter(v => v.summary && v.summary.opportunityMap && v.summary.opportunityMap.total_opportunities > 10).length}</p>
            <p className="text-xs text-gray-600 mt-1">High Potential</p>
          </div>
        </div>
      </div>

      {/* Product Ecosystem */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Package className="w-6 h-6 text-indigo-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Most Recommended Tools</h3>
            <p className="text-sm text-gray-600">{meta?.product_ecosystem?.total_unique_products} unique products mentioned across {meta?.product_ecosystem?.total_product_mentions} times</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {topProducts.map((product, idx) => (
            <div key={idx} className="p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-semibold text-slate-800">{product.name}</h4>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 rounded-md bg-white text-indigo-700 border border-indigo-300 text-xs font-medium">
                    {product.mention_count} mentions
                  </span>
                  <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                    product.sentiment_score === 'highly_positive' ? 'bg-green-50 text-green-700 border border-green-200' :
                    'bg-blue-50 text-blue-700 border border-blue-200'
                  }`}>
                    {product.sentiment_score.replace('_', ' ')}
                  </span>
                </div>
              </div>
              <p className="text-xs text-gray-600 capitalize mb-2">{product.primary_category.replace(/-/g, ' ')}</p>
              {product.common_use_cases && product.common_use_cases.length > 0 && (
                <p className="text-xs text-gray-500 italic line-clamp-2">{product.common_use_cases[0]}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Opportunity Matrix */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Rocket className="w-6 h-6 text-rose-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Top Startup Opportunities</h3>
            <p className="text-sm text-gray-600">{meta?.opportunity_matrix?.total_opportunities} total opportunities ({meta?.opportunity_matrix?.by_type?.startup_ideas} ideas, {meta?.opportunity_matrix?.by_type?.market_gaps} gaps, {meta?.opportunity_matrix?.by_type?.trend_opportunities} trends)</p>
          </div>
        </div>

        <div className="space-y-4">
          {topStartupIdeas.map((idea, idx) => (
            <div key={idx} className="p-4 bg-rose-50 border border-rose-200 rounded-lg">
              <h4 className="text-sm font-semibold text-slate-800 mb-2">{idea.title}</h4>
              <div className="space-y-1 text-xs text-gray-600">
                {idea.target_market && <p><span className="font-medium">Target:</span> {idea.target_market}</p>}
                {idea.problem_solved && <p><span className="font-medium">Problem:</span> {idea.problem_solved}</p>}
                {idea.business_model && <p><span className="font-medium">Model:</span> {idea.business_model}</p>}
                {idea.validation && (
                  <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded">
                    <p className="text-green-700"><span className="font-medium">Validation:</span> {idea.validation}</p>
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-2 italic">From: {idea.video_title}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Expert Consensus */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Users className="w-6 h-6 text-teal-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Expert Consensus Topics</h3>
            <p className="text-sm text-gray-600">Topics frequently discussed with high agreement</p>
          </div>
        </div>

        <div className="space-y-3">
          {consensusTopics.map(([topic, data], idx) => {
            const totalSentiments = Object.values(data.sentiment_distribution).reduce((a, b) => a + b, 0);
            const topSentiment = Object.entries(data.sentiment_distribution).sort((a, b) => b[1] - a[1])[0];
            const sentimentPercent = totalSentiments > 0 ? ((topSentiment[1] / totalSentiments) * 100).toFixed(0) : 0;

            return (
              <div key={idx} className="p-4 bg-teal-50 border border-teal-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-slate-800 capitalize">{topic.replace(/_/g, ' ')}</h4>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 rounded-md bg-white text-teal-700 border border-teal-300 text-xs font-medium">
                      {data.total_mentions} mentions
                    </span>
                    <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                      data.consensus_level === 'high' ? 'bg-green-50 text-green-700 border border-green-200' :
                      'bg-blue-50 text-blue-700 border border-blue-200'
                    }`}>
                      {data.consensus_level} consensus
                    </span>
                  </div>
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  <span className="font-medium">{sentimentPercent}%</span> {topSentiment[0]} sentiment
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Content Performance */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Award className="w-6 h-6 text-cyan-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Highest Insight Density</h3>
            <p className="text-sm text-gray-600">Videos with the most insights per 1000 characters</p>
          </div>
        </div>

        <div className="space-y-2">
          {videosWithDensity.map((video, idx) => (
            <div key={video.video_id} className="flex items-center justify-between p-3 bg-cyan-50 border border-cyan-200 rounded-lg">
              <div className="flex-1">
                <h4 className="text-sm font-medium text-slate-800">{video.title}</h4>
                <div className="flex items-center gap-3 mt-1 text-xs text-gray-600">
                  <span>Density: {video.insightDensity} insights/1k chars</span>
                  <span>•</span>
                  <span>Total Insights: {video.enrichment?.totalInsights}</span>
                  <span>•</span>
                  <span>Quality: {video.enrichment?.avgActionability}%</span>
                </div>
              </div>
              <span className="px-3 py-1 rounded-md bg-cyan-100 text-cyan-700 border border-cyan-300 text-xs font-bold">
                #{idx + 1}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

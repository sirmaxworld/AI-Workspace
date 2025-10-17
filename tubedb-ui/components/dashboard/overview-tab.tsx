'use client';

import { useEffect, useState } from 'react';
import { Target, Sparkles, TrendingUp, Package, Rocket, Zap, ArrowRight, ExternalLink, Library } from 'lucide-react';
import Link from 'next/link';

interface MetaIntelligence {
  data_scope: {
    total_videos: number;
    total_insights: number;
  };
  cross_video_trends?: {
    top_trends: Array<{
      trend: string;
      frequency: number;
      stage: string;
      opportunities: string[];
    }>;
  };
  product_ecosystem?: {
    most_recommended_tools: Array<{
      name: string;
      mention_count: number;
      sentiment_score: string;
      common_use_cases?: string[];
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
    }>;
  };
  strategy_playbooks?: {
    recurring_playbooks: Array<{
      playbook_name: string;
      frequency: number;
      strategy_type: string;
    }>;
  };
}

export default function OverviewTab() {
  const [meta, setMeta] = useState<MetaIntelligence | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/meta-intelligence')
      .then(res => res.json())
      .then(data => {
        setMeta(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading intelligence:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading intelligence...</div>
      </div>
    );
  }

  const topTrends = meta?.cross_video_trends?.top_trends?.slice(0, 3) || [];
  const topTools = meta?.product_ecosystem?.most_recommended_tools?.slice(0, 5) || [];
  const topOpportunities = meta?.opportunity_matrix?.top_startup_ideas?.slice(0, 5) || [];
  const topPlaybooks = meta?.strategy_playbooks?.recurring_playbooks?.slice(0, 4) || [];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="glass-card bg-gradient-to-br from-slate-800 to-slate-900 p-8 text-white">
        <h1 className="text-3xl font-bold mb-3">Intelligence Dashboard</h1>
        <p className="text-slate-300 text-lg mb-6">
          Actionable insights from {meta?.data_scope.total_videos} videos and {meta?.data_scope.total_insights.toLocaleString()} data points
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
            <div className="text-3xl font-bold">{meta?.opportunity_matrix?.total_opportunities}</div>
            <div className="text-slate-300 text-sm mt-1">Total Opportunities</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
            <div className="text-3xl font-bold">{meta?.opportunity_matrix?.by_type.startup_ideas}</div>
            <div className="text-slate-300 text-sm mt-1">Startup Ideas</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
            <div className="text-3xl font-bold">{meta?.cross_video_trends?.top_trends.length}</div>
            <div className="text-slate-300 text-sm mt-1">Active Trends</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
            <div className="text-3xl font-bold">{meta?.product_ecosystem?.most_recommended_tools.length}</div>
            <div className="text-slate-300 text-sm mt-1">Recommended Tools</div>
          </div>
        </div>
      </div>

      {/* Top Opportunities */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Rocket className="w-6 h-6 text-rose-600" />
            <div>
              <h2 className="text-xl font-bold text-slate-800">Top 5 Opportunities</h2>
              <p className="text-sm text-gray-600">Validated startup ideas you can build right now</p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {topOpportunities.map((opp, idx) => (
            <div key={idx} className="p-5 bg-gradient-to-r from-rose-50 to-pink-50 border-2 border-rose-200 rounded-xl hover:shadow-lg transition-shadow">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-rose-500 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  {idx + 1}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-slate-800 mb-2">{opp.title}</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-start gap-2">
                      <Target className="w-4 h-4 text-rose-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <span className="font-semibold text-gray-700">Target Market:</span>
                        <span className="text-gray-600 ml-1">{opp.target_market}</span>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <Sparkles className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <span className="font-semibold text-gray-700">Problem:</span>
                        <span className="text-gray-600 ml-1">{opp.problem_solved}</span>
                      </div>
                    </div>
                    {opp.business_model && (
                      <div className="flex items-start gap-2">
                        <TrendingUp className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <div>
                          <span className="font-semibold text-gray-700">Model:</span>
                          <span className="text-gray-600 ml-1">{opp.business_model}</span>
                        </div>
                      </div>
                    )}
                    {opp.validation && (
                      <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <div className="font-semibold text-green-800 text-xs mb-1">✓ VALIDATION</div>
                        <div className="text-green-700 text-sm">{opp.validation}</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hot Trends */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-slate-800">Hot Trends</h2>
              <p className="text-sm text-gray-600">Ride these waves now</p>
            </div>
          </div>

          <div className="space-y-4">
            {topTrends.map((trend, idx) => (
              <div key={idx} className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-slate-800 capitalize text-lg">{trend.trend.replace(/_/g, ' ')}</h3>
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 border border-blue-300 rounded-md text-sm font-bold">
                      {trend.frequency} mentions
                    </span>
                    <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                      trend.stage === 'growing' ? 'bg-green-100 text-green-700 border border-green-300' :
                      trend.stage === 'early' ? 'bg-amber-100 text-amber-700 border border-amber-300' :
                      'bg-gray-100 text-gray-700 border border-gray-300'
                    }`}>
                      {trend.stage}
                    </span>
                  </div>
                </div>
                {trend.opportunities && trend.opportunities.length > 0 && (
                  <div className="space-y-1 mt-3">
                    {trend.opportunities.slice(0, 2).map((opp, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm text-gray-700">
                        <ArrowRight className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span>{opp}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Must-Have Tools */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Package className="w-6 h-6 text-purple-600" />
            <div>
              <h2 className="text-xl font-bold text-slate-800">Must-Have Tools</h2>
              <p className="text-sm text-gray-600">What experts actually use</p>
            </div>
          </div>

          <div className="space-y-3">
            {topTools.map((tool, idx) => (
              <div key={idx} className="p-4 bg-purple-50 border border-purple-200 rounded-lg hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-slate-800 text-lg">{tool.name}</h3>
                  <span className="px-3 py-1 bg-purple-100 text-purple-700 border border-purple-300 rounded-md text-sm font-bold">
                    {tool.mention_count} mentions
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                    tool.sentiment_score === 'highly_positive' ? 'bg-green-100 text-green-700 border border-green-300' :
                    'bg-blue-100 text-blue-700 border border-blue-300'
                  }`}>
                    {tool.sentiment_score.replace('_', ' ')}
                  </span>
                  {tool.common_use_cases && tool.common_use_cases[0] && (
                    <span className="text-sm text-gray-600 italic">{tool.common_use_cases[0]}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Strategic Playbooks */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-6 h-6 text-amber-600" />
          <div>
            <h2 className="text-xl font-bold text-slate-800">Proven Playbooks</h2>
            <p className="text-sm text-gray-600">Strategies that work across multiple experts</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {topPlaybooks.map((playbook, idx) => (
            <div key={idx} className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-slate-800">{playbook.playbook_name}</h3>
                <span className="px-2 py-1 bg-amber-100 text-amber-700 border border-amber-300 rounded-md text-xs font-bold">
                  {playbook.frequency}x
                </span>
              </div>
              <p className="text-sm text-gray-600 capitalize">{playbook.strategy_type.replace(/_/g, ' ')}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/library">
          <div className="glass-card p-6 hover:shadow-xl transition-all cursor-pointer group border-2 border-transparent hover:border-slate-300">
            <Library className="w-8 h-8 text-slate-600 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-bold text-slate-800 mb-2">Browse Video Library</h3>
            <p className="text-sm text-gray-600">Explore all {meta?.data_scope.total_videos} videos with filtering and search</p>
            <div className="flex items-center gap-2 text-sm text-slate-600 mt-3 group-hover:text-slate-800">
              <span>View Library</span>
              <ExternalLink className="w-4 h-4" />
            </div>
          </div>
        </Link>

        <div className="glass-card p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
          <Sparkles className="w-8 h-8 text-green-600 mb-3" />
          <h3 className="font-bold text-slate-800 mb-2">Quality Insights</h3>
          <p className="text-sm text-gray-600">Check the Insights tab for cross-video patterns, quick wins, and expert consensus</p>
        </div>

        <div className="glass-card p-6 bg-gradient-to-br from-indigo-50 to-blue-50 border-2 border-indigo-200">
          <TrendingUp className="w-8 h-8 text-indigo-600 mb-3" />
          <h3 className="font-bold text-slate-800 mb-2">Advanced Analytics</h3>
          <p className="text-sm text-gray-600">PhD-level analysis: opportunity scoring, trend momentum, market timing</p>
        </div>
      </div>
    </div>
  );
}

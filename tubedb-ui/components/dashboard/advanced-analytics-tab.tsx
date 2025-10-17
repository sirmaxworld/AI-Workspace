'use client';

import { useEffect, useState } from 'react';
import { ResponsiveScatterPlot } from '@nivo/scatterplot';
import { ResponsiveBubble } from '@nivo/circle-packing';
import {  Target, TrendingUp, Award, AlertTriangle, Clock, Shield } from 'lucide-react';
import { Video } from '@/lib/types';

interface MetaIntelligence {
  opportunity_matrix?: {
    total_opportunities: number;
    top_startup_ideas: any[];
  };
  cross_video_trends?: {
    top_trends: any[];
  };
  product_ecosystem?: {
    most_recommended_tools: any[];
  };
  strategy_playbooks?: {
    recurring_playbooks: any[];
  };
}

interface OpportunityScore {
  title: string;
  composite_score: number;
  validation_score: number;
  market_score: number;
  trend_score: number;
  risk_level: string;
  potential_return: string;
  timing_signal: string;
}

export default function AdvancedAnalyticsTab() {
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
      console.error('Error loading analytics data:', err);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Computing advanced analytics...</div>
      </div>
    );
  }

  // Advanced Analytics Calculations

  // 1. Opportunity Scoring Matrix
  const opportunities = meta?.opportunity_matrix?.top_startup_ideas || [];
  const trends = meta?.cross_video_trends?.top_trends || [];

  const scoredOpportunities: OpportunityScore[] = opportunities.slice(0, 20).map((opp: any) => {
    const validation_score = opp.validation && opp.validation !== 'not specified' ? 75 : 25;
    const market_score = opp.target_market && opp.target_market.length > 20 ? 70 : 30;
    const is_trending = trends.some((t: any) =>
      opp.title.toLowerCase().includes(t.trend.toLowerCase().replace(/_/g, ' '))
    );
    const trend_score = is_trending ? 80 : 40;
    const composite_score = Math.round((validation_score * 0.4 + market_score * 0.3 + trend_score * 0.3));

    return {
      title: opp.title,
      composite_score,
      validation_score,
      market_score,
      trend_score,
      risk_level: validation_score > 60 ? 'low' : validation_score > 30 ? 'medium' : 'high',
      potential_return: (opp.business_model?.includes('subscription') || opp.business_model?.includes('high-margin')) ? 'high' : 'medium',
      timing_signal: is_trending ? 'hot' : composite_score > 65 ? 'good' : 'wait'
    };
  }).sort((a, b) => b.composite_score - a.composite_score);

  // Risk/Reward Quadrants
  const quadrants = scoredOpportunities.reduce((acc, opp) => {
    const high_reward = opp.potential_return === 'high';
    const low_risk = opp.risk_level === 'low';

    if (high_reward && low_risk) acc.high_reward_low_risk++;
    else if (high_reward && !low_risk) acc.high_reward_high_risk++;
    else if (!high_reward && low_risk) acc.low_reward_low_risk++;
    else acc.low_reward_high_risk++;

    return acc;
  }, { high_reward_low_risk: 0, high_reward_high_risk: 0, low_reward_low_risk: 0, low_reward_high_risk: 0 });

  // 2. Quality-Value Scatter Plot Data
  const scatterData = videos
    .filter(v => v.enrichment && v.summary?.opportunityMap)
    .map(v => ({
      x: v.enrichment!.avgActionability,
      y: v.summary!.opportunityMap!.total_opportunities,
      title: v.title,
      insights: v.enrichment!.totalInsights
    }))
    .filter(d => d.x > 0 && d.y > 0);

  const qualityVsOpportunities = [
    {
      id: 'videos',
      data: scatterData
    }
  ];

  // Calculate correlation
  const meanQuality = scatterData.reduce((sum, v) => sum + v.x, 0) / (scatterData.length || 1);
  const meanOpps = scatterData.reduce((sum, v) => sum + v.y, 0) / (scatterData.length || 1);
  const numerator = scatterData.reduce((sum, v) => sum + (v.x - meanQuality) * (v.y - meanOpps), 0);
  const denomQuality = Math.sqrt(scatterData.reduce((sum, v) => sum + Math.pow(v.x - meanQuality, 2), 0));
  const denomOpps = Math.sqrt(scatterData.reduce((sum, v) => sum + Math.pow(v.y - meanOpps, 2), 0));
  const correlation = denomQuality * denomOpps !== 0 ? numerator / (denomQuality * denomOpps) : 0;

  // 3. Trend Momentum Analysis
  const trendMomentum = trends.slice(0, 10).map((t: any) => {
    const velocity = t.mentioned_in_videos > 0 ? t.frequency / t.mentioned_in_videos : 0;
    const stage_progression: Record<string, string> = {
      'early': 'growing',
      'growing': 'mature',
      'mature': 'declining'
    };
    const projected_stage = velocity > 1.2 ? stage_progression[t.stage] || t.stage : t.stage;

    let entry_timing = 'monitor';
    if (t.stage === 'early' && velocity > 1) entry_timing = 'optimal';
    else if (t.stage === 'growing') entry_timing = 'good';
    else if (t.stage === 'mature') entry_timing = 'late';

    return {
      trend: t.trend,
      velocity: velocity.toFixed(2),
      stage: t.stage,
      projected_stage,
      entry_timing,
      frequency: t.frequency
    };
  }).sort((a, b) => parseFloat(b.velocity) - parseFloat(a.velocity));

  // 4. Strategy Success Patterns
  const playbooks = meta?.strategy_playbooks?.recurring_playbooks || [];
  const by_type: Record<string, any[]> = {};
  playbooks.forEach((pb: any) => {
    if (!by_type[pb.strategy_type]) by_type[pb.strategy_type] = [];
    by_type[pb.strategy_type].push(pb);
  });

  const strategyEffectiveness = Object.entries(by_type).map(([type, strats]) => {
    const total_freq = strats.reduce((sum: number, s: any) => sum + s.frequency, 0);
    const has_outcomes = strats.some((s: any) => s.expected_outcomes && s.expected_outcomes.length > 0);

    return {
      strategy_type: type,
      avg_outcome_quality: has_outcomes ? 75 : 50,
      frequency: total_freq,
      case_study_count: strats.reduce((sum: number, s: any) => sum + (s.case_studies?.length || 0), 0),
      success_indicator: Math.min(95, 60 + (total_freq / 2))
    };
  }).sort((a, b) => b.success_indicator - a.success_indicator);

  // 5. Market Timing Indicators
  const marketTiming = scoredOpportunities.slice(0, 10).map(opp => {
    const maturity_level = opp.validation_score;
    const competition_level = maturity_level > 70 ? 'high' : maturity_level > 40 ? 'medium' : 'low';

    let window_status = 'open';
    if (maturity_level > 70) window_status = 'closing';
    else if (opp.timing_signal === 'hot' && maturity_level < 40) window_status = 'opening';

    let recommended_action = 'research';
    if (window_status === 'opening' && competition_level === 'low') recommended_action = 'move_fast';
    else if (window_status === 'open' && competition_level === 'medium') recommended_action = 'validate';
    else if (window_status === 'closing') recommended_action = 'differentiate';

    return {
      opportunity: opp.title,
      maturity_level,
      competition_level,
      window_status,
      recommended_action,
      timing_signal: opp.timing_signal
    };
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Advanced Intelligence Analytics</h2>
        <p className="text-gray-600">PhD-level insights derived from multi-dimensional data analysis</p>
      </div>

      {/* Opportunity Risk/Reward Matrix */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-6 h-6 text-purple-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Opportunity Risk/Reward Matrix</h3>
            <p className="text-sm text-gray-600">Multi-factor scoring: validation × market × trend alignment</p>
          </div>
        </div>

        {/* Quadrant Summary */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="p-4 bg-green-50 border-2 border-green-300 rounded-lg">
            <div className="text-center">
              <p className="text-3xl font-bold text-green-700">{quadrants.high_reward_low_risk}</p>
              <p className="text-sm text-gray-600 mt-1">High Reward / Low Risk</p>
              <p className="text-xs text-green-600 font-medium mt-2">🎯 Prime Opportunities</p>
            </div>
          </div>
          <div className="p-4 bg-amber-50 border-2 border-amber-300 rounded-lg">
            <div className="text-center">
              <p className="text-3xl font-bold text-amber-700">{quadrants.high_reward_high_risk}</p>
              <p className="text-sm text-gray-600 mt-1">High Reward / High Risk</p>
              <p className="text-xs text-amber-600 font-medium mt-2">⚡ High Stakes Plays</p>
            </div>
          </div>
          <div className="p-4 bg-blue-50 border-2 border-blue-300 rounded-lg">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-700">{quadrants.low_reward_low_risk}</p>
              <p className="text-sm text-gray-600 mt-1">Low Reward / Low Risk</p>
              <p className="text-xs text-blue-600 font-medium mt-2">🛡️ Safe Bets</p>
            </div>
          </div>
          <div className="p-4 bg-red-50 border-2 border-red-300 rounded-lg">
            <div className="text-center">
              <p className="text-3xl font-bold text-red-700">{quadrants.low_reward_high_risk}</p>
              <p className="text-sm text-gray-600 mt-1">Low Reward / High Risk</p>
              <p className="text-xs text-red-600 font-medium mt-2">⚠️ Avoid</p>
            </div>
          </div>
        </div>

        {/* Top Scored Opportunities */}
        <div className="space-y-2">
          <h4 className="font-semibold text-slate-800 mb-3">Top Scored Opportunities</h4>
          {scoredOpportunities.slice(0, 5).map((opp, idx) => (
            <div key={idx} className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h5 className="text-sm font-semibold text-slate-800 flex-1">{opp.title}</h5>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-md bg-purple-100 text-purple-700 border border-purple-300 text-sm font-bold">
                    Score: {opp.composite_score}
                  </span>
                  <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                    opp.timing_signal === 'hot' ? 'bg-red-100 text-red-700 border border-red-300' :
                    opp.timing_signal === 'good' ? 'bg-green-100 text-green-700 border border-green-300' :
                    'bg-gray-100 text-gray-700 border border-gray-300'
                  }`}>
                    {opp.timing_signal}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-600">
                <span>Validation: {opp.validation_score}/100</span>
                <span>•</span>
                <span>Market: {opp.market_score}/100</span>
                <span>•</span>
                <span>Trend: {opp.trend_score}/100</span>
                <span>•</span>
                <span className={`font-medium ${
                  opp.risk_level === 'low' ? 'text-green-600' :
                  opp.risk_level === 'medium' ? 'text-amber-600' :
                  'text-red-600'
                }`}>
                  Risk: {opp.risk_level}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quality vs Opportunities Correlation */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Award className="w-6 h-6 text-indigo-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Quality-Value Correlation Analysis</h3>
            <p className="text-sm text-gray-600">Correlation coefficient: {correlation.toFixed(3)} ({Math.abs(correlation) > 0.5 ? 'Strong' : Math.abs(correlation) > 0.3 ? 'Moderate' : 'Weak'} {correlation > 0 ? 'positive' : 'negative'} correlation)</p>
          </div>
        </div>

        <div className="h-[400px] bg-white rounded-lg p-4 border border-gray-200">
          <ResponsiveScatterPlot
            data={qualityVsOpportunities}
            margin={{ top: 30, right: 30, bottom: 70, left: 70 }}
            xScale={{ type: 'linear', min: 0, max: 100 }}
            yScale={{ type: 'linear', min: 0, max: 'auto' }}
            axisBottom={{
              legend: 'Content Quality (Actionability Score)',
              legendPosition: 'middle',
              legendOffset: 46
            }}
            axisLeft={{
              legend: 'Total Opportunities',
              legendPosition: 'middle',
              legendOffset: -50
            }}
            colors={{ scheme: 'nivo' }}
            nodeSize={10}
            tooltip={({ node }) => (
              <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
                <p className="text-xs font-semibold text-slate-800 max-w-xs">{node.data.title}</p>
                <p className="text-xs text-gray-600 mt-1">Quality: {node.data.x}%</p>
                <p className="text-xs text-gray-600">Opportunities: {node.data.y}</p>
                <p className="text-xs text-gray-600">Insights: {node.data.insights}</p>
              </div>
            )}
          />
        </div>
      </div>

      {/* Trend Momentum Dashboard */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <TrendingUp className="w-6 h-6 text-cyan-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Trend Momentum & Timing Signals</h3>
            <p className="text-sm text-gray-600">Growth velocity and optimal entry timing analysis</p>
          </div>
        </div>

        <div className="space-y-2">
          {trendMomentum.map((t, idx) => (
            <div key={idx} className="p-4 bg-cyan-50 border border-cyan-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h5 className="text-sm font-semibold text-slate-800 capitalize">{t.trend.replace(/_/g, ' ')}</h5>
                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-600">
                    <span>Velocity: {t.velocity}x</span>
                    <span>•</span>
                    <span>Stage: {t.stage} → {t.projected_stage}</span>
                    <span>•</span>
                    <span>{t.frequency} mentions</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-600" />
                  <span className={`px-3 py-1 rounded-md text-xs font-medium ${
                    t.entry_timing === 'optimal' ? 'bg-green-100 text-green-700 border border-green-300' :
                    t.entry_timing === 'good' ? 'bg-blue-100 text-blue-700 border border-blue-300' :
                    t.entry_timing === 'late' ? 'bg-amber-100 text-amber-700 border border-amber-300' :
                    'bg-gray-100 text-gray-700 border border-gray-300'
                  }`}>
                    {t.entry_timing}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strategy Success Patterns */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-6 h-6 text-teal-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Strategy Success Correlation</h3>
            <p className="text-sm text-gray-600">Which strategies show highest success indicators</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {strategyEffectiveness.map((strategy, idx) => (
            <div key={idx} className="p-4 bg-teal-50 border border-teal-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h5 className="text-sm font-semibold text-slate-800 capitalize">{strategy.strategy_type.replace(/_/g, ' ')}</h5>
                <span className="px-2 py-1 rounded-md bg-teal-100 text-teal-700 border border-teal-300 text-xs font-bold">
                  {Math.round(strategy.success_indicator)}% success
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-gray-600">
                <span>{strategy.frequency} mentions</span>
                <span>•</span>
                <span>{strategy.case_study_count} case studies</span>
              </div>
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-teal-500 h-2 rounded-full transition-all"
                    style={{ width: `${strategy.success_indicator}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Market Timing Indicators */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="w-6 h-6 text-orange-600" />
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Market Timing Intelligence</h3>
            <p className="text-sm text-gray-600">Emerging vs saturated opportunities & first-mover windows</p>
          </div>
        </div>

        <div className="space-y-2">
          {marketTiming.map((market, idx) => (
            <div key={idx} className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h5 className="text-sm font-semibold text-slate-800">{market.opportunity}</h5>
                  <div className="flex items-center gap-3 mt-2 text-xs">
                    <span className={`px-2 py-1 rounded-md font-medium ${
                      market.competition_level === 'low' ? 'bg-green-100 text-green-700 border border-green-300' :
                      market.competition_level === 'medium' ? 'bg-amber-100 text-amber-700 border border-amber-300' :
                      'bg-red-100 text-red-700 border border-red-300'
                    }`}>
                      Competition: {market.competition_level}
                    </span>
                    <span className={`px-2 py-1 rounded-md font-medium ${
                      market.window_status === 'opening' ? 'bg-green-100 text-green-700 border border-green-300' :
                      market.window_status === 'open' ? 'bg-blue-100 text-blue-700 border border-blue-300' :
                      'bg-red-100 text-red-700 border border-red-300'
                    }`}>
                      Window: {market.window_status}
                    </span>
                    <span className={`px-2 py-1 rounded-md font-medium ${
                      market.recommended_action === 'move_fast' ? 'bg-green-100 text-green-700 border border-green-300' :
                      market.recommended_action === 'validate' ? 'bg-blue-100 text-blue-700 border border-blue-300' :
                      market.recommended_action === 'differentiate' ? 'bg-amber-100 text-amber-700 border border-amber-300' :
                      'bg-gray-100 text-gray-700 border border-gray-300'
                    }`}>
                      Action: {market.recommended_action.replace(/_/g, ' ')}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

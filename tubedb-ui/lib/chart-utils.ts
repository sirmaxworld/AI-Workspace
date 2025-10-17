import { Video } from './types';

// Transform video data for quality heatmap
export function transformToQualityHeatmap(videos: Video[]) {
  return videos
    .filter(v => v.enrichment)
    .slice(0, 50) // Top 50 videos
    .map(video => ({
      videoId: video.video_id,
      title: video.title.substring(0, 40) + (video.title.length > 40 ? '...' : ''),
      actionability: Math.round(video.enrichment!.avgActionability),
      specificity: Math.round(video.enrichment!.avgSpecificity),
      evidence: Math.round(video.enrichment!.avgEvidence),
      recency: Math.round(video.enrichment!.avgRecency),
    }));
}

// Transform video data for insight distribution treemap
export function transformToInsightTreemap(videos: Video[]) {
  const insightCounts: { [key: string]: number } = {
    products: 0,
    ideas: 0,
    trends: 0,
    problems: 0,
    tactics: 0,
    workflows: 0,
    strategies: 0,
    quotes: 0,
    statistics: 0,
  };

  videos.forEach(video => {
    if (video.insights) {
      Object.entries(video.insights).forEach(([key, value]) => {
        if (key in insightCounts) {
          insightCounts[key] += value || 0;
        }
      });
    }
  });

  return {
    name: 'insights',
    children: Object.entries(insightCounts)
      .filter(([_, count]) => count > 0)
      .map(([type, count]) => ({
        name: type.charAt(0).toUpperCase() + type.slice(1),
        value: count,
        loc: count,
      })),
  };
}

// Transform video data for trend analysis
export function transformToTrendData(videos: Video[]) {
  const trendCounts: { [key: string]: number } = {};

  videos.forEach(video => {
    if (video.insights?.trends) {
      trendCounts['Trends'] = (trendCounts['Trends'] || 0) + video.insights.trends;
    }
  });

  return Object.entries(trendCounts).map(([trend, count]) => ({
    trend,
    count,
  }));
}

// Transform video data for opportunity chart
export function transformToOpportunityData(videos: Video[]) {
  const opportunityTypes = {
    startup_ideas: 0,
    market_gaps: 0,
    trend_opportunities: 0,
  };

  videos.forEach(video => {
    if (video.summary?.opportunityMap) {
      const map = video.summary.opportunityMap;
      if (map.by_type) {
        opportunityTypes.startup_ideas += map.by_type.startup_ideas || 0;
        opportunityTypes.market_gaps += map.by_type.market_gaps || 0;
        opportunityTypes.trend_opportunities += map.by_type.trend_opportunities || 0;
      }
    }
  });

  return [
    { id: 'Startup Ideas', value: opportunityTypes.startup_ideas, label: 'Startup Ideas' },
    { id: 'Market Gaps', value: opportunityTypes.market_gaps, label: 'Market Gaps' },
    { id: 'Trend Opportunities', value: opportunityTypes.trend_opportunities, label: 'Trend Opportunities' },
  ];
}

// Transform video data for video type radar chart
export function transformToVideoTypeRadar(video: Video | null) {
  if (!video || !video.enrichment) {
    return [];
  }

  const typeScores = [
    { metric: 'Entrepreneurship', value: 0 },
    { metric: 'Tutorial', value: 0 },
    { metric: 'Interview', value: 0 },
    { metric: 'Case Study', value: 0 },
    { metric: 'Market Research', value: 0 },
  ];

  // Use video type confidence as base value
  const primaryType = video.enrichment.videoType;
  const confidence = video.enrichment.typeConfidence * 100;

  // Map primary type to index
  const typeMap: { [key: string]: number } = {
    entrepreneurship: 0,
    tutorial: 1,
    interview: 2,
    case_study: 3,
    market_research: 4,
  };

  const index = typeMap[primaryType];
  if (index !== undefined) {
    typeScores[index].value = confidence;
  }

  return typeScores;
}

// Transform video data for quality distribution
export function transformToQualityDistribution(videos: Video[]) {
  const ranges = {
    'Excellent (80-100)': 0,
    'Good (60-79)': 0,
    'Average (40-59)': 0,
    'Below Average (20-39)': 0,
    'Poor (0-19)': 0,
  };

  videos.forEach(video => {
    if (video.enrichment) {
      const score = video.enrichment.avgActionability;
      if (score >= 80) ranges['Excellent (80-100)']++;
      else if (score >= 60) ranges['Good (60-79)']++;
      else if (score >= 40) ranges['Average (40-59)']++;
      else if (score >= 20) ranges['Below Average (20-39)']++;
      else ranges['Poor (0-19)']++;
    }
  });

  return Object.entries(ranges).map(([range, count]) => ({
    id: range,
    label: range,
    value: count,
  }));
}

// Get top N videos by a specific metric
export function getTopVideosByMetric(
  videos: Video[],
  metric: 'opportunities' | 'actionability' | 'highValueInsights',
  limit: number = 10
) {
  const sorted = videos
    .filter(v => v.enrichment || v.summary)
    .map(video => {
      let value = 0;
      if (metric === 'opportunities') {
        value = video.summary?.opportunityMap?.total_opportunities || 0;
      } else if (metric === 'actionability') {
        value = video.enrichment?.avgActionability || 0;
      } else if (metric === 'highValueInsights') {
        value = video.enrichment?.highValueInsights || 0;
      }
      return { video, value };
    })
    .sort((a, b) => b.value - a.value)
    .slice(0, limit);

  return sorted.map(({ video, value }) => ({
    title: video.title.substring(0, 30) + (video.title.length > 30 ? '...' : ''),
    value,
    videoId: video.video_id,
  }));
}

// Calculate correlation between two metrics
export function calculateCorrelation(videos: Video[], metric1: string, metric2: string): number {
  const pairs = videos
    .filter(v => v.enrichment)
    .map(v => {
      const enrichment = v.enrichment!;
      return {
        x: (enrichment as any)[metric1] || 0,
        y: (enrichment as any)[metric2] || 0,
      };
    });

  if (pairs.length === 0) return 0;

  const meanX = pairs.reduce((sum, p) => sum + p.x, 0) / pairs.length;
  const meanY = pairs.reduce((sum, p) => sum + p.y, 0) / pairs.length;

  let numerator = 0;
  let denomX = 0;
  let denomY = 0;

  pairs.forEach(p => {
    const dx = p.x - meanX;
    const dy = p.y - meanY;
    numerator += dx * dy;
    denomX += dx * dx;
    denomY += dy * dy;
  });

  if (denomX === 0 || denomY === 0) return 0;

  return numerator / Math.sqrt(denomX * denomY);
}

// Get low quality videos (for QC tab)
export function getLowQualityVideos(videos: Video[], threshold: number = 20) {
  return videos
    .filter(v => v.enrichment && v.enrichment.avgActionability < threshold)
    .map(video => ({
      videoId: video.video_id,
      title: video.title,
      actionability: Math.round(video.enrichment!.avgActionability),
      specificity: Math.round(video.enrichment!.avgSpecificity),
      evidence: Math.round(video.enrichment!.avgEvidence),
      insights: video.enrichment!.totalInsights,
    }))
    .sort((a, b) => a.actionability - b.actionability);
}

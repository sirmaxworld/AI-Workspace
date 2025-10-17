import { Video } from './types';

export type GroupingMethod = 'type' | 'quality' | 'opportunities' | 'insightType';
export type SortOption = 'quality' | 'opportunities' | 'date' | 'title';

export interface VideoCategory {
  name: string;
  videos: Video[];
  count: number;
  avgQuality: number;
  totalOpportunities: number;
  highValueCount: number;
}

// Group videos by video type
export function groupVideosByType(videos: Video[]): VideoCategory[] {
  const grouped: { [key: string]: Video[] } = {};

  videos.forEach(video => {
    const type = video.enrichment?.videoType || 'uncategorized';
    if (!grouped[type]) {
      grouped[type] = [];
    }
    grouped[type].push(video);
  });

  return Object.entries(grouped).map(([type, vids]) => ({
    name: formatCategoryName(type),
    videos: vids,
    count: vids.length,
    ...calculateCategoryStats(vids),
  })).sort((a, b) => b.count - a.count);
}

// Group videos by quality tier
export function groupVideosByQuality(videos: Video[]): VideoCategory[] {
  const tiers = {
    'Excellent (80-100%)': [] as Video[],
    'Good (60-79%)': [] as Video[],
    'Average (40-59%)': [] as Video[],
    'Below Average (20-39%)': [] as Video[],
    'Needs Review (<20%)': [] as Video[],
  };

  videos.forEach(video => {
    if (!video.enrichment) return;

    const quality = video.enrichment.avgActionability;
    if (quality >= 80) tiers['Excellent (80-100%)'].push(video);
    else if (quality >= 60) tiers['Good (60-79%)'].push(video);
    else if (quality >= 40) tiers['Average (40-59%)'].push(video);
    else if (quality >= 20) tiers['Below Average (20-39%)'].push(video);
    else tiers['Needs Review (<20%)'].push(video);
  });

  return Object.entries(tiers)
    .filter(([_, vids]) => vids.length > 0)
    .map(([tier, vids]) => ({
      name: tier,
      videos: vids,
      count: vids.length,
      ...calculateCategoryStats(vids),
    }));
}

// Group videos by opportunity level
export function groupVideosByOpportunities(videos: Video[]): VideoCategory[] {
  const levels = {
    'High Potential (>10 opps)': [] as Video[],
    'Medium Potential (5-10 opps)': [] as Video[],
    'Low Potential (1-4 opps)': [] as Video[],
    'No Opportunities': [] as Video[],
  };

  videos.forEach(video => {
    const opps = video.summary?.opportunityMap?.total_opportunities || 0;
    if (opps > 10) levels['High Potential (>10 opps)'].push(video);
    else if (opps >= 5) levels['Medium Potential (5-10 opps)'].push(video);
    else if (opps >= 1) levels['Low Potential (1-4 opps)'].push(video);
    else levels['No Opportunities'].push(video);
  });

  return Object.entries(levels)
    .filter(([_, vids]) => vids.length > 0)
    .map(([level, vids]) => ({
      name: level,
      videos: vids,
      count: vids.length,
      ...calculateCategoryStats(vids),
    }));
}

// Group videos by primary insight type
export function groupVideosByInsightType(videos: Video[]): VideoCategory[] {
  const types = {
    'Product-Focused': [] as Video[],
    'Trend-Focused': [] as Video[],
    'Strategy-Focused': [] as Video[],
    'Idea-Focused': [] as Video[],
    'Mixed Content': [] as Video[],
  };

  videos.forEach(video => {
    if (!video.insights) {
      types['Mixed Content'].push(video);
      return;
    }

    const { products = 0, trends = 0, strategies = 0, ideas = 0 } = video.insights;
    const max = Math.max(products, trends, strategies, ideas);

    if (max === 0) {
      types['Mixed Content'].push(video);
    } else if (products === max) {
      types['Product-Focused'].push(video);
    } else if (trends === max) {
      types['Trend-Focused'].push(video);
    } else if (strategies === max) {
      types['Strategy-Focused'].push(video);
    } else if (ideas === max) {
      types['Idea-Focused'].push(video);
    } else {
      types['Mixed Content'].push(video);
    }
  });

  return Object.entries(types)
    .filter(([_, vids]) => vids.length > 0)
    .map(([type, vids]) => ({
      name: type,
      videos: vids,
      count: vids.length,
      ...calculateCategoryStats(vids),
    }))
    .sort((a, b) => b.count - a.count);
}

// Calculate aggregate stats for a category
function calculateCategoryStats(videos: Video[]) {
  const enrichedVideos = videos.filter(v => v.enrichment);

  const avgQuality = enrichedVideos.length > 0
    ? enrichedVideos.reduce((sum, v) => sum + (v.enrichment!.avgActionability || 0), 0) / enrichedVideos.length
    : 0;

  const totalOpportunities = videos.reduce((sum, v) =>
    sum + (v.summary?.opportunityMap?.total_opportunities || 0), 0
  );

  const highValueCount = videos.reduce((sum, v) =>
    sum + (v.enrichment?.highValueInsights || 0), 0
  );

  return {
    avgQuality: Math.round(avgQuality),
    totalOpportunities,
    highValueCount,
  };
}

// Sort videos within a category
export function sortVideos(videos: Video[], sortBy: SortOption): Video[] {
  const sorted = [...videos];

  switch (sortBy) {
    case 'quality':
      return sorted.sort((a, b) =>
        (b.enrichment?.avgActionability || 0) - (a.enrichment?.avgActionability || 0)
      );
    case 'opportunities':
      return sorted.sort((a, b) =>
        (b.summary?.opportunityMap?.total_opportunities || 0) -
        (a.summary?.opportunityMap?.total_opportunities || 0)
      );
    case 'date':
      return sorted.sort((a, b) =>
        new Date(b.extracted_at || 0).getTime() - new Date(a.extracted_at || 0).getTime()
      );
    case 'title':
      return sorted.sort((a, b) => a.title.localeCompare(b.title));
    default:
      return sorted;
  }
}

// Format category names for display
function formatCategoryName(name: string): string {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Filter videos by search query
export function filterVideosBySearch(videos: Video[], query: string): Video[] {
  if (!query.trim()) return videos;

  const lowerQuery = query.toLowerCase();
  return videos.filter(video =>
    video.title.toLowerCase().includes(lowerQuery) ||
    video.enrichment?.videoType.toLowerCase().includes(lowerQuery) ||
    video.featured_products?.some(p => p.name.toLowerCase().includes(lowerQuery)) ||
    video.featured_ideas?.some(i => i.idea.toLowerCase().includes(lowerQuery))
  );
}

// Get quick wins (high quality + high opportunities)
export function getQuickWins(videos: Video[], minQuality: number = 80, minOpps: number = 10): Video[] {
  return videos.filter(video =>
    video.enrichment &&
    video.enrichment.avgActionability >= minQuality &&
    (video.summary?.opportunityMap?.total_opportunities || 0) >= minOpps
  );
}

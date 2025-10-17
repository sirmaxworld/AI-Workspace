export interface TranscriptSegment {
  text: string;
  start: number;
  duration: number;
}

export interface Transcript {
  language?: string;
  segments?: TranscriptSegment[];
  segment_count?: number;
}

export interface QCVerification {
  quality_score: number;
  key_topics: string[];
  summary: string;
  verifier?: string;
}

export interface InsightCounts {
  products: number;
  ideas: number;
  problems: number;
  trends: number;
  tactics: number;
  workflows: number;
  strategies: number;
  quotes: number;
  statistics: number;
}

export interface Product {
  name: string;
  category?: string;
  use_case?: string;
  sentiment?: string;
  pricing?: string;
  metrics?: string;
}

export interface StartupIdea {
  idea: string;
  target_market?: string;
  problem_solved?: string;
  business_model?: string;
}

export interface EnrichedMetrics {
  avgActionability: number;
  avgSpecificity: number;
  avgEvidence: number;
  avgRecency: number;
  highValueInsights: number;
  totalInsights: number;
  videoType: string;
  typeConfidence: number;
}

export interface ContentProfile {
  title?: string;
  video_type?: string;
  type_confidence?: number;
  primary_themes?: string[];
  experience_level?: string;
  industry_focus?: string[];
  content_density?: number;
}

export interface OpportunityMap {
  total_opportunities: number;
  by_type: {
    startup_ideas?: number;
    market_gaps?: number;
    trend_opportunities?: number;
  };
  opportunities?: {
    startup_ideas?: any[];
    market_gaps?: any[];
    trend_opportunities?: any[];
  };
}

export interface VideoSummary {
  contentProfile: ContentProfile | null;
  keyTakeaways: string[];
  standoutInsights: any[];
  opportunityMap: OpportunityMap | null;
  practicalNextSteps: string[];
  metricsummary: any;
}

export interface Video {
  video_id: string;
  title: string;
  agent_id?: number;
  method?: string;
  extracted_at?: string;
  transcript_length?: number;
  hasTranscript?: boolean;
  insights?: InsightCounts;
  featured_products?: Product[];
  featured_ideas?: StartupIdea[];
  transcript?: Transcript | null;
  qc_verification?: QCVerification;
  enrichment?: EnrichedMetrics | null;
  summary?: VideoSummary | null;
}

export interface BatchData {
  filename: string;
  videos: Video[];
  video_count: number;
  timestamp: string;
}

export interface SystemStats {
  totalVideos: number;
  totalSegments: number;
  avgQualityScore: number;
  processingTime: number;
  totalOpportunities?: number;
  totalHighValueInsights?: number;
  avgActionability?: number;
  enrichedCount?: number;
}

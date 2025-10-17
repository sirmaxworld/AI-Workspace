// Configuration for the application
export const config = {
  // Data source configuration
  dataPath: process.env.DATA_PATH || '/Users/yourox/AI-Workspace/data/transcripts',
  transcriptsDir: '/Users/yourox/AI-Workspace/data/transcripts',

  // API configuration
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || '',

  // Feature flags
  features: {
    videoModal: true,
    qcTab: true,
    analyticsTab: true,
    rawDataTab: true,
    researchTab: false, // Coming soon
  },

  // Display settings
  display: {
    videosPerPage: 50,
    defaultTab: 'overview',
  },
} as const;

export type Config = typeof config;

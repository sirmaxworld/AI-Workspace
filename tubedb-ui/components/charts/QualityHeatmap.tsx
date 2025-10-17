'use client';

import { HeatMapGrid } from 'react-grid-heatmap';

interface HeatmapData {
  videoId: string;
  title: string;
  actionability: number;
  specificity: number;
  evidence: number;
  recency: number;
}

interface QualityHeatmapProps {
  data: HeatmapData[];
}

export default function QualityHeatmap({ data }: QualityHeatmapProps) {
  const xLabels = ['Actionability', 'Specificity', 'Evidence', 'Recency'];
  const yLabels = data.map(d => d.title);

  // Transform data into 2D array for heatmap
  const heatmapData = data.map(video => [
    video.actionability,
    video.specificity,
    video.evidence,
    video.recency,
  ]);

  // Color scale function: 0-100 range
  const getColor = (value: number) => {
    if (value >= 80) return '#10b981'; // green-500
    if (value >= 60) return '#3b82f6'; // blue-500
    if (value >= 40) return '#f59e0b'; // amber-500
    if (value >= 20) return '#f97316'; // orange-500
    return '#ef4444'; // red-500
  };

  return (
    <div className="w-full h-full">
      <HeatMapGrid
        data={heatmapData}
        xLabels={xLabels}
        yLabels={yLabels}
        cellStyle={(x, y, value) => ({
          background: getColor(value),
          fontSize: '11px',
          color: value > 50 ? '#fff' : '#000',
          border: '1px solid #e5e7eb',
        })}
        cellRender={(value) => value && <div>{value}</div>}
        xLabelsStyle={() => ({
          color: '#1f2937',
          fontSize: '0.75rem',
          fontWeight: '600',
        })}
        yLabelsStyle={() => ({
          fontSize: '0.7rem',
          color: '#4b5563',
          marginRight: '8px',
        })}
        square
      />
    </div>
  );
}

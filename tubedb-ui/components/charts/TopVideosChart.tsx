'use client';

import { ResponsiveBar } from '@nivo/bar';

interface VideoData {
  title: string;
  value: number;
  videoId: string;
}

interface TopVideosChartProps {
  data: VideoData[];
  metric: string;
}

export default function TopVideosChart({ data, metric }: TopVideosChartProps) {
  return (
    <div className="w-full h-full">
      <ResponsiveBar
        data={data}
        keys={['value']}
        indexBy="title"
        margin={{ top: 20, right: 30, bottom: 60, left: 200 }}
        padding={0.3}
        layout="horizontal"
        valueScale={{ type: 'linear' }}
        colors={['#8b5cf6']}
        borderColor="#e5e7eb"
        axisTop={null}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: metric,
          legendPosition: 'middle',
          legendOffset: 40,
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
        }}
        enableLabel={true}
        labelSkipWidth={12}
        labelSkipHeight={12}
        labelTextColor="#fff"
        animate={true}
        motionConfig="gentle"
      />
    </div>
  );
}

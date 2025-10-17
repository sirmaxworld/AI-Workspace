'use client';

import { ResponsiveBar } from '@nivo/bar';

interface TrendData {
  trend: string;
  count: number;
}

interface TrendAnalysisProps {
  data: TrendData[];
}

export default function TrendAnalysis({ data }: TrendAnalysisProps) {
  return (
    <div className="w-full h-full">
      <ResponsiveBar
        data={data}
        keys={['count']}
        indexBy="trend"
        margin={{ top: 20, right: 30, bottom: 60, left: 60 }}
        padding={0.3}
        layout="horizontal"
        valueScale={{ type: 'linear' }}
        colors={['#3b82f6']}
        borderColor="#e5e7eb"
        axisTop={null}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Count',
          legendPosition: 'middle',
          legendOffset: 40,
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Trend',
          legendPosition: 'middle',
          legendOffset: -50,
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

'use client';

import { ResponsiveBar } from '@nivo/bar';

interface DistributionData {
  id: string;
  label: string;
  value: number;
}

interface QualityDistributionProps {
  data: DistributionData[];
}

export default function QualityDistribution({ data }: QualityDistributionProps) {
  return (
    <div className="w-full h-full">
      <ResponsiveBar
        data={data}
        keys={['value']}
        indexBy="id"
        margin={{ top: 20, right: 30, bottom: 80, left: 60 }}
        padding={0.3}
        valueScale={{ type: 'linear' }}
        colors={['#10b981', '#3b82f6', '#f59e0b', '#f97316', '#ef4444']}
        borderColor="#e5e7eb"
        axisTop={null}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: -45,
          legend: 'Quality Score Range',
          legendPosition: 'middle',
          legendOffset: 60,
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Number of Videos',
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

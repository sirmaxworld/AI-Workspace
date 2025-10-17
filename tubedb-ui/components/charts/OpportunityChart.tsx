'use client';

import { ResponsivePie } from '@nivo/pie';

interface OpportunityData {
  id: string;
  value: number;
  label: string;
}

interface OpportunityChartProps {
  data: OpportunityData[];
}

export default function OpportunityChart({ data }: OpportunityChartProps) {
  return (
    <div className="w-full h-full">
      <ResponsivePie
        data={data}
        margin={{ top: 40, right: 80, bottom: 80, left: 80 }}
        innerRadius={0.5}
        padAngle={0.7}
        cornerRadius={3}
        activeOuterRadiusOffset={8}
        colors={{ scheme: 'set3' }}
        borderWidth={1}
        borderColor="#e5e7eb"
        arcLinkLabelsSkipAngle={10}
        arcLinkLabelsTextColor="#1f2937"
        arcLinkLabelsThickness={2}
        arcLinkLabelsColor={{ from: 'color' }}
        arcLabelsSkipAngle={10}
        arcLabelsTextColor="#1f2937"
        valueFormat={(value) => `${value}`}
        legends={[
          {
            anchor: 'bottom',
            direction: 'row',
            justify: false,
            translateX: 0,
            translateY: 56,
            itemsSpacing: 0,
            itemWidth: 120,
            itemHeight: 18,
            itemTextColor: '#4b5563',
            itemDirection: 'left-to-right',
            itemOpacity: 1,
            symbolSize: 12,
            symbolShape: 'circle',
          },
        ]}
        animate={true}
        motionConfig="gentle"
      />
    </div>
  );
}

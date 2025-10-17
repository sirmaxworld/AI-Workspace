'use client';

import { ResponsiveTreeMap } from '@nivo/treemap';

interface TreemapData {
  name: string;
  children?: Array<{
    name: string;
    value: number;
    loc: number;
  }>;
}

interface InsightTreemapProps {
  data: TreemapData;
}

export default function InsightTreemap({ data }: InsightTreemapProps) {
  return (
    <div className="w-full h-full">
      <ResponsiveTreeMap
        data={data}
        identity="name"
        value="loc"
        valueFormat=".0f"
        margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
        labelSkipSize={12}
        labelTextColor="#1f2937"
        parentLabelSize={16}
        parentLabelTextColor="#1f2937"
        colors={{ scheme: 'blues' }}
        borderColor="#e5e7eb"
        borderWidth={2}
        enableParentLabel={true}
        animate={true}
        motionConfig="gentle"
        label={(node) => `${node.id}: ${node.value}`}
        labelTextColor={{
          from: 'color',
          modifiers: [['darker', 2]],
        }}
      />
    </div>
  );
}

'use client';

import { ResponsiveRadar } from '@nivo/radar';

interface RadarData {
  metric: string;
  value: number;
}

interface VideoTypeRadarProps {
  data: RadarData[];
}

export default function VideoTypeRadar({ data }: VideoTypeRadarProps) {
  return (
    <div className="w-full h-full">
      <ResponsiveRadar
        data={data}
        keys={['value']}
        indexBy="metric"
        maxValue={100}
        margin={{ top: 70, right: 80, bottom: 40, left: 80 }}
        borderColor="#e5e7eb"
        gridLabelOffset={16}
        dotSize={8}
        dotColor="#3b82f6"
        dotBorderWidth={2}
        dotBorderColor="#fff"
        enableDotLabel={true}
        colors={['#3b82f6']}
        fillOpacity={0.25}
        blendMode="multiply"
        animate={true}
        motionConfig="gentle"
        gridLabel={(props) => (
          <text
            x={props.x}
            y={props.y}
            dy={4}
            textAnchor={props.anchor}
            style={{
              fill: '#4b5563',
              fontSize: '11px',
              fontWeight: '600',
            }}
          >
            {props.id}
          </text>
        )}
      />
    </div>
  );
}

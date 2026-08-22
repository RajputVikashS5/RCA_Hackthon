import React from 'react';
import ReactECharts from 'echarts-for-react';
import ChartCard from '../../dashboard/ChartCard';
import type { SimilarityBucket } from '../../../types/analytics';

interface SimilarityDistributionChartProps {
  data: SimilarityBucket[];
}

const SimilarityDistributionChart: React.FC<SimilarityDistributionChartProps> = ({ data }) => {
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' },
      formatter: (params: any) => {
        const item = params[0];
        return `Similarity: ${item.name}<br/>${item.marker} ${item.value} retrievals`;
      },
      backgroundColor: 'white',
      borderRadius: 8,
      borderWidth: 0,
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
    },
    grid: { left: 0, right: 10, bottom: 0, top: 10, containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(d => d.range),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: 'var(--muted)', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      splitLine: { show: false }
    },
    series: [
      {
        type: 'bar',
        showBackground: true,
        backgroundStyle: { color: 'rgba(0,0,0,0.03)', borderRadius: [4, 4, 0, 0] },
        data: data.map((d, i) => {
          // Color based on quality bucket
          let color: any = {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#34d399' }, { offset: 1, color: '#059669' }] // green
          };
          if (i === 3) color = {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#fbbf24' }, { offset: 1, color: '#d97706' }] // orange
          };
          if (i === 4) color = {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#f87171' }, { offset: 1, color: '#b91c1c' }] // red
          };
          return {
            value: d.count,
            itemStyle: { color, borderRadius: [4, 4, 0, 0] }
          }
        }),
        barWidth: '50%'
      }
    ]
  };

  return (
    <ChartCard title="Similarity Distribution">
      <div style={{ height: '300px', width: '100%' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
      </div>
    </ChartCard>
  );
};

export default SimilarityDistributionChart;

import React from 'react';
import ReactECharts from 'echarts-for-react';
import ChartCard from '../../dashboard/ChartCard';
import type { RootCause } from '../../../types/analytics';

interface RootCauseChartProps {
  data: RootCause[];
}

const RootCauseChart: React.FC<RootCauseChartProps> = ({ data }) => {
  // Sort descending and limit to top 6-8
  const sortedData = [...data].sort((a, b) => a.count - b.count); // Echarts horizontal bar renders bottom-to-top

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' },
      formatter: (params: any) => {
        const item = params[0];
        const dataItem = sortedData[item.dataIndex];
        return `${dataItem.name}<br/>${item.marker} ${item.value} occurrences (${dataItem.percentage}%)`;
      },
      backgroundColor: 'white',
      borderRadius: 8,
      borderWidth: 0,
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
    },
    grid: { left: 10, right: 40, bottom: 0, top: 10, containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'category',
      data: sortedData.map(d => d.name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: 'var(--text-primary)', fontSize: 13, width: 140, overflow: 'truncate' }
    },
    series: [
      {
        type: 'bar',
        data: sortedData.map(d => d.count),
        showBackground: true,
        backgroundStyle: { color: 'rgba(0,0,0,0.03)', borderRadius: [0, 4, 4, 0] },
        itemStyle: { 
          color: {
            type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [{ offset: 0, color: '#34d399' }, { offset: 1, color: '#059669' }]
          },
          borderRadius: [0, 4, 4, 0] 
        },
        barWidth: 16,
        label: {
          show: true,
          position: 'right',
          color: 'var(--muted)',
          fontSize: 12,
          formatter: '{c}'
        }
      }
    ]
  };

  return (
    <ChartCard title="Top Root Causes">
      <div style={{ height: '300px', width: '100%' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
      </div>
    </ChartCard>
  );
};

export default RootCauseChart;

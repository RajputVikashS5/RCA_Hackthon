import React from 'react';
import ReactECharts from 'echarts-for-react';
import ChartCard from '../../dashboard/ChartCard';
import type { ResolutionTimeBySeverity } from '../../../types/analytics';

interface ResolutionTimeChartProps {
  data: ResolutionTimeBySeverity[];
}

const ResolutionTimeChart: React.FC<ResolutionTimeChartProps> = ({ data }) => {
  // ECharts horizontal bar draws from bottom to top, so we reverse it to have Critical on top
  const sortedData = [...data].reverse();


  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' },
      formatter: (params: any) => {
        const item = params[0];
        return `${item.name}<br/>${item.marker} ${item.value} hours average`;
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
      data: sortedData.map(d => d.severity),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: 'var(--text-primary)', fontSize: 13 }
    },
    series: [
      {
        type: 'bar',
        showBackground: true,
        backgroundStyle: { color: 'rgba(0,0,0,0.03)', borderRadius: [0, 4, 4, 0] },
        data: sortedData.map(d => {
          let gradient;
          if (d.severity === 'Critical') gradient = [{ offset: 0, color: '#fca5a5' }, { offset: 1, color: '#dc2626' }];
          else if (d.severity === 'High') gradient = [{ offset: 0, color: '#fcd34d' }, { offset: 1, color: '#d97706' }];
          else if (d.severity === 'Medium') gradient = [{ offset: 0, color: '#34d399' }, { offset: 1, color: '#059669' }];
          else gradient = [{ offset: 0, color: '#9ca3af' }, { offset: 1, color: '#4b5563' }];
          
          return {
            value: d.averageTimeHours,
            itemStyle: { 
              color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: gradient },
              borderRadius: [0, 4, 4, 0] 
            }
          };
        }),
        barWidth: 16,
        label: {
          show: true,
          position: 'right',
          color: 'var(--muted)',
          fontSize: 12,
          formatter: '{c} hrs'
        }
      }
    ]
  };

  return (
    <ChartCard title="Average Resolution Time">
      <div style={{ height: '240px', width: '100%' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
      </div>
    </ChartCard>
  );
};

export default ResolutionTimeChart;

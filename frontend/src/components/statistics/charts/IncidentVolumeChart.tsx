import React from 'react';
import ReactECharts from 'echarts-for-react';
import ChartCard from '../../dashboard/ChartCard';
import type { IncidentVolumeDataPoint } from '../../../types/analytics';

interface IncidentVolumeChartProps {
  data: IncidentVolumeDataPoint[];
}

const IncidentVolumeChart: React.FC<IncidentVolumeChartProps> = ({ data }) => {
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' },
      backgroundColor: 'white',
      borderRadius: 8,
      borderWidth: 0,
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
    },
    legend: {
      data: ['Total Incidents', 'Resolved'],
      bottom: 0,
      icon: 'circle',
      itemWidth: 10,
      textStyle: { color: 'var(--muted)' }
    },
    grid: { left: 0, right: 0, bottom: 30, top: 10, containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#9ca3af', fontSize: 12, margin: 12 }
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
        name: 'Total Incidents',
        type: 'bar',
        data: data.map(d => d.total),
        showBackground: true,
        backgroundStyle: { color: 'rgba(0,0,0,0.03)', borderRadius: [4, 4, 0, 0] },
        itemStyle: { 
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#047857' }, { offset: 1, color: '#064e3b' }]
          },
          borderRadius: [4, 4, 0, 0] 
        },
        barWidth: 16,
        barGap: '20%'
      },
      {
        name: 'Resolved',
        type: 'bar',
        data: data.map(d => d.resolved),
        showBackground: true,
        backgroundStyle: { color: 'rgba(0,0,0,0.03)', borderRadius: [4, 4, 0, 0] },
        itemStyle: { 
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#34d399' }, { offset: 1, color: '#059669' }]
          },
          borderRadius: [4, 4, 0, 0] 
        },
        barWidth: 16
      }
    ]
  };

  return (
    <ChartCard title="Incident Volume">
      <div style={{ color: 'var(--muted)', fontSize: '13px', marginBottom: '24px' }}>
        Incident activity over time
      </div>
      <div style={{ height: '300px', width: '100%' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
      </div>
    </ChartCard>
  );
};

export default IncidentVolumeChart;

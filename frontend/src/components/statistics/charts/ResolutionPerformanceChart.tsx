import React from 'react';
import ReactECharts from 'echarts-for-react';
import ChartCard from '../../dashboard/ChartCard';
import type { ResolutionPerformance } from '../../../types/analytics';

interface ResolutionPerformanceChartProps {
  data: ResolutionPerformance[];
}

const ResolutionPerformanceChart: React.FC<ResolutionPerformanceChartProps> = ({ data }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Resolved': return '#10b981';
      case 'Pending': return '#f59e0b';
      case 'Reopened': return '#f97316';
      case 'Unresolved': return '#ef4444';
      default: return '#9ca3af';
    }
  };

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%',
      backgroundColor: 'white',
      borderRadius: 8,
      borderWidth: 0,
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      icon: 'circle',
      itemWidth: 10,
      textStyle: { color: 'var(--muted)' },
      formatter: (name: string) => {
        const item = data.find(d => d.status === name);
        return `${name}  ${item ? item.percentage + '%' : ''}`;
      }
    },
    series: [
      {
        type: 'pie',
        radius: ['55%', '80%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        label: { show: false },
        itemStyle: {
          borderWidth: 2,
          borderColor: '#fff',
        },
        data: data.map(d => ({
          value: d.percentage,
          name: d.status,
          itemStyle: { color: getStatusColor(d.status) }
        }))
      }
    ]
  };

  return (
    <ChartCard title="Resolution Performance">
      <div style={{ position: 'relative', height: '240px', display: 'flex', alignItems: 'center' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
        <div style={{ position: 'absolute', left: '35%', top: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
          <div style={{ fontSize: '11px', color: 'var(--muted)', lineHeight: 1.2 }}>Resolution<br/>Status</div>
        </div>
      </div>
    </ChartCard>
  );
};

export default ResolutionPerformanceChart;

import React from 'react';
import ReactECharts from 'echarts-for-react';
import ChartCard from '../../dashboard/ChartCard';
import type { SeverityDistribution } from '../../../types/analytics';

interface SeverityDonutChartProps {
  data: SeverityDistribution[];
}

const SeverityDonutChart: React.FC<SeverityDonutChartProps> = ({ data }) => {
  const getSeverityColor = (level: string) => {
    switch (level) {
      case 'Critical': return '#ef4444'; // red
      case 'High': return '#f97316'; // orange
      case 'Medium': return '#10b981'; // green/lime
      case 'Low': return '#9ca3af'; // neutral/gray
      default: return '#9ca3af';
    }
  };

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
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
        const item = data.find(d => d.level === name);
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
          value: d.count,
          name: d.level,
          itemStyle: { color: getSeverityColor(d.level) }
        }))
      }
    ]
  };

  return (
    <ChartCard title="Incident Severity">
      <div style={{ position: 'relative', height: '300px', display: 'flex', alignItems: 'center' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
        <div style={{ position: 'absolute', left: '35%', top: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
          <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Total</div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--text-primary)' }}>
            {data.reduce((acc, curr) => acc + curr.count, 0)}
          </div>
        </div>
      </div>
    </ChartCard>
  );
};

export default SeverityDonutChart;

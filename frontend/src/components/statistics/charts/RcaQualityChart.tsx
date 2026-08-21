import React from 'react';
import ReactECharts from 'echarts-for-react';
import ChartCard from '../../dashboard/ChartCard';
import type { RcaQuality } from '../../../types/analytics';

interface RcaQualityChartProps {
  data: RcaQuality[];
}

const RcaQualityChart: React.FC<RcaQualityChartProps> = ({ data }) => {
  const getQualityColor = (level: string) => {
    switch (level) {
      case 'High': return '#10b981';
      case 'Medium': return '#9bcc2b';
      case 'Low': return '#f97316';
      case 'Insufficient': return '#ef4444';
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
          itemStyle: { color: getQualityColor(d.level) }
        }))
      }
    ]
  };

  return (
    <ChartCard title="RCA Evidence Quality">
      <div style={{ position: 'relative', height: '240px', display: 'flex', alignItems: 'center' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
        <div style={{ position: 'absolute', left: '35%', top: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
          <div style={{ fontSize: '11px', color: 'var(--muted)', lineHeight: 1.2 }}>RCA<br/>Quality</div>
        </div>
      </div>
      <div style={{ fontSize: '13px', color: 'var(--muted)', textAlign: 'center', marginTop: '16px', padding: '0 16px' }}>
        Confidence is based on supporting historical evidence, consistency of root causes, service alignment, and retrieval quality.
      </div>
    </ChartCard>
  );
};

export default RcaQualityChart;

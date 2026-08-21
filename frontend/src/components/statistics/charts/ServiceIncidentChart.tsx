import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';
import ChartCard from '../../dashboard/ChartCard';
import type { ServiceStatistic } from '../../../types/analytics';

interface ServiceIncidentChartProps {
  services: ServiceStatistic[];
  components: ServiceStatistic[];
}

const ServiceIncidentChart: React.FC<ServiceIncidentChartProps> = ({ services, components }) => {
  const [view, setView] = useState<'service' | 'component'>('service');
  
  const data = view === 'service' ? services : components;
  const sortedData = [...data].sort((a, b) => a.count - b.count); // Echarts horizontal bar renders bottom-to-top

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' },
      formatter: (params: any) => {
        const item = params[0];
        const dataItem = sortedData[item.dataIndex];
        return `${dataItem.name}<br/>${item.marker} ${item.value} incidents (${dataItem.percentage}%)`;
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
            colorStops: [{ offset: 0, color: '#047857' }, { offset: 1, color: '#064e3b' }]
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
    <ChartCard title="Incidents by Service">
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', backgroundColor: 'var(--canvas)', padding: '4px', borderRadius: '8px', width: 'fit-content' }}>
        <button 
          onClick={() => setView('service')}
          style={{ 
            padding: '6px 12px', 
            borderRadius: '6px', 
            border: 'none', 
            background: view === 'service' ? 'white' : 'transparent',
            boxShadow: view === 'service' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
            color: view === 'service' ? 'var(--text-primary)' : 'var(--muted)',
            fontWeight: 500,
            fontSize: '13px',
            cursor: 'pointer'
          }}
        >
          Service
        </button>
        <button 
          onClick={() => setView('component')}
          style={{ 
            padding: '6px 12px', 
            borderRadius: '6px', 
            border: 'none', 
            background: view === 'component' ? 'white' : 'transparent',
            boxShadow: view === 'component' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
            color: view === 'component' ? 'var(--text-primary)' : 'var(--muted)',
            fontWeight: 500,
            fontSize: '13px',
            cursor: 'pointer'
          }}
        >
          Component
        </button>
      </div>
      <div style={{ height: '260px', width: '100%' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
      </div>
    </ChartCard>
  );
};

export default ServiceIncidentChart;

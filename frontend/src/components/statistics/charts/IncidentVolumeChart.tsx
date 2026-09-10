import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';
import ChartCard from '../../dashboard/ChartCard';
import type { IncidentVolumeDataPoint } from '../../../types/analytics';

interface IncidentVolumeChartProps {
  data: IncidentVolumeDataPoint[];
}

const IncidentVolumeChart: React.FC<IncidentVolumeChartProps> = ({ data }) => {
  const [viewMode, setViewMode] = useState<'spline' | 'bar'>('spline');
  const isDark = typeof document !== 'undefined' && document.body.classList.contains('theme-dark');

  const splineOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line',
        lineStyle: { color: isDark ? '#334155' : '#cbd5e1', type: 'dashed', width: 1 }
      },
      backgroundColor: isDark ? '#0f172a' : 'white',
      borderColor: isDark ? '#1e293b' : '#e2e8f0',
      borderWidth: 1,
      padding: [10, 14],
      textStyle: { color: isDark ? '#f8fafc' : '#1e293b', fontSize: 12 },
      extraCssText: 'box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1); border-radius: 8px;'
    },
    legend: {
      data: ['Total Incidents', 'Resolved'],
      bottom: 0,
      icon: 'circle',
      itemWidth: 10,
      textStyle: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 12 }
    },
    grid: { left: '1%', right: '2%', bottom: 35, top: 15, containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date),
      axisLine: {
        show: true,
        lineStyle: { color: isDark ? '#1e293b' : '#e5e7eb', width: 1 }
      },
      axisTick: { show: false },
      axisLabel: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 12, margin: 10 },
      splitLine: { show: false },
      boundaryGap: true
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { 
        color: isDark ? '#94a3b8' : '#64748b', 
        fontSize: 12,
        margin: 12,
        formatter: (val: number) => val.toLocaleString()
      },
      splitLine: { 
        show: true,
        lineStyle: { color: isDark ? '#1e293b' : '#f1f5f9', width: 1, type: 'dashed' }
      }
    },
    series: [
      {
        name: 'Total Incidents',
        type: 'line',
        smooth: 0.45,
        showSymbol: false,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          color: '#ffffff',
          borderColor: '#2b7fff',
          borderWidth: 2.5
        },
        lineStyle: {
          color: '#2b7fff',
          width: 3.5,
          cap: 'round'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(43, 127, 255, 0.25)' },
              { offset: 0.85, color: 'rgba(43, 127, 255, 0.03)' },
              { offset: 1, color: 'rgba(43, 127, 255, 0.00)' }
            ]
          }
        },
        emphasis: {
          scale: 1.4,
          itemStyle: {
            color: '#ffffff',
            borderColor: '#2b7fff',
            borderWidth: 3,
            shadowColor: 'rgba(43, 127, 255, 0.35)',
            shadowBlur: 8
          }
        },
        data: data.map(d => d.total)
      },
      {
        name: 'Resolved',
        type: 'line',
        smooth: 0.45,
        showSymbol: false,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          color: '#ffffff',
          borderColor: '#10b981',
          borderWidth: 2.5
        },
        lineStyle: {
          color: '#10b981',
          width: 3.5,
          cap: 'round'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(16, 185, 129, 0.18)' },
              { offset: 0.85, color: 'rgba(16, 185, 129, 0.02)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.00)' }
            ]
          }
        },
        emphasis: {
          scale: 1.4,
          itemStyle: {
            color: '#ffffff',
            borderColor: '#10b981',
            borderWidth: 3,
            shadowColor: 'rgba(16, 185, 129, 0.35)',
            shadowBlur: 8
          }
        },
        data: data.map(d => d.resolved)
      }
    ]
  };

  const barOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' },
      backgroundColor: isDark ? '#0f172a' : 'white',
      borderRadius: 8,
      borderWidth: 0,
      textStyle: { color: isDark ? '#f8fafc' : '#1e293b' },
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
    },
    legend: {
      data: ['Total Incidents', 'Resolved'],
      bottom: 0,
      icon: 'circle',
      itemWidth: 10,
      textStyle: { color: isDark ? '#94a3b8' : '#64748b' }
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
            colorStops: [{ offset: 0, color: '#4f7df9' }, { offset: 1, color: '#2563eb' }]
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
    <ChartCard 
      title="Incident Volume & Velocity" 
      headerRight={
        <div style={{ display: 'inline-flex', background: '#f1f5f9', borderRadius: '6px', padding: '2px' }}>
          <button
            type="button"
            onClick={() => setViewMode('spline')}
            style={{
              border: 0,
              background: viewMode === 'spline' ? '#ffffff' : 'transparent',
              color: viewMode === 'spline' ? '#2563eb' : '#64748b',
              fontWeight: 600,
              fontSize: '11px',
              padding: '4px 10px',
              borderRadius: '4px',
              cursor: 'pointer',
              boxShadow: viewMode === 'spline' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            Spline Curve
          </button>
          <button
            type="button"
            onClick={() => setViewMode('bar')}
            style={{
              border: 0,
              background: viewMode === 'bar' ? '#ffffff' : 'transparent',
              color: viewMode === 'bar' ? '#2563eb' : '#64748b',
              fontWeight: 600,
              fontSize: '11px',
              padding: '4px 10px',
              borderRadius: '4px',
              cursor: 'pointer',
              boxShadow: viewMode === 'bar' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            Bar Breakdown
          </button>
        </div>
      }
    >
      <div style={{ color: 'var(--muted)', fontSize: '13px', marginBottom: '16px' }}>
        Smooth spline trend & historical volume progression
      </div>
      <div style={{ height: '300px', width: '100%' }}>
        <ReactECharts 
          option={viewMode === 'spline' ? splineOption : barOption} 
          style={{ height: '100%', width: '100%' }} 
          notMerge={true}
        />
      </div>
    </ChartCard>
  );
};

export default IncidentVolumeChart;

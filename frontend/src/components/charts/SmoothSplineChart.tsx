import React, { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'

export interface SplineDataPoint {
  label: string
  value: number
  secondaryValue?: number
}

export interface SmoothSplineChartProps {
  data?: (number | SplineDataPoint)[]
  labels?: string[]
  height?: string | number
  color?: string
  secondaryColor?: string
  showSecondary?: boolean
  secondaryName?: string
  primaryName?: string
  yAxisMin?: number
  yAxisMax?: number
  yInterval?: number
  unit?: string
  showPoints?: boolean
  pointSize?: number
  lineWidth?: number
  smoothness?: number | boolean
  fillArea?: boolean
  areaOpacity?: number
  dashedGrid?: boolean
  showAxisLine?: boolean
  title?: string
  subtitle?: string
  className?: string
}

const DEFAULT_SAMPLE_POINTS: SplineDataPoint[] = [
  { label: 'Sun', value: 1 },
  { label: 'Mon', value: 8 },
  { label: 'Tue', value: 1 },
  { label: 'Wed', value: 11 },
  { label: 'Thu', value: 0 },
  { label: 'Fri', value: 0 },
  { label: 'Sat', value: 0 },
]

export const SmoothSplineChart: React.FC<SmoothSplineChartProps> = ({
  data = DEFAULT_SAMPLE_POINTS,
  labels,
  height = '210px',
  color = '#2b7fff',
  secondaryColor = '#10b981',
  showSecondary = false,
  secondaryName = 'Resolved',
  primaryName = 'Incident Volume',
  yAxisMin = 0,
  yAxisMax = 12,
  yInterval = 2,
  unit = '',
  showPoints = false,
  pointSize = 6,
  lineWidth = 3.5,
  smoothness = 0.45,
  fillArea = true,
  areaOpacity = 0.22,
  dashedGrid = true,
  showAxisLine = true,
  title,
  subtitle,
  className = '',
}) => {
  const isDark = typeof document !== 'undefined' && document.body.classList.contains('theme-dark')

  const { chartLabels, primaryValues, secondaryValues } = useMemo(() => {
    if (!data || data.length === 0) {
      return { chartLabels: [], primaryValues: [], secondaryValues: [] }
    }

    if (typeof data[0] === 'number') {
      const numData = data as number[]
      const lbls = labels && labels.length === numData.length 
        ? labels 
        : numData.map((_, i) => labels?.[i] ?? `Point ${i + 1}`)
      return {
        chartLabels: lbls,
        primaryValues: numData,
        secondaryValues: [],
      }
    }

    const objData = data as SplineDataPoint[]
    return {
      chartLabels: labels || objData.map((d) => d.label),
      primaryValues: objData.map((d) => d.value),
      secondaryValues: objData.map((d) => d.secondaryValue ?? 0),
    }
  }, [data, labels])

  const option = useMemo(() => {
    const seriesList: any[] = [
      {
        name: primaryName,
        type: 'line',
        smooth: smoothness,
        showSymbol: showPoints,
        symbol: 'circle',
        symbolSize: pointSize,
        itemStyle: {
          color: '#ffffff',
          borderColor: color,
          borderWidth: 2.5,
        },
        lineStyle: {
          color: color,
          width: lineWidth,
          cap: 'round',
        },
        areaStyle: fillArea
          ? {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(43, 127, 255, 0.25)' },
                  { offset: 0.85, color: 'rgba(43, 127, 255, 0.03)' },
                  { offset: 1, color: 'rgba(43, 127, 255, 0.00)' },
                ],
              },
            }
          : undefined,
        emphasis: {
          scale: 1.4,
          itemStyle: {
            color: '#ffffff',
            borderColor: color,
            borderWidth: 3,
            shadowColor: 'rgba(43, 127, 255, 0.35)',
            shadowBlur: 8,
          },
        },
        data: primaryValues,
      },
    ]

    if (showSecondary && secondaryValues.length > 0) {
      seriesList.push({
        name: secondaryName,
        type: 'line',
        smooth: smoothness,
        showSymbol: showPoints,
        symbol: 'circle',
        symbolSize: pointSize,
        itemStyle: {
          color: '#ffffff',
          borderColor: secondaryColor,
          borderWidth: 2.5,
        },
        lineStyle: {
          color: secondaryColor,
          width: lineWidth,
          cap: 'round',
        },
        emphasis: {
          scale: 1.4,
          itemStyle: {
            color: '#ffffff',
            borderColor: secondaryColor,
            borderWidth: 3,
            shadowColor: 'rgba(16, 185, 129, 0.35)',
            shadowBlur: 8,
          },
        },
        data: secondaryValues,
      })
    }

    return {
      backgroundColor: 'transparent',
      animation: true,
      animationDuration: 1000,
      animationEasing: 'cubicOut',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'line',
          lineStyle: {
            color: isDark ? '#334155' : '#cbd5e1',
            type: 'dashed',
            width: 1,
          },
        },
        backgroundColor: isDark ? '#0f172a' : '#ffffff',
        borderColor: isDark ? '#1e293b' : '#e2e8f0',
        borderWidth: 1,
        padding: [8, 12],
        textStyle: {
          color: isDark ? '#f8fafc' : '#1e293b',
          fontSize: 12,
        },
        extraCssText: 'box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); border-radius: 8px;',
        formatter: (params: any) => {
          if (!Array.isArray(params) || params.length === 0) return ''
          const header = `<div style="font-weight: 600; margin-bottom: 3px; color: ${isDark ? '#94a3b8' : '#64748b'}; font-size: 11px;">${params[0].name}</div>`
          const items = params
            .map(
              (p: any) =>
                `<div style="display: flex; align-items: center; justify-content: space-between; gap: 14px;">
                  <span style="display: inline-flex; align-items: center; gap: 5px;">
                    <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: ${p.color};"></span>
                    <span>${p.seriesName}:</span>
                  </span>
                  <strong style="font-size: 12px;">${typeof p.value === 'number' ? p.value.toLocaleString() : p.value} ${unit}</strong>
                </div>`
            )
            .join('')
          return `${header}${items}`
        },
      },
      grid: {
        left: '0%',
        right: '2%',
        top: '6%',
        bottom: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: chartLabels,
        axisLine: {
          show: showAxisLine,
          lineStyle: {
            color: isDark ? '#1e293b' : '#e5e7eb',
            width: 1,
          },
        },
        axisTick: { show: false },
        axisLabel: {
          color: isDark ? '#94a3b8' : '#64748b',
          fontSize: 12,
          margin: 10,
        },
        splitLine: { show: false },
        boundaryGap: true,
      },
      yAxis: {
        type: 'value',
        min: yAxisMin,
        max: yAxisMax,
        interval: yInterval,
        splitNumber: yAxisMax && yInterval ? Math.round((yAxisMax - (yAxisMin || 0)) / yInterval) : 6,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: isDark ? '#94a3b8' : '#64748b',
          fontSize: 12,
          margin: 12,
          formatter: (value: number) => value.toString(),
        },
        splitLine: {
          show: true,
          lineStyle: {
            color: isDark ? '#1e293b' : '#f1f5f9',
            width: 1,
            type: dashedGrid ? 'dashed' : 'solid',
          },
        },
      },
      series: seriesList,
    }
  }, [
    chartLabels,
    primaryValues,
    secondaryValues,
    primaryName,
    secondaryName,
    color,
    secondaryColor,
    showSecondary,
    showPoints,
    pointSize,
    lineWidth,
    smoothness,
    fillArea,
    areaOpacity,
    dashedGrid,
    showAxisLine,
    unit,
    yAxisMin,
    yAxisMax,
    yInterval,
    isDark,
  ])

  return (
    <div className={`spline-chart-container ${className}`} style={{ width: '100%' }}>
      {(title || subtitle) && (
        <div style={{ marginBottom: '16px' }}>
          {title && <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 700, color: isDark ? '#f8fafc' : '#0f172a' }}>{title}</h2>}
          {subtitle && <p style={{ margin: '4px 0 0', fontSize: '14px', color: '#64748b' }}>{subtitle}</p>}
        </div>
      )}
      <div style={{ height, width: '100%' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} notMerge={true} lazyUpdate={true} />
      </div>
    </div>
  )
}

export default SmoothSplineChart

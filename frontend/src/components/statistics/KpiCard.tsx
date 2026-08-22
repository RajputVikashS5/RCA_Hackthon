import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { KpiMetric } from '../../types/analytics';

interface KpiCardProps {
  metric: KpiMetric;
}

const KpiCard: React.FC<KpiCardProps> = ({ metric }) => {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div style={{ fontSize: '14px', color: 'var(--muted)', fontWeight: 500 }}>
        {metric.label}
      </div>
      <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-display)', color: 'var(--text-primary)' }}>
        {metric.value}
      </div>
      
      {(metric.trend || metric.trendText) && (
        <div className="stat-change" style={{ margin: 0, marginTop: 'auto', paddingTop: '8px' }}>
          {metric.trend === 'up' && (
            <span className="trend-up" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <TrendingUp size={14} /> {metric.trendValue}
            </span>
          )}
          {metric.trend === 'down' && (
            <span className="trend-down" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <TrendingDown size={14} /> {metric.trendValue}
            </span>
          )}
          {metric.trend === 'none' && metric.trendValue && (
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--muted)', fontWeight: 500 }}>
              <Minus size={14} /> {metric.trendValue}
            </span>
          )}
          
          {metric.trendText && (
            <span className="trend-text">{metric.trendText}</span>
          )}
        </div>
      )}
    </div>
  );
};

export default KpiCard;

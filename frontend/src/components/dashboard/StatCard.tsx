import React from 'react';
import { MoreHorizontal, TrendingUp, TrendingDown } from 'lucide-react';

export interface StatCardProps {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'none';
  trendText: string;
  isDark?: boolean;
  date?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, trend, trendText, isDark, date }) => {
  return (
    <div className={`card ${isDark ? 'card-dark' : ''}`}>
      <div className="card-header">
        <span className="card-title">
          {isDark ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'white' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--error)' }}></div>
              {title}
            </div>
          ) : (
            title
          )}
        </span>
        <button className="header-icon-btn" style={{ width: '28px', height: '28px', border: 'none', background: 'transparent' }}>
          <MoreHorizontal size={16} color={isDark ? 'white' : 'var(--muted)'} />
        </button>
      </div>
      
      {date && (
        <div style={{ fontSize: '11px', color: isDark ? 'rgba(255,255,255,0.6)' : 'var(--muted)', marginBottom: '8px' }}>
          {date}
        </div>
      )}
      
      <div className="stat-value">{value}</div>
      
      {isDark && (
        <div style={{ color: 'var(--brand-green)', fontSize: '14px', fontWeight: '500', marginTop: '12px' }}>
          {change} in 1 week
        </div>
      )}

      {!isDark && trend !== 'none' && (
        <div className="stat-change">
          {trend === 'up' ? (
            <span className="trend-up" style={{ display: 'flex', alignItems: 'center' }}><TrendingUp size={14} /> {change}</span>
          ) : (
            <span className="trend-down" style={{ display: 'flex', alignItems: 'center' }}><TrendingDown size={14} /> {change}</span>
          )}
          <span className="trend-text">{trendText}</span>
        </div>
      )}

      {isDark && (
        <div style={{ marginTop: 'auto', paddingTop: '16px', fontSize: '12px', color: 'rgba(255,255,255,0.7)', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
          See Statistics {'>'}
        </div>
      )}
    </div>
  );
};

export default StatCard;

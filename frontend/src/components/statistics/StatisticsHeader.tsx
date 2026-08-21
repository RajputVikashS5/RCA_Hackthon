import React from 'react';
import { Calendar } from 'lucide-react';

interface StatisticsHeaderProps {
  timeRange: string;
  onTimeRangeChange: (range: string) => void;
}

const StatisticsHeader: React.FC<StatisticsHeaderProps> = ({ timeRange, onTimeRangeChange }) => {
  return (
    <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
      <div>
        <h1 className="display-lg" style={{ marginBottom: '8px' }}>Statistics</h1>
        <p className="body-md" style={{ color: 'var(--muted)' }}>
          Understand incident trends, RCA patterns, and AI analysis performance.
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          backgroundColor: 'white', 
          padding: '8px 16px', 
          borderRadius: '100px',
          border: '1px solid var(--border)',
          gap: '8px'
        }}>
          <Calendar size={16} color="var(--muted)" />
          <select 
            value={timeRange} 
            onChange={(e) => onTimeRangeChange(e.target.value)}
            style={{
              border: 'none',
              background: 'transparent',
              outline: 'none',
              fontSize: '14px',
              fontWeight: 500,
              color: 'var(--text-primary)',
              cursor: 'pointer'
            }}
          >
            <option value="7d">7 Days</option>
            <option value="30d">30 Days</option>
            <option value="3m">3 Months</option>
            <option value="6m">6 Months</option>
            <option value="1y">1 Year</option>
          </select>
        </div>
      </div>
    </header>
  );
};

export default StatisticsHeader;

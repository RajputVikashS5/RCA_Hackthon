import React from 'react';
import { MoreHorizontal } from 'lucide-react';

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
  headerRight?: React.ReactNode;
}

const ChartCard: React.FC<ChartCardProps> = ({ title, children, headerRight }) => {
  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title" style={{ color: 'var(--ink)' }}>{title}</span>
        {headerRight || (
          <button className="header-icon-btn" style={{ width: '28px', height: '28px', border: 'none', background: 'transparent' }}>
            <MoreHorizontal size={16} color="var(--muted)" />
          </button>
        )}
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {children}
      </div>
    </div>
  );
};

export default ChartCard;

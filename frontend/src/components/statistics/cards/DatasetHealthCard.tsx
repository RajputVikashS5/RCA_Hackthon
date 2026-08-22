import React from 'react';
import ChartCard from '../../dashboard/ChartCard';
import type { DatasetHealth } from '../../../types/analytics';

interface DatasetHealthCardProps {
  data: DatasetHealth;
}

const DatasetHealthCard: React.FC<DatasetHealthCardProps> = ({ data }) => {
  return (
    <ChartCard title="Dataset Health">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', minHeight: '240px' }}>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Total Records</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)' }}>{data.totalRecords}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Successfully Indexed</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--brand-green-dark)' }}>{data.successfullyIndexed}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Duplicates Removed</div>
            <div style={{ fontSize: '18px', fontWeight: 700 }}>{data.duplicatesRemoved}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Invalid Records</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: '#ef4444' }}>{data.invalidRecords}</div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', borderLeft: '1px solid var(--border)', paddingLeft: '24px' }}>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Root Cause Available</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)' }}>{data.rootCauseAvailablePct}%</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Resolution Available</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)' }}>{data.resolutionAvailablePct}%</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Service Info Available</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)' }}>{data.serviceInformationAvailablePct}%</div>
          </div>
        </div>
      </div>
    </ChartCard>
  );
};

export default DatasetHealthCard;

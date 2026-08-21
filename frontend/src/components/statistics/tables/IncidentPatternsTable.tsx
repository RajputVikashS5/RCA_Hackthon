import React from 'react';
import ChartCard from '../../dashboard/ChartCard';
import type { IncidentPattern } from '../../../types/analytics';

interface IncidentPatternsTableProps {
  data: IncidentPattern[];
}

const IncidentPatternsTable: React.FC<IncidentPatternsTableProps> = ({ data }) => {
  return (
    <ChartCard title="Most Common Incident Patterns">
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--muted)' }}>
              <th style={{ padding: '12px 16px', fontWeight: 500 }}>Incident Pattern</th>
              <th style={{ padding: '12px 16px', fontWeight: 500 }}>Occurrences</th>
              <th style={{ padding: '12px 16px', fontWeight: 500 }}>Avg. Similarity</th>
              <th style={{ padding: '12px 16px', fontWeight: 500 }}>Most Common Root Cause</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr 
                key={row.id} 
                style={{ 
                  borderBottom: '1px solid var(--border)', 
                  transition: 'background-color 0.2s', 
                  cursor: 'pointer' 
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--canvas)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <td style={{ padding: '16px', fontWeight: 500, color: 'var(--text-primary)' }}>{row.pattern}</td>
                <td style={{ padding: '16px' }}>{row.occurrences}</td>
                <td style={{ padding: '16px' }}>{row.avgSimilarity.toFixed(2)}</td>
                <td style={{ padding: '16px', color: 'var(--muted)' }}>{row.mostCommonRootCause}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </ChartCard>
  );
};

export default IncidentPatternsTable;

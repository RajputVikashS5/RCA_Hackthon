import React from 'react';
import ChartCard from '../../dashboard/ChartCard';
import type { AiAnalysisPerformance } from '../../../types/analytics';

interface AiPerformanceCardProps {
  data: AiAnalysisPerformance;
}

const AiPerformanceCard: React.FC<AiPerformanceCardProps> = ({ data }) => {
  return (
    <ChartCard title="AI Analysis Performance">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', height: '100%', justifyContent: 'center', minHeight: '240px' }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
          <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Total RCA Analyses</div>
          <div style={{ fontSize: '20px', fontWeight: 700 }}>{data.totalAnalyses}</div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
          <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Successful Analyses</div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--brand-green-dark)' }}>{data.successful}</div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
          <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Insufficient Evidence</div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: '#f59e0b' }}>{data.insufficientEvidence}</div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Average Response Time</div>
          <div style={{ fontSize: '20px', fontWeight: 700 }}>{data.averageResponseTimeSeconds}s</div>
        </div>

      </div>
    </ChartCard>
  );
};

export default AiPerformanceCard;

import React from 'react';
import ChartCard from '../../dashboard/ChartCard';
import type { RetrievalQuality } from '../../../types/analytics';

interface RagQualityCardProps {
  data: RetrievalQuality;
}

const RagQualityCard: React.FC<RagQualityCardProps> = ({ data }) => {
  return (
    <ChartCard title="RAG Retrieval Quality">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', height: '100%', justifyContent: 'center', minHeight: '240px' }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
          <div>
            <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Average Top-1 Similarity</div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Primary match</div>
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700 }}>{data.averageTop1Similarity}</div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
          <div>
            <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Average Top-5 Similarity</div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Context matches</div>
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700 }}>{data.averageTop5Similarity}</div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
          <div>
            <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Useful Retrievals</div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Similarity &gt; 0.75</div>
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--brand-green-dark)' }}>{data.usefulRetrievalRate}%</div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Weak Retrievals</div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Similarity &lt; 0.60</div>
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--error, #ef4444)' }}>{data.weakRetrievalRate}%</div>
        </div>

      </div>
    </ChartCard>
  );
};

export default RagQualityCard;

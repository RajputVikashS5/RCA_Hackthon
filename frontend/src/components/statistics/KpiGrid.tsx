import React from 'react';
import type { OverviewMetrics } from '../../types/analytics';
import KpiCard from './KpiCard';

interface KpiGridProps {
  metrics: OverviewMetrics;
}

const KpiGrid: React.FC<KpiGridProps> = ({ metrics }) => {
  return (
    <div className="grid" style={{ gridTemplateColumns: 'repeat(5, 1fr)', marginBottom: '24px' }}>
      <KpiCard metric={metrics.totalIncidents} />
      <KpiCard metric={metrics.resolvedIncidents} />
      <KpiCard metric={metrics.rcaAnalyses} />
      <KpiCard metric={metrics.averageSimilarity} />
      <KpiCard metric={metrics.averageAnalysisTime} />
    </div>
  );
};

export default KpiGrid;

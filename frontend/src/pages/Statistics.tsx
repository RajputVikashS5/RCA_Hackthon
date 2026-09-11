import React, { useState, useEffect } from 'react';
import StatisticsHeader from '../components/statistics/StatisticsHeader';
import KpiGrid from '../components/statistics/KpiGrid';
import IncidentVolumeChart from '../components/statistics/charts/IncidentVolumeChart';
import SeverityDonutChart from '../components/statistics/charts/SeverityDonutChart';
import RootCauseChart from '../components/statistics/charts/RootCauseChart';
import ServiceIncidentChart from '../components/statistics/charts/ServiceIncidentChart';
import SimilarityDistributionChart from '../components/statistics/charts/SimilarityDistributionChart';
import RcaQualityChart from '../components/statistics/charts/RcaQualityChart';
import ResolutionPerformanceChart from '../components/statistics/charts/ResolutionPerformanceChart';
import ResolutionTimeChart from '../components/statistics/charts/ResolutionTimeChart';
import RagQualityCard from '../components/statistics/cards/RagQualityCard';
import AiPerformanceCard from '../components/statistics/cards/AiPerformanceCard';
import DatasetHealthCard from '../components/statistics/cards/DatasetHealthCard';
import IncidentPatternsTable from '../components/statistics/tables/IncidentPatternsTable';

import { fetchStatistics } from '../services/analyticsService';
import type { StatisticsOverviewResponse } from '../types/analytics';

const Statistics: React.FC = () => {
  const [timeRange, setTimeRange] = useState<string>('30d');
  const [data, setData] = useState<StatisticsOverviewResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchStatistics(timeRange);
        if (isMounted) {
          setData(result);
        }
      } catch {
        if (isMounted) {
          setError('Unable to load statistics.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  }, [timeRange]);

  if (error) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '16px' }}>
        <div style={{ color: 'var(--error, #ef4444)', fontSize: '16px', fontWeight: 500 }}>{error}</div>
        <button className="btn-primary" onClick={() => setTimeRange(prev => prev)}>Try again</button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', paddingBottom: '40px' }}>
      <StatisticsHeader timeRange={timeRange} onTimeRangeChange={setTimeRange} />

      {loading || !data ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <div style={{ color: 'var(--muted)', fontSize: '16px' }}>Loading statistics...</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <KpiGrid metrics={data.overview} />

          <div className="grid grid-cols-2">
            <div style={{ gridColumn: 'span 1' }}>
              <IncidentVolumeChart data={data.incidentVolume} />
            </div>
            <div style={{ gridColumn: 'span 1' }}>
              <SeverityDonutChart data={data.severityDistribution} />
            </div>
          </div>

          <div className="grid grid-cols-2">
            <RootCauseChart data={data.topRootCauses} />
            <ServiceIncidentChart services={data.incidentsByService} components={data.incidentsByComponent} />
          </div>

          <div className="grid grid-cols-2">
            <RagQualityCard data={data.retrievalQuality} />
            <RcaQualityChart data={data.rcaQuality} />
          </div>

          <div className="grid grid-cols-2">
            <SimilarityDistributionChart data={data.similarityDistribution} />
            <ResolutionPerformanceChart data={data.resolutionPerformance} />
          </div>
          
          <div className="grid grid-cols-2">
            <ResolutionTimeChart data={data.resolutionTimeBySeverity} />
            <AiPerformanceCard data={data.aiAnalysisPerformance} />
          </div>

          <div className="grid grid-cols-2">
            <DatasetHealthCard data={data.datasetHealth} />
            <div style={{ width: '100%', height: '100%' }}></div> {/* Empty spacer or another card could go here */}
          </div>

          <div style={{ width: '100%' }}>
            <IncidentPatternsTable data={data.incidentPatterns} />
          </div>

        </div>
      )}
    </div>
  );
};

export default Statistics;

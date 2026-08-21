export interface KpiMetric {
  value: string | number;
  label: string;
  trend?: 'up' | 'down' | 'none';
  trendValue?: string;
  trendText?: string;
}

export interface OverviewMetrics {
  totalIncidents: KpiMetric;
  resolvedIncidents: KpiMetric;
  rcaAnalyses: KpiMetric;
  averageSimilarity: KpiMetric;
  averageAnalysisTime: KpiMetric;
}

export interface IncidentVolumeDataPoint {
  date: string;
  total: number;
  resolved: number;
  unresolved: number;
}

export interface SeverityDistribution {
  level: 'Critical' | 'High' | 'Medium' | 'Low';
  percentage: number;
  count: number;
}

export interface RootCause {
  name: string;
  count: number;
  percentage: number;
}

export interface ServiceStatistic {
  name: string;
  count: number;
  percentage: number;
}

export interface RetrievalQuality {
  averageTop1Similarity: number;
  averageTop5Similarity: number;
  usefulRetrievalRate: number;
  weakRetrievalRate: number;
}

export interface SimilarityBucket {
  range: string;
  count: number;
}

export interface RcaQuality {
  level: 'High' | 'Medium' | 'Low' | 'Insufficient';
  percentage: number;
  count: number;
}

export interface ResolutionPerformance {
  status: 'Resolved' | 'Pending' | 'Reopened' | 'Unresolved';
  percentage: number;
}

export interface ResolutionTimeBySeverity {
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  averageTimeHours: number;
}

export interface AiAnalysisPerformance {
  totalAnalyses: number;
  successful: number;
  insufficientEvidence: number;
  averageResponseTimeSeconds: number;
}

export interface DatasetHealth {
  totalRecords: number;
  successfullyIndexed: number;
  duplicatesRemoved: number;
  invalidRecords: number;
  rootCauseAvailablePct: number;
  resolutionAvailablePct: number;
  serviceInformationAvailablePct: number;
}

export interface IncidentPattern {
  id: string;
  pattern: string;
  occurrences: number;
  avgSimilarity: number;
  mostCommonRootCause: string;
}

export interface StatisticsOverviewResponse {
  overview: OverviewMetrics;
  incidentVolume: IncidentVolumeDataPoint[];
  severityDistribution: SeverityDistribution[];
  topRootCauses: RootCause[];
  incidentsByService: ServiceStatistic[];
  incidentsByComponent: ServiceStatistic[];
  retrievalQuality: RetrievalQuality;
  similarityDistribution: SimilarityBucket[];
  rcaQuality: RcaQuality[];
  resolutionPerformance: ResolutionPerformance[];
  resolutionTimeBySeverity: ResolutionTimeBySeverity[];
  aiAnalysisPerformance: AiAnalysisPerformance;
  datasetHealth: DatasetHealth;
  incidentPatterns: IncidentPattern[];
}

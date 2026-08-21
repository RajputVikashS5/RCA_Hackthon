import type { StatisticsOverviewResponse } from '../types/analytics';

/**
 * Mock analytics service that returns structured mock data for the Statistics page.
 * This simulates a future GET /api/statistics endpoint.
 */
export const fetchStatistics = async (timeRange: string): Promise<StatisticsOverviewResponse> => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 800));

  // In a real implementation, timeRange ('7d', '30d', etc) would adjust the backend query
  console.log(`Fetching statistics for range: ${timeRange}`);

  return {
    overview: {
      totalIncidents: {
        label: 'Total Incidents',
        value: '1,284',
        trend: 'up',
        trendValue: '12.4%',
        trendText: 'from last month'
      },
      resolvedIncidents: {
        label: 'Resolved Incidents',
        value: '1,032',
        trend: 'none',
        trendText: '80.4% resolution rate'
      },
      rcaAnalyses: {
        label: 'RCA Analyses',
        value: '428',
        trend: 'up',
        trendValue: '18.7%',
        trendText: 'from last month'
      },
      averageSimilarity: {
        label: 'Average Similarity',
        value: '0.84',
        trend: 'none',
        trendText: 'Top-5 retrieval'
      },
      averageAnalysisTime: {
        label: 'Average Analysis Time',
        value: '2.4s',
        trend: 'down',
        trendValue: '16%',
        trendText: 'from last month'
      }
    },
    incidentVolume: [
      { date: 'Mon', total: 42, resolved: 30, unresolved: 12 },
      { date: 'Tue', total: 38, resolved: 25, unresolved: 13 },
      { date: 'Wed', total: 65, resolved: 45, unresolved: 20 },
      { date: 'Thu', total: 48, resolved: 35, unresolved: 13 },
      { date: 'Fri', total: 55, resolved: 42, unresolved: 13 },
      { date: 'Sat', total: 22, resolved: 18, unresolved: 4 },
      { date: 'Sun', total: 18, resolved: 15, unresolved: 3 }
    ],
    severityDistribution: [
      { level: 'Critical', percentage: 12, count: 154 },
      { level: 'High', percentage: 28, count: 359 },
      { level: 'Medium', percentage: 42, count: 539 },
      { level: 'Low', percentage: 18, count: 232 }
    ],
    topRootCauses: [
      { name: 'Database Connection Issues', count: 359, percentage: 28 },
      { name: 'Network Connectivity', count: 270, percentage: 21 },
      { name: 'Authentication Failure', count: 205, percentage: 16 },
      { name: 'Resource Exhaustion', count: 154, percentage: 12 },
      { name: 'Configuration Error', count: 128, percentage: 10 },
      { name: 'API Timeout', count: 103, percentage: 8 },
      { name: 'Other', count: 65, percentage: 5 }
    ],
    incidentsByService: [
      { name: 'Payment API', count: 412, percentage: 32 },
      { name: 'Authentication Service', count: 315, percentage: 25 },
      { name: 'Database', count: 245, percentage: 19 },
      { name: 'Notification Service', count: 168, percentage: 13 },
      { name: 'Frontend', count: 98, percentage: 8 },
      { name: 'User Service', count: 46, percentage: 3 }
    ],
    incidentsByComponent: [
      { name: 'Redis Cache', count: 280, percentage: 22 },
      { name: 'PostgreSQL DB', count: 250, percentage: 19 },
      { name: 'Kafka Queue', count: 190, percentage: 15 },
      { name: 'Auth Gateway', count: 175, percentage: 14 },
      { name: 'Worker Nodes', count: 120, percentage: 9 }
    ],
    retrievalQuality: {
      averageTop1Similarity: 0.87,
      averageTop5Similarity: 0.82,
      usefulRetrievalRate: 91,
      weakRetrievalRate: 9
    },
    similarityDistribution: [
      { range: '0.90–1.00', count: 412 },
      { range: '0.80–0.89', count: 620 },
      { range: '0.70–0.79', count: 185 },
      { range: '0.60–0.69', count: 45 },
      { range: '< 0.60', count: 22 }
    ],
    rcaQuality: [
      { level: 'High', percentage: 62, count: 265 },
      { level: 'Medium', percentage: 25, count: 107 },
      { level: 'Low', percentage: 8, count: 34 },
      { level: 'Insufficient', percentage: 5, count: 22 }
    ],
    resolutionPerformance: [
      { status: 'Resolved', percentage: 81 },
      { status: 'Pending', percentage: 12 },
      { status: 'Reopened', percentage: 5 },
      { status: 'Unresolved', percentage: 2 }
    ],
    resolutionTimeBySeverity: [
      { severity: 'Critical', averageTimeHours: 4.2 },
      { severity: 'High', averageTimeHours: 7.8 },
      { severity: 'Medium', averageTimeHours: 13.4 },
      { severity: 'Low', averageTimeHours: 18.1 }
    ],
    aiAnalysisPerformance: {
      totalAnalyses: 428,
      successful: 411,
      insufficientEvidence: 17,
      averageResponseTimeSeconds: 2.4
    },
    datasetHealth: {
      totalRecords: 1284,
      successfullyIndexed: 1251,
      duplicatesRemoved: 21,
      invalidRecords: 12,
      rootCauseAvailablePct: 94,
      resolutionAvailablePct: 91,
      serviceInformationAvailablePct: 97
    },
    incidentPatterns: [
      { id: 'p1', pattern: 'Payment API Timeout', occurrences: 82, avgSimilarity: 0.89, mostCommonRootCause: 'Database Connection Exhaustion' },
      { id: 'p2', pattern: 'Database Connection Lost', occurrences: 67, avgSimilarity: 0.86, mostCommonRootCause: 'Connection Pool Saturation' },
      { id: 'p3', pattern: 'Authentication Failure', occurrences: 54, avgSimilarity: 0.83, mostCommonRootCause: 'Certificate Expiration' },
      { id: 'p4', pattern: 'API 500 Errors', occurrences: 37, avgSimilarity: 0.79, mostCommonRootCause: 'Configuration Error' }
    ]
  };
};

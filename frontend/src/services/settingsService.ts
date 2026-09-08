import type { ApplicationSettings, SystemStatus } from '../types/settings';

const DEFAULT_SETTINGS: ApplicationSettings = {
  ai: {
    enabled: true,
    topK: 5,
    minSimilarity: 0.70,
    responseStyle: 'Concise',
    showEvidence: true,
    showSimilarity: true,
    showUncertainty: true
  },
  retrieval: {
    searchMethod: 'Semantic Search',
    topK: 5,
    minSimilarity: 0.70,
    metadataFiltering: true,
    reranking: false
  },
  knowledgeBase: {
    activeDataset: 'Historical Incidents v1.2',
    recordCount: 1284,
    indexedCount: 1251,
    lastUpdated: 'Recently',
    embeddingStatus: 'Ready',
    duplicateHandling: 'Skip duplicates',
    missingRootCause: 'Keep record',
    missingResolution: 'Keep record'
  },
  providers: {
    llmProvider: 'Configured Provider',
    llmModel: 'gemini-3.6-flash',
    embeddingProvider: 'Local',
    embeddingModel: 'all-MiniLM-L6-v2',
    llmStatus: 'Connected',
    embeddingStatus: 'Connected'
  },
  privacy: {
    storeAnalysisHistory: true,
    storeEvidence: true,
    evaluationData: false,
    sensitiveDataHandling: true,
    dataRetention: '90 Days'
  },
  notifications: {
    rcaCompleted: true,
    datasetCompleted: true,
    datasetFailed: true,
    systemErrors: true,
    newDatasetIndexed: false
  },
  appearance: {
    theme: 'System',
    compactMode: false
  }
};

export const fetchSettings = async (): Promise<ApplicationSettings> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Simulate fetching from a real backend.
      // In reality, this might be a GET /api/settings
      const stored = localStorage.getItem('incident_iq_settings');
      if (stored) {
        resolve(JSON.parse(stored));
      } else {
        resolve({ ...DEFAULT_SETTINGS });
      }
    }, 800);
  });
};

export const saveSettings = async (settings: ApplicationSettings): Promise<void> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Validate topK and minSimilarity manually here as a safety measure
      if (settings.ai.topK < 1 || settings.ai.topK > 20) {
        return reject(new Error('Top K must be between 1 and 20'));
      }
      if (settings.ai.minSimilarity < 0 || settings.ai.minSimilarity > 1) {
        return reject(new Error('Minimum similarity must be between 0 and 1'));
      }
      
      localStorage.setItem('incident_iq_settings', JSON.stringify(settings));
      resolve();
    }, 600);
  });
};

export const fetchSystemStatus = async (): Promise<SystemStatus> => {
  const response = await fetch('/api/health');
  const payload = await response.json();
  const dependencies = payload.dependencies || {};
  const state = (name: string, fallback: string) =>
    dependencies[name]?.status === 'available' ? fallback : 'Down';
  return {
    api: state('api', 'Operational') as SystemStatus['api'],
    vectorDatabase: state('pgvector', 'Operational') as SystemStatus['vectorDatabase'],
    embeddingService: state('embedding_model', 'Operational') as SystemStatus['embeddingService'],
    llmService: state('gemini', 'Operational') as SystemStatus['llmService'],
    knowledgeBase: payload.incident_records > 0 ? 'Ready' : 'Error',
    lastChecked: new Date().toLocaleTimeString(),
    details: dependencies,
  };
};

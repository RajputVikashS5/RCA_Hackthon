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
    llmModel: 'gemini-2.5-flash',
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

const DEFAULT_STATUS: SystemStatus = {
  api: 'Operational',
  vectorDatabase: 'Operational',
  embeddingService: 'Operational',
  llmService: 'Operational',
  knowledgeBase: 'Ready',
  lastChecked: new Date().toLocaleTimeString()
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
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ ...DEFAULT_STATUS, lastChecked: new Date().toLocaleTimeString() });
    }, 400);
  });
};

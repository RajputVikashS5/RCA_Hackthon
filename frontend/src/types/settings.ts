export interface AiRcaSettings {
  enabled: boolean;
  topK: number; // 1-20
  minSimilarity: number; // 0-1
  responseStyle: 'Brief' | 'Concise' | 'Detailed';
  showEvidence: boolean;
  showSimilarity: boolean;
  showUncertainty: boolean;
}

export interface RetrievalSettings {
  searchMethod: 'Semantic Search' | 'Hybrid Search' | 'Keyword Search';
  topK: number; // Linked to AiRcaSettings
  minSimilarity: number; // Linked to AiRcaSettings
  metadataFiltering: boolean;
  reranking: boolean; // Coming soon
}

export interface KnowledgeBaseSettings {
  activeDataset: string;
  recordCount: number;
  indexedCount: number;
  lastUpdated: string;
  embeddingStatus: 'Ready' | 'Processing' | 'Failed';
  duplicateHandling: 'Skip duplicates' | 'Replace existing records';
  missingRootCause: 'Keep record' | 'Skip record';
  missingResolution: 'Keep record' | 'Skip record';
}

export interface ProviderSettings {
  llmProvider: 'Configured Provider' | 'OpenAI' | 'Anthropic' | 'Google' | 'Local Model';
  llmModel: string;
  embeddingProvider: 'Local' | 'Cloud Provider';
  embeddingModel: string;
  llmStatus: 'Connected' | 'Not configured' | 'Error';
  embeddingStatus: 'Connected' | 'Not configured' | 'Error';
}

export interface PrivacySettings {
  storeAnalysisHistory: boolean;
  storeEvidence: boolean;
  evaluationData: boolean;
  sensitiveDataHandling: boolean;
  dataRetention: '30 Days' | '90 Days' | '180 Days' | '1 Year' | 'Indefinite';
}

export interface NotificationSettings {
  rcaCompleted: boolean;
  datasetCompleted: boolean;
  datasetFailed: boolean;
  systemErrors: boolean;
  newDatasetIndexed: boolean;
}

export interface AppearanceSettings {
  theme: 'Light' | 'Dark' | 'System';
  compactMode: boolean;
}

export interface SystemStatus {
  api: 'Operational' | 'Degraded' | 'Down' | 'Unknown';
  vectorDatabase: 'Operational' | 'Degraded' | 'Down' | 'Unknown';
  embeddingService: 'Operational' | 'Degraded' | 'Down' | 'Unknown';
  llmService: 'Operational' | 'Degraded' | 'Down' | 'Unknown';
  knowledgeBase: 'Ready' | 'Building' | 'Error' | 'Unknown';
  lastChecked: string;
}

export interface ApplicationSettings {
  ai: AiRcaSettings;
  retrieval: RetrievalSettings;
  knowledgeBase: KnowledgeBaseSettings;
  providers: ProviderSettings;
  privacy: PrivacySettings;
  notifications: NotificationSettings;
  appearance: AppearanceSettings;
}

import React from 'react';
import type { RetrievalSettings, AiRcaSettings } from '../../../types/settings';
import { SettingsSection, SettingsRow, Toggle, SettingsSelect, SettingsInput } from '../FormControls';

interface RetrievalSectionProps {
  data: RetrievalSettings;
  aiData: AiRcaSettings;
  onChange: <K extends keyof RetrievalSettings>(key: K, value: RetrievalSettings[K]) => void;
}

export const RetrievalSection: React.FC<RetrievalSectionProps> = ({ data, aiData, onChange }) => {
  return (
    <SettingsSection 
      id="retrieval" 
      title="Retrieval" 
      description="Configure how historical incidents are searched and ranked."
    >
      <SettingsRow title="Search Method" description="Algorithm used to find related historical incidents.">
        <SettingsSelect 
          value={data.searchMethod} 
          onChange={(e) => onChange('searchMethod', e.target.value as any)}
        >
          <option value="Semantic Search">Semantic Search</option>
          <option value="Hybrid Search" disabled>Hybrid Search (Unavailable)</option>
          <option value="Keyword Search" disabled>Keyword Search (Unavailable)</option>
        </SettingsSelect>
      </SettingsRow>

      <SettingsRow 
        title="Top K" 
        description="Number of incidents retrieved from vector search. Synced with AI & RCA settings."
      >
        <SettingsInput 
          type="number" 
          value={aiData.topK} 
          disabled
          style={{ width: '80px', backgroundColor: 'var(--canvas)' }}
        />
      </SettingsRow>

      <SettingsRow 
        title="Minimum Similarity" 
        description="Base retrieval threshold. Synced with AI & RCA settings."
      >
        <SettingsInput 
          type="number" 
          value={aiData.minSimilarity} 
          disabled
          style={{ width: '80px', backgroundColor: 'var(--canvas)' }}
        />
      </SettingsRow>

      <SettingsRow 
        title="Metadata Filtering" 
        description="Use service, component, severity, and category metadata when available."
      >
        <Toggle checked={data.metadataFiltering} onChange={(v) => onChange('metadataFiltering', v)} />
      </SettingsRow>

      <SettingsRow 
        title="Re-ranking" 
        description="Apply an additional relevance-ranking step after vector retrieval. (Coming soon)"
      >
        <Toggle checked={data.reranking} onChange={(v) => onChange('reranking', v)} disabled />
      </SettingsRow>
    </SettingsSection>
  );
};

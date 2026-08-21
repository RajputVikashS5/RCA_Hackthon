import React from 'react';
import type { AiRcaSettings } from '../../../types/settings';
import { SettingsSection, SettingsRow, Toggle, SettingsInput, SettingsSelect } from '../FormControls';

interface AiRcaSectionProps {
  data: AiRcaSettings;
  onChange: <K extends keyof AiRcaSettings>(key: K, value: AiRcaSettings[K]) => void;
}

export const AiRcaSection: React.FC<AiRcaSectionProps> = ({ data, onChange }) => {
  return (
    <SettingsSection 
      id="ai-rca" 
      title="AI & RCA" 
      description="Configure how Incident IQ analyzes incidents and generates evidence-grounded RCA summaries."
    >
      <SettingsRow 
        title="Enable AI RCA" 
        description="Allow Incident IQ to generate RCA summaries using retrieved historical incidents."
      >
        <Toggle checked={data.enabled} onChange={(v) => onChange('enabled', v)} />
      </SettingsRow>

      <SettingsRow 
        title="Top K Results" 
        description="Number of historical incidents retrieved for RCA analysis."
      >
        <SettingsSelect 
          value={data.topK} 
          onChange={(e) => onChange('topK', parseInt(e.target.value))}
          disabled={!data.enabled}
        >
          <option value={3}>3</option>
          <option value={5}>5</option>
          <option value={10}>10</option>
          <option value={15}>15</option>
          <option value={20}>20</option>
        </SettingsSelect>
      </SettingsRow>

      <SettingsRow 
        title="Minimum Similarity Score" 
        description="Historical incidents below this threshold may be treated as weak evidence."
      >
        <SettingsInput 
          type="number" 
          step="0.01" 
          min="0" 
          max="1" 
          value={data.minSimilarity} 
          onChange={(e) => onChange('minSimilarity', parseFloat(e.target.value))}
          disabled={!data.enabled}
          style={{ width: '80px' }}
        />
      </SettingsRow>

      <SettingsRow 
        title="Response Style" 
        description="Detail level of generated RCA summaries."
      >
        <SettingsSelect 
          value={data.responseStyle} 
          onChange={(e) => onChange('responseStyle', e.target.value as any)}
          disabled={!data.enabled}
        >
          <option value="Brief">Brief</option>
          <option value="Concise">Concise</option>
          <option value="Detailed">Detailed</option>
        </SettingsSelect>
      </SettingsRow>

      <SettingsRow 
        title="Show Historical Evidence" 
        description="Display the historical incidents supporting each RCA."
      >
        <Toggle checked={data.showEvidence} onChange={(v) => onChange('showEvidence', v)} disabled={!data.enabled} />
      </SettingsRow>

      <SettingsRow 
        title="Show Similarity Scores" 
        description="Display semantic similarity scores for retrieved incidents."
      >
        <Toggle checked={data.showSimilarity} onChange={(v) => onChange('showSimilarity', v)} disabled={!data.enabled || !data.showEvidence} />
      </SettingsRow>

      <SettingsRow 
        title="Always Show Uncertainty" 
        description="Clearly communicate when historical evidence is incomplete or conflicting."
      >
        <Toggle checked={data.showUncertainty} onChange={(v) => onChange('showUncertainty', v)} disabled={!data.enabled} />
      </SettingsRow>
    </SettingsSection>
  );
};

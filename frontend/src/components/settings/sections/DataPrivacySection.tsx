import React from 'react';
import type { PrivacySettings } from '../../../types/settings';
import { SettingsSection, SettingsRow, Toggle, SettingsSelect } from '../FormControls';

interface DataPrivacySectionProps {
  data: PrivacySettings;
  onChange: <K extends keyof PrivacySettings>(key: K, value: PrivacySettings[K]) => void;
}

export const DataPrivacySection: React.FC<DataPrivacySectionProps> = ({ data, onChange }) => {
  return (
    <SettingsSection 
      id="data-privacy" 
      title="Data & Privacy" 
      description="Control how incident information and RCA analysis data are handled."
    >
      <SettingsRow 
        title="Store Analysis History" 
        description="Store completed RCA analyses for later review."
      >
        <Toggle checked={data.storeAnalysisHistory} onChange={(v) => onChange('storeAnalysisHistory', v)} />
      </SettingsRow>

      <SettingsRow 
        title="Store Retrieved Evidence" 
        description="Store references to historical incidents used during RCA generation."
      >
        <Toggle checked={data.storeEvidence} onChange={(v) => onChange('storeEvidence', v)} />
      </SettingsRow>

      <SettingsRow 
        title="Use Analysis Data for Evaluation" 
        description="Allow anonymized analysis results to be included in RAG evaluation."
      >
        <Toggle checked={data.evaluationData} onChange={(v) => onChange('evaluationData', v)} />
      </SettingsRow>

      <SettingsRow 
        title="Sensitive Data Handling" 
        description="Apply configured protections when processing potentially sensitive incident content."
      >
        <Toggle checked={data.sensitiveDataHandling} onChange={(v) => onChange('sensitiveDataHandling', v)} />
      </SettingsRow>

      <SettingsRow 
        title="Data Retention" 
        description="How long to keep incident and analysis data."
      >
        <SettingsSelect 
          value={data.dataRetention} 
          onChange={(e) => onChange('dataRetention', e.target.value as any)}
        >
          <option value="30 Days" disabled>30 Days (Coming soon)</option>
          <option value="90 Days">90 Days</option>
          <option value="180 Days" disabled>180 Days (Coming soon)</option>
          <option value="1 Year" disabled>1 Year (Coming soon)</option>
          <option value="Indefinite" disabled>Indefinite (Coming soon)</option>
        </SettingsSelect>
      </SettingsRow>
    </SettingsSection>
  );
};

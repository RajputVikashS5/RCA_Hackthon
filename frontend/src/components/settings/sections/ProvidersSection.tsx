import React from 'react';
import type { ProviderSettings } from '../../../types/settings';
import { SettingsSection, SettingsRow, SettingsSelect, SettingsInput } from '../FormControls';

interface ProvidersSectionProps {
  data: ProviderSettings;
  onChange: <K extends keyof ProviderSettings>(key: K, value: ProviderSettings[K]) => void;
}

export const ProvidersSection: React.FC<ProvidersSectionProps> = ({ data, onChange }) => {
  return (
    <SettingsSection 
      id="providers" 
      title="AI Providers" 
      description="Configure the models used for embeddings and RCA generation."
    >
      <SettingsRow title="LLM Provider">
        <SettingsSelect value={data.llmProvider} onChange={(e) => onChange('llmProvider', e.target.value as any)}>
          <option value="Configured Provider">Configured Provider</option>
          <option value="OpenAI">OpenAI</option>
          <option value="Anthropic">Anthropic</option>
          <option value="Google">Google</option>
          <option value="Local Model">Local Model</option>
        </SettingsSelect>
      </SettingsRow>

      <SettingsRow title="LLM Model">
        <SettingsInput 
          value={data.llmModel} 
          onChange={(e) => onChange('llmModel', e.target.value)} 
          placeholder="e.g. gpt-4o-mini"
        />
      </SettingsRow>

      <SettingsRow title="Embedding Provider">
        <SettingsSelect value={data.embeddingProvider} onChange={(e) => onChange('embeddingProvider', e.target.value as any)}>
          <option value="Local">Local</option>
          <option value="Cloud Provider">Cloud Provider</option>
        </SettingsSelect>
      </SettingsRow>

      <SettingsRow title="Embedding Model">
        <SettingsInput 
          value={data.embeddingModel} 
          onChange={(e) => onChange('embeddingModel', e.target.value)} 
          placeholder="e.g. all-MiniLM-L6-v2"
        />
      </SettingsRow>

      <div style={{ marginTop: '16px', padding: '16px', backgroundColor: 'var(--canvas)', borderRadius: 'var(--rounded-md)' }}>
        <h4 className="title-sm" style={{ marginBottom: '16px' }}>API Configuration</h4>
        <p className="body-sm text-muted" style={{ marginBottom: '16px' }}>API credentials are stored securely and are never displayed.</p>
        
        <SettingsRow title="API Key">
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <span style={{ fontFamily: 'var(--font-code)', fontSize: '14px', color: 'var(--muted)' }}>••••••••••••••••</span>
            <button className="btn-secondary" style={{ padding: '4px 12px', fontSize: '12px' }}>Update Key</button>
          </div>
        </SettingsRow>
      </div>

      <div style={{ marginTop: '8px', padding: '16px', border: '1px solid var(--border)', borderRadius: 'var(--rounded-md)' }}>
        <h4 className="title-sm" style={{ marginBottom: '16px' }}>Connection Status</h4>
        <div style={{ display: 'flex', gap: '48px' }}>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '4px' }}>LLM Service</div>
            <div style={{ fontSize: '14px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px', color: data.llmStatus === 'Connected' ? 'var(--success)' : 'var(--error)' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'currentColor' }}></span>
              {data.llmStatus}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '4px' }}>Embedding Service</div>
            <div style={{ fontSize: '14px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px', color: data.embeddingStatus === 'Connected' ? 'var(--success)' : 'var(--error)' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'currentColor' }}></span>
              {data.embeddingStatus}
            </div>
          </div>
        </div>
      </div>

    </SettingsSection>
  );
};

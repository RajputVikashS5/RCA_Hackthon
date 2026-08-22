import React from 'react';
import type { KnowledgeBaseSettings } from '../../../types/settings';
import { SettingsSection, SettingsRow, SettingsSelect } from '../FormControls';

interface KnowledgeBaseSectionProps {
  data: KnowledgeBaseSettings;
  onChange: <K extends keyof KnowledgeBaseSettings>(key: K, value: KnowledgeBaseSettings[K]) => void;
}

export const KnowledgeBaseSection: React.FC<KnowledgeBaseSectionProps> = ({ data, onChange }) => {
  return (
    <SettingsSection 
      id="knowledge-base" 
      title="Knowledge Base" 
      description="Manage the historical incident data used by the RCA assistant."
    >
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        padding: '20px',
        backgroundColor: 'var(--canvas)',
        borderRadius: 'var(--rounded-md)',
        border: '1px solid var(--border)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '13px', color: 'var(--muted)', fontWeight: 600, letterSpacing: '0.5px', textTransform: 'uppercase' }}>Active Dataset</div>
            <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--ink)' }}>{data.activeDataset}</div>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '13px' }}>View Dataset</button>
            <button className="btn-primary" style={{ padding: '6px 12px', fontSize: '13px' }}>Upload Dataset</button>
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: '48px', marginTop: '8px' }}>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '4px' }}>Records</div>
            <div style={{ fontSize: '20px', fontWeight: 700 }}>{data.recordCount.toLocaleString()}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '4px' }}>Indexed Records</div>
            <div style={{ fontSize: '20px', fontWeight: 700 }}>{data.indexedCount.toLocaleString()}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '4px' }}>Last Updated</div>
            <div style={{ fontSize: '14px', fontWeight: 500, marginTop: '4px' }}>{data.lastUpdated}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '4px' }}>Embedding Status</div>
            <div style={{ fontSize: '14px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px', color: data.embeddingStatus === 'Ready' ? 'var(--success)' : 'var(--warning)', marginTop: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'currentColor' }}></span>
              {data.embeddingStatus}
            </div>
          </div>
        </div>
        
        <div style={{ marginTop: '8px' }}>
          <button className="btn-secondary" style={{ width: '100%' }}>Rebuild Index</button>
        </div>
      </div>

      <div style={{ marginTop: '16px' }}>
        <h4 className="title-sm" style={{ marginBottom: '16px' }}>Dataset Processing Settings</h4>
        
        <SettingsRow title="Duplicate Handling">
          <SettingsSelect value={data.duplicateHandling} onChange={(e) => onChange('duplicateHandling', e.target.value as any)}>
            <option value="Skip duplicates">Skip duplicates</option>
            <option value="Replace existing records">Replace existing records</option>
          </SettingsSelect>
        </SettingsRow>
        
        <SettingsRow title="Missing Root Cause">
          <SettingsSelect value={data.missingRootCause} onChange={(e) => onChange('missingRootCause', e.target.value as any)}>
            <option value="Keep record">Keep record</option>
            <option value="Skip record">Skip record</option>
          </SettingsSelect>
        </SettingsRow>
        
        <SettingsRow title="Missing Resolution">
          <SettingsSelect value={data.missingResolution} onChange={(e) => onChange('missingResolution', e.target.value as any)}>
            <option value="Keep record">Keep record</option>
            <option value="Skip record">Skip record</option>
          </SettingsSelect>
        </SettingsRow>
      </div>

    </SettingsSection>
  );
};

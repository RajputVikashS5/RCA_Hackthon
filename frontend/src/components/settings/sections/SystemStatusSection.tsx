import React, { useState, useEffect } from 'react';
import type { SystemStatus } from '../../../types/settings';
import { fetchSystemStatus } from '../../../services/settingsService';
import { SettingsSection } from '../FormControls';

export const SystemStatusSection: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadStatus = async () => {
    setRefreshing(true);
    try {
      const data = await fetchSystemStatus();
      setStatus(data);
    } catch (e) {
      console.error(e);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const StatusIndicator = ({ state }: { state: string }) => {
    let color = 'var(--muted)';
    if (state === 'Operational' || state === 'Ready') color = 'var(--success)';
    if (state === 'Degraded' || state === 'Building') color = 'var(--warning)';
    if (state === 'Down' || state === 'Error') color = 'var(--error)';
    
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', fontWeight: 500, color }}>
        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'currentColor' }}></span>
        {state}
      </div>
    );
  };

  return (
    <SettingsSection 
      id="system-status" 
      title="System Status" 
      description="Check the services required for Incident IQ analysis."
    >
      <div style={{ backgroundColor: 'var(--canvas)', borderRadius: 'var(--rounded-md)', border: '1px solid var(--border)', padding: '16px' }}>
        {status ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)' }}>API</span>
              <StatusIndicator state={status.api} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)' }}>Vector Database</span>
              <StatusIndicator state={status.vectorDatabase} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)' }}>Embedding Service</span>
              <StatusIndicator state={status.embeddingService} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)' }}>LLM Service</span>
              <StatusIndicator state={status.llmService} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)' }}>Knowledge Base</span>
              <StatusIndicator state={status.knowledgeBase} />
            </div>
          </div>
        ) : (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)', fontSize: '14px' }}>Loading status...</div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
        <span style={{ fontSize: '12px', color: 'var(--muted)' }}>
          {status ? `Last checked at ${status.lastChecked}` : 'Checking...'}
        </span>
        <button 
          className="btn-secondary" 
          onClick={loadStatus} 
          disabled={refreshing}
          style={{ padding: '6px 12px', fontSize: '12px' }}
        >
          {refreshing ? 'Refreshing...' : 'Refresh Status'}
        </button>
      </div>
    </SettingsSection>
  );
};

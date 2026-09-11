import React, { useState, useEffect } from 'react';
import type { ApplicationSettings } from '../types/settings';
import { fetchSettings, saveSettings } from '../services/settingsService';
import { SettingsSidebar } from '../components/settings/SettingsSidebar';

// Sections will be imported here
import { AiRcaSection } from '../components/settings/sections/AiRcaSection';
import { RetrievalSection } from '../components/settings/sections/RetrievalSection';
import { KnowledgeBaseSection } from '../components/settings/sections/KnowledgeBaseSection';
import { ProvidersSection } from '../components/settings/sections/ProvidersSection';
import { DataPrivacySection } from '../components/settings/sections/DataPrivacySection';
import { NotificationsSection } from '../components/settings/sections/NotificationsSection';
import { AppearanceSection } from '../components/settings/sections/AppearanceSection';
import { SystemStatusSection } from '../components/settings/sections/SystemStatusSection';

interface SettingsProps {
  setUnsavedChanges: (val: boolean) => void;
  unsavedChanges: boolean;
}

const Settings: React.FC<SettingsProps> = ({ setUnsavedChanges, unsavedChanges }) => {
  const [activeSection, setActiveSection] = useState('ai-rca');
  const [settings, setSettings] = useState<ApplicationSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadSettings = async () => {
      try {
        const data = await fetchSettings();
        if (isMounted) {
          setSettings(data);
          setLoading(false);
        }
      } catch {
        if (isMounted) {
          setError('Unable to load settings.');
          setLoading(false);
        }
      }
    };
    loadSettings();
    return () => { isMounted = false; };
  }, []);

  // Update Settings helper
  const updateSettings = <K extends keyof ApplicationSettings>(
    category: K, 
    key: keyof ApplicationSettings[K], 
    value: any
  ) => {
    if (!settings) return;
    setSettings({
      ...settings,
      [category]: {
        ...settings[category],
        [key]: value
      }
    });
    setUnsavedChanges(true);
    setSuccessMsg(null);
  };

  const handleSave = async () => {
    if (!settings) return;
    
    // Validation
    if (settings.ai.topK < 1 || settings.ai.topK > 20) {
      setError('Top K must be between 1 and 20.');
      return;
    }
    if (settings.ai.minSimilarity < 0 || settings.ai.minSimilarity > 1) {
      setError('Similarity score must be between 0 and 1.');
      return;
    }

    setSaving(true);
    setError(null);
    try {
      await saveSettings(settings);
      setUnsavedChanges(false);
      setSuccessMsg('Settings saved successfully.');
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Unable to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  // Scroll spy effect for sidebar
  useEffect(() => {
    const handleScroll = () => {
      const sections = ['ai-rca', 'retrieval', 'knowledge-base', 'providers', 'data-privacy', 'notifications', 'appearance', 'system-status'];
      for (const section of sections) {
        const el = document.getElementById(section);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top >= 0 && rect.top <= 300) {
            setActiveSection(section);
            break;
          }
        }
      }
    };
    const contentArea = document.querySelector('.content-area');
    if (contentArea) contentArea.addEventListener('scroll', handleScroll);
    return () => contentArea?.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div style={{ paddingBottom: '100px', maxWidth: '1200px' }}>
      <header style={{ marginBottom: '32px' }}>
        <h1 className="display-lg" style={{ marginBottom: '8px' }}>Settings</h1>
        <p className="body-md" style={{ color: 'var(--muted)' }}>
          Configure Incident IQ, your RCA assistant, and system preferences.
        </p>
      </header>

      {error && (
        <div className="card" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--error)', color: 'var(--error)', marginBottom: '24px', padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{error}</span>
          {!settings && <button className="btn-primary" onClick={() => window.location.reload()}>Try Again</button>}
        </div>
      )}

      {loading || !settings ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px', color: 'var(--muted)' }}>
          Loading settings...
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '48px', alignItems: 'flex-start' }}>
          
          <SettingsSidebar activeSection={activeSection} onSelectSection={setActiveSection} />

          <div style={{ flex: 1, maxWidth: '700px' }}>
            <AiRcaSection data={settings.ai} onChange={(k, v) => updateSettings('ai', k, v)} />
            <RetrievalSection data={settings.retrieval} aiData={settings.ai} onChange={(k, v) => updateSettings('retrieval', k, v)} />
            <KnowledgeBaseSection data={settings.knowledgeBase} onChange={(k, v) => updateSettings('knowledgeBase', k, v)} />
            <ProvidersSection data={settings.providers} onChange={(k, v) => updateSettings('providers', k, v)} />
            <DataPrivacySection data={settings.privacy} onChange={(k, v) => updateSettings('privacy', k, v)} />
            <NotificationsSection data={settings.notifications} onChange={(k, v) => updateSettings('notifications', k, v)} />
            <AppearanceSection data={settings.appearance} onChange={(k, v) => updateSettings('appearance', k, v)} />
            <SystemStatusSection />
          </div>

        </div>
      )}

      {/* Sticky Footer for Saving */}
      {settings && (
        <div style={{
          position: 'fixed',
          bottom: 0, left: '260px', right: 0,
          backgroundColor: 'var(--canvas)',
          borderTop: '1px solid var(--border)',
          padding: '16px 48px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          zIndex: 100
        }}>
          <div>
            {successMsg && <span style={{ color: 'var(--success)', fontWeight: 500, fontSize: '14px' }}>{successMsg}</span>}
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            {unsavedChanges && (
              <button 
                className="btn-secondary" 
                disabled={saving}
                onClick={() => {
                  if (confirm('Discard unsaved changes?')) {
                    window.location.reload();
                  }
                }}
              >
                Cancel
              </button>
            )}
            <button 
              className="btn-primary" 
              onClick={handleSave}
              disabled={!unsavedChanges || saving}
              style={{ opacity: (!unsavedChanges || saving) ? 0.6 : 1 }}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;

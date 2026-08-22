import React from 'react';
import type { AppearanceSettings } from '../../../types/settings';
import { SettingsSection, SettingsRow, SettingsSelect, Toggle } from '../FormControls';

interface AppearanceSectionProps {
  data: AppearanceSettings;
  onChange: <K extends keyof AppearanceSettings>(key: K, value: AppearanceSettings[K]) => void;
}

export const AppearanceSection: React.FC<AppearanceSectionProps> = ({ data, onChange }) => {
  return (
    <SettingsSection 
      id="appearance" 
      title="Appearance" 
      description="Customize the Incident IQ interface."
    >
      <SettingsRow title="Theme">
        <SettingsSelect 
          value={data.theme} 
          onChange={(e) => onChange('theme', e.target.value as any)}
        >
          <option value="Light">Light</option>
          <option value="Dark" disabled>Dark (Coming soon)</option>
          <option value="System">System</option>
        </SettingsSelect>
      </SettingsRow>

      <SettingsRow title="Accent Color">
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: 'var(--brand-green)', border: '2px solid white', boxShadow: '0 0 0 1px var(--border)' }}></div>
          <span style={{ fontSize: '14px', color: 'var(--ink)' }}>Default Green</span>
        </div>
      </SettingsRow>

      <SettingsRow title="Compact Mode" description="Reduce spacing and increase information density. (Coming soon)">
        <Toggle checked={data.compactMode} onChange={(v) => onChange('compactMode', v)} disabled />
      </SettingsRow>
    </SettingsSection>
  );
};

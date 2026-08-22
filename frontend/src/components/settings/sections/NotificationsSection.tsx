import React from 'react';
import type { NotificationSettings } from '../../../types/settings';
import { SettingsSection, SettingsRow, Toggle } from '../FormControls';

interface NotificationsSectionProps {
  data: NotificationSettings;
  onChange: <K extends keyof NotificationSettings>(key: K, value: NotificationSettings[K]) => void;
}

export const NotificationsSection: React.FC<NotificationsSectionProps> = ({ data, onChange }) => {
  return (
    <SettingsSection 
      id="notifications" 
      title="Notifications" 
      description="Choose which Incident IQ events should generate notifications. (Preferences saved for future integration)"
    >
      <SettingsRow title="RCA Analysis Completed">
        <Toggle checked={data.rcaCompleted} onChange={(v) => onChange('rcaCompleted', v)} />
      </SettingsRow>

      <SettingsRow title="Dataset Processing Completed">
        <Toggle checked={data.datasetCompleted} onChange={(v) => onChange('datasetCompleted', v)} />
      </SettingsRow>

      <SettingsRow title="Dataset Processing Failed">
        <Toggle checked={data.datasetFailed} onChange={(v) => onChange('datasetFailed', v)} />
      </SettingsRow>

      <SettingsRow title="System Errors">
        <Toggle checked={data.systemErrors} onChange={(v) => onChange('systemErrors', v)} />
      </SettingsRow>

      <SettingsRow title="New Dataset Indexed">
        <Toggle checked={data.newDatasetIndexed} onChange={(v) => onChange('newDatasetIndexed', v)} />
      </SettingsRow>
    </SettingsSection>
  );
};

import React from 'react';

const SETTINGS_SECTIONS = [
  { id: 'ai-rca', label: 'AI & RCA' },
  { id: 'retrieval', label: 'Retrieval' },
  { id: 'knowledge-base', label: 'Knowledge Base' },
  { id: 'providers', label: 'AI Providers' },
  { id: 'data-privacy', label: 'Data & Privacy' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'appearance', label: 'Appearance' },
  { id: 'system-status', label: 'System Status' },
];

interface SettingsSidebarProps {
  activeSection: string;
  onSelectSection: (id: string) => void;
}

export const SettingsSidebar: React.FC<SettingsSidebarProps> = ({ activeSection, onSelectSection }) => {
  return (
    <div style={{
      width: '240px',
      position: 'sticky',
      top: '24px',
      alignSelf: 'flex-start',
      display: 'flex',
      flexDirection: 'column',
      gap: '4px'
    }}>
      {SETTINGS_SECTIONS.map(section => (
        <button
          key={section.id}
          onClick={() => {
            onSelectSection(section.id);
            const el = document.getElementById(section.id);
            if (el) {
              el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          }}
          style={{
            textAlign: 'left',
            padding: '10px 16px',
            border: 'none',
            background: activeSection === section.id ? 'white' : 'transparent',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: activeSection === section.id ? 600 : 500,
            color: activeSection === section.id ? 'var(--ink)' : 'var(--muted)',
            boxShadow: activeSection === section.id ? '0 1px 3px rgba(0,0,0,0.05)' : 'none',
            transition: 'all 0.2s'
          }}
        >
          {section.label}
        </button>
      ))}
    </div>
  );
};

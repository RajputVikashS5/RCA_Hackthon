import React from 'react';

// --- Toggle Component ---
interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

export const Toggle: React.FC<ToggleProps> = ({ checked, onChange, disabled }) => {
  return (
    <button
      type="button"
      onClick={() => !disabled && onChange(!checked)}
      style={{
        width: '40px',
        height: '24px',
        borderRadius: '12px',
        backgroundColor: checked ? 'var(--brand-green)' : 'var(--border)',
        position: 'relative',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.6 : 1,
        border: 'none',
        transition: 'background-color 0.2s',
        display: 'flex',
        alignItems: 'center',
        padding: '0 2px'
      }}
    >
      <div
        style={{
          width: '20px',
          height: '20px',
          backgroundColor: 'white',
          borderRadius: '50%',
          boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
          transition: 'transform 0.2s',
          transform: checked ? 'translateX(16px)' : 'translateX(0)',
        }}
      />
    </button>
  );
};

// --- Settings Section/Card Component ---
interface SettingsSectionProps {
  id: string;
  title: string;
  description: string;
  children: React.ReactNode;
}

export const SettingsSection: React.FC<SettingsSectionProps> = ({ id, title, description, children }) => (
  <div id={id} className="card" style={{ marginBottom: '32px' }}>
    <div style={{ marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid var(--border)' }}>
      <h3 className="title-md" style={{ marginBottom: '4px' }}>{title}</h3>
      <p className="body-md text-muted">{description}</p>
    </div>
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {children}
    </div>
  </div>
);

// --- Settings Row Component ---
interface SettingsRowProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  vertical?: boolean;
}

export const SettingsRow: React.FC<SettingsRowProps> = ({ title, description, children, vertical = false }) => (
  <div style={{ 
    display: 'flex', 
    flexDirection: vertical ? 'column' : 'row', 
    justifyContent: vertical ? 'flex-start' : 'space-between', 
    alignItems: vertical ? 'flex-start' : 'center',
    gap: vertical ? '12px' : '24px'
  }}>
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)' }}>{title}</div>
      {description && <div style={{ fontSize: '13px', color: 'var(--muted)', marginTop: '4px' }}>{description}</div>}
    </div>
    <div style={{ minWidth: vertical ? '100%' : '200px', display: 'flex', justifyContent: vertical ? 'flex-start' : 'flex-end' }}>
      {children}
    </div>
  </div>
);

// --- Inputs & Selects ---
export const SettingsSelect = (props: React.SelectHTMLAttributes<HTMLSelectElement>) => (
  <select className="input-field" {...props} style={{ width: 'auto', minWidth: '100%', ...props.style }}>
    {props.children}
  </select>
);

export const SettingsInput = (props: React.InputHTMLAttributes<HTMLInputElement>) => (
  <input className="input-field" {...props} style={{ width: '100%', ...props.style }} />
);

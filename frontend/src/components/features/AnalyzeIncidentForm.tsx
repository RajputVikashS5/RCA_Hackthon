import React from 'react';

interface AnalyzeIncidentFormProps {
  description: string;
  setDescription: (v: string) => void;
  component: string;
  setComponent: (v: string) => void;
  severity: string;
  setSeverity: (v: string) => void;
  environment: string;
  setEnvironment: (v: string) => void;
  incidentType: string;
  setIncidentType: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  error: string | null;
}

const AnalyzeIncidentForm: React.FC<AnalyzeIncidentFormProps> = ({
  description, setDescription, component, setComponent,
  severity, setSeverity, environment, setEnvironment,
  incidentType, setIncidentType, onSubmit, loading, error
}) => {
  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title" style={{ color: 'var(--ink)' }}>Analyze New Incident</span>
      </div>
      
      <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label className="caption">Incident Description</label>
          <textarea 
            className="input-field" 
            style={{ height: '100px', resize: 'vertical' }}
            placeholder="Example: Payment checkout is failing with HTTP 500 errors in production."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-3">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label className="caption">Component</label>
            <input className="input-field" value={component} onChange={e => setComponent(e.target.value)} placeholder="e.g. Payment Service" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label className="caption">Severity</label>
            <select className="input-field" value={severity} onChange={e => setSeverity(e.target.value)}>
              <option value="">Select...</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label className="caption">Environment</label>
            <select className="input-field" value={environment} onChange={e => setEnvironment(e.target.value)}>
              <option value="">Select...</option>
              <option value="Production">Production</option>
              <option value="Staging">Staging</option>
              <option value="QA">QA</option>
              <option value="Development">Development</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label className="caption">Incident Type</label>
          <input className="input-field" value={incidentType} onChange={e => setIncidentType(e.target.value)} placeholder="e.g. Service Outage" />
        </div>

        {error && <div className="text-error body-sm">{error}</div>}
        
        <button type="submit" className="btn-primary" style={{ alignSelf: 'flex-start', marginTop: '8px' }} disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Incident'}
        </button>
      </form>
    </div>
  );
};

export default AnalyzeIncidentForm;

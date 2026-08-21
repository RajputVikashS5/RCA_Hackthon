import React from 'react';
import { Database, CheckCircle, AlertCircle } from 'lucide-react';

interface ZenodoTestCardProps {
  onTest: () => void;
  loading: boolean;
  result: any;
  error: string | null;
}

const ZenodoTestCard: React.FC<ZenodoTestCardProps> = ({ onTest, loading, result, error }) => {
  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title" style={{ color: 'var(--ink)' }}>Zenodo Connection</span>
      </div>
      
      <p className="body-sm text-muted" style={{ marginBottom: '24px' }}>
        Read-only test for the configured public Zenodo record.
      </p>

      <button 
        className="btn-secondary" 
        onClick={onTest} 
        disabled={loading}
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
      >
        <Database size={16} />
        {loading ? 'Testing...' : 'Test Connection'}
      </button>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--error)', marginTop: '16px', fontSize: '13px' }}>
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '24px', padding: '16px', backgroundColor: 'var(--canvas)', borderRadius: '8px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <CheckCircle size={16} className="text-success" />
            <span style={{ fontSize: '14px', fontWeight: '600' }}>Connection Successful</span>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Record:</span>
              <span style={{ fontWeight: '500', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{result.recordTitle}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Files Found:</span>
              <span style={{ fontWeight: '500' }}>{result.filesFound}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Sample Records:</span>
              <span style={{ fontWeight: '500' }}>{result.sampleRecords?.length || 0}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ZenodoTestCard;

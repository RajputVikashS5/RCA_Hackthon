import React, { useState } from 'react';
import './App.css';
import { analyzeIncident, getIngestionStatus, getZenodoStatus, inspectZenodoDataset } from './api';

function App() {
  const [description, setDescription] = useState('');
  const [component, setComponent] = useState('');
  const [severity, setSeverity] = useState('');
  const [environment, setEnvironment] = useState('');
  const [incidentType, setIncidentType] = useState('');
  
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [zenodoLoading, setZenodoLoading] = useState(false);
  const [zenodoResult, setZenodoResult] = useState<any>(null);
  const [inspectionResult, setInspectionResult] = useState<any>(null);
  const [ingestionResult, setIngestionResult] = useState<any>(null);
  const [zenodoError, setZenodoError] = useState<string | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) {
      setAnalysisError('Enter an incident description before analyzing.');
      return;
    }
    setAnalysisError(null);
    setAnalysisLoading(true);
    setAnalysisResult(null);
    try {
      const result = await analyzeIncident({
        description: description.trim(),
        component: component.trim() || undefined,
        severity: severity || undefined,
        environment: environment || undefined,
        incident_type: incidentType.trim() || undefined,
      });
      setAnalysisResult(result);
    } catch (err: any) {
      setAnalysisError(err.message);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const handleZenodoTest = async () => {
    setZenodoLoading(true);
    setZenodoError(null);
    setZenodoResult(null);
    try {
      setZenodoResult(await getZenodoStatus());
    } catch (err: any) {
      setZenodoError(err.message);
    } finally {
      setZenodoLoading(false);
    }
  };

  const handleInspect = async () => {
    setZenodoLoading(true);
    setZenodoError(null);
    try {
      setInspectionResult(await inspectZenodoDataset());
    } catch (err: any) {
      setZenodoError(err.message);
    } finally {
      setZenodoLoading(false);
    }
  };

  const handleIngestionStatus = async () => {
    setZenodoLoading(true);
    setZenodoError(null);
    try {
      setIngestionResult(await getIngestionStatus());
    } catch (err: any) {
      setZenodoError(err.message);
    } finally {
      setZenodoLoading(false);
    }
  };

  return (
    <>
      <nav className="top-nav container">
        <div className="top-nav-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="var(--ink)" strokeWidth="4" fill="none"/>
          </svg>
          Enterprise RCA Assistant
        </div>
      </nav>

      <main>
        <section className="section container">
          <div className="hero-band" style={{ padding: '48px 0', textAlign: 'center' }}>
            <h1 className="display-lg">Resolve incidents faster</h1>
            <p className="title-md" style={{ color: 'var(--muted)', marginTop: '16px' }}>
              Analyze a new incident and retrieve the strongest evidence for likely root cause and resolution.
            </p>
          </div>

          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            {/* Main Column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '48px' }}>
              <div className="product-mockup-card">
                <h3 className="title-lg" style={{ marginBottom: '12px' }}>Dataset Connection</h3>
                <p className="body-sm text-muted">Zenodo is the historical source for offline ingestion, not the live knowledge base.</p>
                <button type="button" className="button-primary" style={{ marginTop: '20px' }} onClick={handleZenodoTest} disabled={zenodoLoading}>
                  {zenodoLoading ? 'Checking dataset...' : 'Check Dataset Status'}
                </button>
                <button type="button" className="button-secondary" style={{ marginTop: '20px', marginLeft: '12px' }} onClick={handleInspect} disabled={zenodoLoading}>Inspect Dataset</button>
                <button type="button" className="button-secondary" style={{ marginTop: '20px', marginLeft: '12px' }} onClick={handleIngestionStatus} disabled={zenodoLoading}>Test Ingestion Status</button>
                {zenodoError && <div style={{ color: 'var(--error)', marginTop: '16px' }} className="body-sm">{zenodoError}</div>}
                {zenodoResult && (
                  <div style={{ marginTop: '20px' }}>
                    <div className="body-sm"><strong>Status:</strong> {zenodoResult.metadata_access}</div>
                    <div className="body-sm"><strong>Record:</strong> {zenodoResult.title}</div>
                    <div className="body-sm"><strong>Version:</strong> {zenodoResult.version || 'Not reported'}</div>
                    <div className="body-sm"><strong>Archive:</strong> {zenodoResult.dataset_archive?.name || 'Unavailable'}</div>
                    <div className="body-sm"><strong>Archive available:</strong> {zenodoResult.dataset_archive?.available ? 'Yes' : 'No'}</div>
                    <div className="body-sm"><strong>Files:</strong> {zenodoResult.files?.length || 0}</div>
                    {inspectionResult && (
                      <div style={{ marginTop: '16px' }}>
                        <div className="body-sm"><strong>Collections:</strong> {inspectionResult.collections?.join(', ') || 'None discovered'}</div>
                        <div className="body-sm"><strong>Sample records:</strong> {inspectionResult.sample_count || 0}</div>
                        <div className="body-sm"><strong>Fields:</strong> {inspectionResult.fields?.join(', ') || 'None discovered'}</div>
                      </div>
                    )}
                    {ingestionResult && (
                      <div style={{ marginTop: '16px' }}>
                        <div className="body-sm"><strong>Knowledge base:</strong> {ingestionResult.knowledge_base?.database || 'Unavailable'}</div>
                        <div className="body-sm"><strong>Indexed incidents:</strong> {ingestionResult.knowledge_base?.incident_records ?? 0}</div>
                        <div className="body-sm"><strong>Ingestion:</strong> {ingestionResult.status}</div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="product-mockup-card">
                <h3 className="title-lg" style={{ marginBottom: '24px' }}>Analyze New Incident</h3>
                <form onSubmit={handleAnalyze} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label className="caption">Incident Description</label>
                    <textarea 
                      className="text-input" 
                      style={{ height: '120px', resize: 'vertical' }}
                      placeholder="Example: Payment checkout is failing with HTTP 500 errors in production."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <label className="caption">Component</label>
                      <input className="text-input" value={component} onChange={e => setComponent(e.target.value)} placeholder="Payment Service" />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <label className="caption">Severity</label>
                      <select className="text-input" value={severity} onChange={e => setSeverity(e.target.value)}>
                        <option value="">Select...</option>
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                        <option value="Critical">Critical</option>
                      </select>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <label className="caption">Environment</label>
                      <select className="text-input" value={environment} onChange={e => setEnvironment(e.target.value)}>
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
                    <input className="text-input" value={incidentType} onChange={e => setIncidentType(e.target.value)} placeholder="Service Outage" />
                  </div>

                  {analysisError && <div style={{ color: 'var(--error)' }} className="body-md">{analysisError}</div>}
                  
                  <button type="submit" className="button-primary" style={{ alignSelf: 'flex-start' }} disabled={analysisLoading}>
                    {analysisLoading ? 'Analyzing...' : 'Analyze Incident'}
                  </button>
                </form>
              </div>

              {analysisResult && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '48px' }}>
                  
                  <div>
                    <h3 className="title-lg" style={{ marginBottom: '24px' }}>RCA Result</h3>
                    <div className="feature-grid-3">
                      <div className="feature-icon-card">
                        <div className="caption text-muted">Likely Root Cause</div>
                        <div className="title-md">{analysisResult.root_cause || "Unavailable"}</div>
                      </div>
                      <div className="feature-icon-card">
                        <div className="caption text-muted">Recommended Resolution</div>
                        <div className="title-md">{analysisResult.resolution || "Unavailable"}</div>
                      </div>
                      <div className="feature-icon-card">
                        <div className="caption text-muted">Evidence Strength</div>
                        <div className="title-md">{analysisResult.evidence_strength || "Unavailable"}</div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="title-lg" style={{ marginBottom: '24px' }}>AI RCA Summary</h3>
                    <div className="feature-card" style={{ backgroundColor: 'var(--canvas)', border: '1px solid var(--hairline)' }}>
                      <p className="body-md">{analysisResult.summary || "No summary was returned by the model."}</p>
                    </div>
                    {analysisResult.evidence_strength === "Insufficient" && (
                      <div style={{ marginTop: '16px', padding: '16px', backgroundColor: 'var(--surface-soft)', color: 'var(--warning)', borderRadius: '8px' }} className="body-sm">
                        ⚠️ Insufficient historical evidence was found to determine a reliable root cause.
                      </div>
                    )}
                  </div>

                  <div>
                    <h3 className="title-lg" style={{ marginBottom: '24px' }}>Top Similar Incidents</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {analysisResult.similar_incidents?.length > 0 ? analysisResult.similar_incidents.map((inc: any, i: number) => (
                        <div key={i} className="feature-card" style={{ backgroundColor: 'var(--canvas)', border: '1px solid var(--hairline)' }}>
                          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '8px' }}>
                            <span className="badge-pill" style={{ backgroundColor: 'var(--surface-soft)' }}>{inc.incident_id || 'Unknown'}</span>
                            <span className="badge-pill orange">Similarity {parseFloat(inc.similarity_score || 0).toFixed(3)}</span>
                          </div>
                          <h4 className="title-md">{inc.title || 'Untitled Incident'}</h4>
                          <p className="body-md text-muted" style={{ margin: '8px 0' }}>{inc.description}</p>
                          <div className="body-sm"><strong>Root Cause:</strong> {inc.root_cause}</div>
                          <div className="body-sm" style={{ marginTop: '4px' }}><strong>Resolution:</strong> {inc.resolution}</div>
                          <div className="caption" style={{ marginTop: '16px', color: 'var(--muted)' }}>
                            Component: {inc.metadata?.component || inc.component} | 
                            Severity: {inc.metadata?.severity || inc.severity} | 
                            Environment: {inc.metadata?.environment || inc.environment}
                          </div>
                        </div>
                      )) : (
                        <div className="body-md text-muted">No similar incidents were returned.</div>
                      )}
                    </div>
                  </div>

                </div>
              )}
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="container footer-grid">
          <div className="footer-col" style={{ gridColumn: 'span 2' }}>
            <div className="top-nav-logo" style={{ color: 'var(--on-dark)' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="var(--on-dark)" strokeWidth="4" fill="none"/>
              </svg>
              Enterprise RCA
            </div>
            <p className="body-sm" style={{ maxWidth: '300px', marginTop: '16px' }}>
              Internal tool for analyzing historical incidents and proposing root causes.
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}

export default App;

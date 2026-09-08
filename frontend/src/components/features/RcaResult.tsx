import React from 'react';
import { AlertTriangle, Search, Activity } from 'lucide-react';

interface RcaResultProps {
  result: any;
}

const RcaResult: React.FC<RcaResultProps> = ({ result }) => {
  if (!result) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="grid grid-cols-3">
        <div className="card">
          <div className="card-header">
            <span className="card-title"><Search size={16} className="text-muted" style={{ display: 'inline', marginRight: '8px' }}/> Likely Root Cause</span>
          </div>
          <div style={{ fontSize: '15px', fontWeight: '500', color: 'var(--ink)', flex: 1 }}>{result.root_cause || "Unavailable"}</div>
        </div>
        <div className="card">
          <div className="card-header">
            <span className="card-title"><Activity size={16} className="text-muted" style={{ display: 'inline', marginRight: '8px' }}/> Recommended Resolution</span>
          </div>
          <div style={{ fontSize: '15px', fontWeight: '500', color: 'var(--ink)', flex: 1 }}>{result.resolution || "Unavailable"}</div>
        </div>
        <div className="card">
          <div className="card-header">
            <span className="card-title"><AlertTriangle size={16} className="text-muted" style={{ display: 'inline', marginRight: '8px' }}/> Evidence Strength</span>
          </div>
          <div style={{ fontSize: '18px', fontWeight: '700', color: result.evidence_strength === 'Insufficient' ? 'var(--warning)' : 'var(--success)' }}>
            {result.evidence_strength || "Unavailable"}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-title" style={{ color: 'var(--ink)' }}>AI RCA Summary</span>
        </div>
        <p className="body-sm" style={{ lineHeight: '1.6' }}>{result.summary || "No summary was returned by the model."}</p>
        {result.evidence_explanation && (
          <p className="body-sm text-muted" style={{ marginTop: '12px', lineHeight: '1.5' }}>{result.evidence_explanation}</p>
        )}
        {result.generation_mode === 'historical_fallback' && (
          <div style={{ marginTop: '16px', padding: '12px 16px', backgroundColor: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)', borderRadius: '8px', fontSize: '13px' }}>
            Gemini is unavailable. This RCA is a direct summary of the strongest documented historical evidence.
          </div>
        )}
        
        {result.evidence_strength === "Insufficient" && (
          <div style={{ marginTop: '16px', padding: '12px 16px', backgroundColor: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
            <AlertTriangle size={16} /> Insufficient historical evidence was found to determine a reliable root cause.
          </div>
        )}
        {result.retrieval_diagnostics && (
          <div className="caption" style={{ marginTop: '16px', display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
            <span>Evidence source: {result.retrieval_diagnostics.provenance || result.provenance || 'PostgreSQL historical knowledge base'}</span>
            <span>Retrieved: {String(result.retrieval_diagnostics.retrieved_incidents ?? 0)}</span>
            <span>Supporting: {String(result.evidence_incidents?.length ?? 0)}</span>
            {result.evidence_expansion_used && <span>R2 expansion: {result.r2_candidates_found ?? 0} candidates, {result.r2_incidents_ingested ?? 0} ingested</span>}
          </div>
        )}
      </div>

      <div className="card" style={{ padding: '0' }}>
        <div className="card-header" style={{ padding: '24px 24px 16px' }}>
          <span className="card-title" style={{ color: 'var(--ink)' }}>Top Similar Incidents</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {result.similar_incidents?.length > 0 ? result.similar_incidents.map((inc: any, i: number) => (
            <div key={i} style={{ padding: '16px 24px', borderTop: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '12px' }}>
                <span className="badge badge-neutral">{inc.incident_id || 'Unknown'}</span>
                <span className="badge badge-success">Similarity {parseFloat(inc.similarity_score || 0).toFixed(3)}</span>
                {inc.retrieval_score != null && <span className="badge badge-neutral">Rank {parseFloat(inc.retrieval_score).toFixed(3)}</span>}
              </div>
              <h4 className="title-sm">{inc.title || 'Untitled Incident'}</h4>
              <p className="body-sm text-muted" style={{ margin: '8px 0' }}>{inc.description}</p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
                <div style={{ backgroundColor: 'var(--canvas)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div className="caption" style={{ marginBottom: '4px' }}>Root Cause</div>
                  <div className="body-sm">{inc.root_cause}</div>
                </div>
                <div style={{ backgroundColor: 'var(--canvas)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div className="caption" style={{ marginBottom: '4px' }}>Resolution</div>
                  <div className="body-sm">{inc.resolution}</div>
                </div>
              </div>
              
              <div className="caption" style={{ marginTop: '16px', display: 'flex', gap: '16px' }}>
                <span>Project: {inc.project || 'Unknown'}</span>
                <span>Comp: {inc.metadata?.component || inc.component}</span>
                <span>Sev: {inc.metadata?.severity || inc.severity}</span>
                <span>Env: {inc.metadata?.environment || inc.environment}</span>
              </div>
            </div>
          )) : (
            <div className="body-sm text-muted" style={{ padding: '0 24px 24px' }}>No similar incidents were returned.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RcaResult;

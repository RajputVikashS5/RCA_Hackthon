import React, { useState } from 'react';
import AnalyzeIncidentForm from '../components/features/AnalyzeIncidentForm';
import ZenodoTestCard from '../components/features/ZenodoTestCard';
import RcaResult from '../components/features/RcaResult';
import { analyzeIncident, testZenodoConnection } from '../api';

const Incidents: React.FC = () => {
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
      setZenodoResult(await testZenodoConnection());
    } catch (err: any) {
      setZenodoError(err.message);
    } finally {
      setZenodoLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', gap: '24px' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <AnalyzeIncidentForm 
          description={description} setDescription={setDescription}
          component={component} setComponent={setComponent}
          severity={severity} setSeverity={setSeverity}
          environment={environment} setEnvironment={setEnvironment}
          incidentType={incidentType} setIncidentType={setIncidentType}
          onSubmit={handleAnalyze}
          loading={analysisLoading}
          error={analysisError}
        />
        
        {analysisResult && (
          <RcaResult result={analysisResult} />
        )}
      </div>

      <div style={{ width: '360px' }}>
        <ZenodoTestCard 
          onTest={handleZenodoTest}
          loading={zenodoLoading}
          result={zenodoResult}
          error={zenodoError}
        />
      </div>
    </div>
  );
};

export default Incidents;

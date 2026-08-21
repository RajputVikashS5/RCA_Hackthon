import { useState } from 'react';
import './App.css';
import DashboardLayout from './components/layout/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Incidents from './pages/Incidents';
import Statistics from './pages/Statistics';
import Settings from './pages/Settings';

function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [pendingPage, setPendingPage] = useState<string | null>(null);

  const handleNavigate = (page: string) => {
    if (unsavedChanges) {
      setPendingPage(page);
    } else {
      setActivePage(page);
    }
  };

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard />;
      case 'analytics':
        return <Statistics />;
      case 'incidents':
        return <Incidents />;
      case 'settings':
        return <Settings setUnsavedChanges={setUnsavedChanges} unsavedChanges={unsavedChanges} />;
      default:
        return <Dashboard />;
    }
  };

  const pageTitles: Record<string, string> = {
    dashboard: 'Dashboard',
    analytics: 'Statistics',
    incidents: 'Incidents Management',
    settings: 'Settings'
  };

  return (
    <>
      <DashboardLayout 
        activePage={activePage} 
        onNavigate={handleNavigate}
        pageTitle={pageTitles[activePage] || 'Incident IQ'}
      >
        {renderPage()}
      </DashboardLayout>

      {pendingPage && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 9999,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div className="card" style={{ width: '400px', gap: '16px' }}>
            <h3 className="title-lg">Unsaved Changes</h3>
            <p className="body-md">You have unsaved changes. Leave without saving?</p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '8px' }}>
              <button className="btn-secondary" onClick={() => setPendingPage(null)}>Stay</button>
              <button className="btn-primary" style={{ backgroundColor: 'var(--error)' }} onClick={() => {
                setUnsavedChanges(false);
                setActivePage(pendingPage);
                setPendingPage(null);
              }}>Leave</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default App;

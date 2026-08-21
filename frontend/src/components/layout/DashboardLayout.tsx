import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface DashboardLayoutProps {
  children: React.ReactNode;
  activePage: string;
  onNavigate: (page: string) => void;
  pageTitle: string;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children, activePage, onNavigate, pageTitle }) => {
  return (
    <div className="dashboard-layout">
      <Sidebar activePage={activePage} onNavigate={onNavigate} />
      <div className="main-container">
        <Header pageTitle={pageTitle} onNavigate={onNavigate} />
        <main className="content-area">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;

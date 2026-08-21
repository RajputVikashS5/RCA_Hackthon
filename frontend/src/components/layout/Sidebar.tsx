import React from 'react';
import { 
  LayoutDashboard, 
  BarChart2, 
  AlertTriangle, 
  Settings, 
  Shield 
} from 'lucide-react';

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activePage, onNavigate }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Overview', icon: <LayoutDashboard size={20} /> },
    { id: 'analytics', label: 'Statistics', icon: <BarChart2 size={20} /> },
    { id: 'incidents', label: 'Incidents', icon: <AlertTriangle size={20} /> },
  ];

  const generalItems = [
    { id: 'settings', label: 'Settings', icon: <Settings size={20} /> }
  ];

  const renderNav = (items: typeof menuItems) => (
    <ul className="sidebar-nav">
      {items.map((item) => (
        <li key={item.id}>
          <button
            className={`sidebar-link ${activePage === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        </li>
      ))}
    </ul>
  );

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="var(--brand-green)" />
             <path d="M2 17L12 22L22 17" stroke="var(--brand-green)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
             <path d="M2 12L12 17L22 12" stroke="var(--brand-green)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>Incident IQ</span>
        </div>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-label">MENU</div>
        {renderNav(menuItems)}
      </div>

      <div className="sidebar-section">
        <div className="sidebar-label">GENERAL</div>
        {renderNav(generalItems)}
      </div>

    </aside>
  );
};

export default Sidebar;

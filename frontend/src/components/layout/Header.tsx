import React from 'react';
import { Search, Bell, Plus, Calendar } from 'lucide-react';

interface HeaderProps {
  pageTitle: string;
  onNavigate: (page: string) => void;
}

const Header: React.FC<HeaderProps> = ({ pageTitle, onNavigate }) => {
  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">{pageTitle}</h1>
        <div className="header-subtitle">
          An easy way to manage incidents with care and precision.
        </div>
      </div>
      
      <div className="header-right">
        <div className="search-bar">
          <Search size={16} className="text-muted" />
          <input type="text" placeholder="Search anything in RCA..." className="search-input" />
        </div>
        
        <button className="header-icon-btn">
          <Calendar size={18} />
        </button>
        <button className="header-icon-btn">
          <Bell size={18} />
        </button>
        <button 
          className="btn-primary" 
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '100px' }}
          onClick={() => onNavigate('incidents')}
        >
          Add new incident <Plus size={16} />
        </button>
      </div>
    </header>
  );
};

export default Header;

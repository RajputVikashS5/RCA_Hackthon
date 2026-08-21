import React from 'react';
import { MoreHorizontal } from 'lucide-react';

export interface Transaction {
  id: string;
  title: string;
  date: string;
  status: 'Completed' | 'Pending' | 'Failed';
  reference: string;
}

interface TransactionListProps {
  transactions: Transaction[];
  title?: string;
}

const TransactionList: React.FC<TransactionListProps> = ({ transactions, title = 'Recent Incidents' }) => {
  return (
    <div className="card" style={{ padding: '24px 0' }}>
      <div className="card-header" style={{ padding: '0 24px' }}>
        <span className="card-title" style={{ color: 'var(--ink)' }}>{title}</span>
        <button className="header-icon-btn" style={{ width: '28px', height: '28px', border: 'none', background: 'transparent' }}>
          <MoreHorizontal size={16} color="var(--muted)" />
        </button>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {transactions.map((tx) => (
          <div key={tx.id} style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            padding: '16px 24px',
            borderBottom: '1px solid var(--border)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: 'var(--surface-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: '18px' }}>⚡</span>
              </div>
              <div>
                <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--ink)' }}>{tx.title}</div>
                <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '2px' }}>{tx.date}</div>
              </div>
            </div>
            
            <div style={{ textAlign: 'right' }}>
              <div style={{ 
                fontSize: '13px', 
                fontWeight: '500', 
                color: tx.status === 'Completed' ? 'var(--success)' : 
                       tx.status === 'Failed' ? 'var(--error)' : 'var(--warning)' 
              }}>
                {tx.status}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '2px', fontFamily: 'var(--font-code)' }}>
                {tx.reference}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TransactionList;

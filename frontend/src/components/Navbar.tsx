import React, { useEffect, useState } from 'react';
import { ShieldCheck, Server, LogOut, User, KeyRound } from 'lucide-react';
import { api } from '../services/api';
import { Seller } from '../types';

interface NavbarProps {
  seller: Seller | null;
  onLogout: () => void;
  activeRoute: string;
  navigate: (route: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  seller,
  onLogout,
  activeRoute,
  navigate,
}) => {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    let isMounted = true;
    api.health
      .check()
      .then(() => {
        if (isMounted) setBackendStatus('online');
      })
      .catch(() => {
        if (isMounted) setBackendStatus('offline');
      });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <header
      style={{
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(11, 14, 20, 0.95)',
        backdropFilter: 'blur(10px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '14px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Brand / Logo */}
        <div
          onClick={() => navigate(seller ? '/dashboard' : '/login')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
          }}
        >
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #1a9fff 0%, #005599 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px rgba(26, 159, 255, 0.4)',
            }}
          >
            <ShieldCheck size={22} color="#ffffff" />
          </div>
          <div>
            <div
              style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 700,
                fontSize: '1.15rem',
                color: '#ffffff',
                letterSpacing: '-0.3px',
              }}
            >
              Steam Guard <span style={{ color: 'var(--steam-cyan)' }}>Resgate</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Infraestrutura Cloud & IMAP Seguro
            </div>
          </div>
        </div>

        {/* Links & Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Backend Health Badge */}
          <div
            className="badge"
            style={{
              background:
                backendStatus === 'online'
                  ? 'rgba(34, 197, 94, 0.1)'
                  : backendStatus === 'offline'
                  ? 'rgba(239, 68, 68, 0.1)'
                  : 'rgba(148, 163, 184, 0.1)',
              color:
                backendStatus === 'online'
                  ? 'var(--color-success)'
                  : backendStatus === 'offline'
                  ? 'var(--color-error)'
                  : 'var(--text-muted)',
              border: `1px solid ${
                backendStatus === 'online'
                  ? 'rgba(34, 197, 94, 0.3)'
                  : backendStatus === 'offline'
                  ? 'rgba(239, 68, 68, 0.3)'
                  : 'rgba(148, 163, 184, 0.2)'
              }`,
            }}
            title="Status do serviço FastAPI no Render"
          >
            <Server size={12} />
            {backendStatus === 'online'
              ? 'API Online'
              : backendStatus === 'offline'
              ? 'API Offline'
              : 'Verificando...'}
          </div>

          {seller ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.85rem',
                  color: 'var(--text-muted)',
                }}
              >
                <User size={15} />
                <span>{seller.email}</span>
              </div>
              <button
                onClick={onLogout}
                className="btn-secondary"
                style={{ padding: '6px 12px', fontSize: '0.82rem' }}
                title="Encerrar sessão"
              >
                <LogOut size={14} />
                Sair
              </button>
            </div>
          ) : (
            <button
              onClick={() => navigate('/login')}
              className={activeRoute === '/login' ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '8px 16px', fontSize: '0.85rem' }}
            >
              <KeyRound size={15} />
              Área do Revendedor
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

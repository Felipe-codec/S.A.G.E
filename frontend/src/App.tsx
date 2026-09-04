import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ResgatePage } from './pages/ResgatePage';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { NotFound } from './pages/NotFound';
import { HealthStatus } from './pages/HealthStatus';
import { api } from './services/api';
import { Seller } from './types';

export const App: React.FC = () => {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [seller, setSeller] = useState<Seller | null>(null);
  const [isAuthChecking, setIsAuthChecking] = useState(true);

  // Sincroniza histórico de navegação
  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    setCurrentPath(path);
  };

  // Restaura sessão se houver token salvo
  useEffect(() => {
    const token = localStorage.getItem('steam_guard_token');
    if (token) {
      api.auth
        .me()
        .then((user) => setSeller(user))
        .catch(() => {
          localStorage.removeItem('steam_guard_token');
          setSeller(null);
        })
        .finally(() => setIsAuthChecking(false));
    } else {
      setIsAuthChecking(false);
    }
  }, []);

  const handleLogout = async () => {
    await api.auth.logout();
    setSeller(null);
    navigate('/login');
  };

  // Extrai o token de resgate da URL se existir (ex: /resgate/xyz)
  let initialRedemptionToken = '';
  if (currentPath.startsWith('/resgate/')) {
    initialRedemptionToken = currentPath.replace('/resgate/', '').split('/')[0];
  }

  // Roteamento
  const renderContent = () => {
    if (currentPath.startsWith('/resgate') || currentPath === '/') {
      return <ResgatePage initialToken={initialRedemptionToken} />;
    }

    if (currentPath === '/login') {
      if (seller) {
        return <Dashboard seller={seller} navigate={navigate} />;
      }
      return <Login onLoginSuccess={(u) => setSeller(u)} navigate={navigate} />;
    }

    if (currentPath === '/dashboard') {
      if (isAuthChecking) {
        return <div style={{ textAlign: 'center', padding: '60px' }}>Verificando autenticação...</div>;
      }
      if (!seller) {
        return <Login onLoginSuccess={(u) => setSeller(u)} navigate={navigate} />;
      }
      return <Dashboard seller={seller} navigate={navigate} />;
    }

    if (currentPath === '/health' || currentPath === '/health/ready') {
      return <HealthStatus navigate={navigate} />;
    }

    return <NotFound navigate={navigate} />;
  };

  return (
    <div className="app-container">
      <Navbar
        seller={seller}
        onLogout={handleLogout}
        activeRoute={currentPath}
        navigate={navigate}
      />
      <main className="main-content">{renderContent()}</main>

      {/* Rodapé institucional */}
      <footer
        style={{
          borderTop: '1px solid var(--border-subtle)',
          padding: '16px 20px',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-dark)',
          background: 'rgba(11, 14, 20, 0.95)',
        }}
      >
        Steam Guard Resgate &copy; {new Date().getFullYear()} — Infraestrutura cloud de alta disponibilidade.
        Não afiliado à Valve Corporation.
      </footer>
    </div>
  );
};

export default App;

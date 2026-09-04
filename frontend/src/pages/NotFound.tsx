import React from 'react';
import { HelpCircle } from 'lucide-react';

interface NotFoundProps {
  navigate: (route: string) => void;
}

export const NotFound: React.FC<NotFoundProps> = ({ navigate }) => {
  return (
    <div style={{ textAlign: 'center', padding: '60px 20px', maxWidth: '480px', margin: '0 auto' }}>
      <div className="glass-card">
        <HelpCircle size={48} color="var(--steam-cyan)" style={{ margin: '0 auto 16px' }} />
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', color: '#ffffff', marginBottom: '8px' }}>
          Página não encontrada
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          O link acessado não existe ou foi modificado.
        </p>
        <button onClick={() => navigate('/')} className="btn-primary" style={{ padding: '12px 24px' }}>
          Voltar para o Início
        </button>
      </div>
    </div>
  );
};

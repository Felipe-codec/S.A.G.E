import React, { useState, useEffect } from 'react';
import { Server, CheckCircle2, XCircle, Loader2, ExternalLink, AlertTriangle, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

interface HealthStatusProps {
  navigate: (route: string) => void;
}

export const HealthStatus: React.FC<HealthStatusProps> = ({ navigate }) => {
  const apiUrl = import.meta.env.VITE_API_URL || '';
  const [healthData, setHealthData] = useState<{ status: string; app_env: string } | null>(null);
  const [readyData, setReadyData] = useState<{ status: string; database: string; redis: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkStatus = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [h, r] = await Promise.all([
        api.health.check(),
        api.health.ready().catch((err) => ({ status: 'erro', database: 'desconectado', redis: err.message })),
      ]);
      setHealthData(h);
      setReadyData(r);
    } catch (err: any) {
      setError(err.message || 'Falha ao conectar com o backend.');
      setHealthData(null);
      setReadyData(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  return (
    <div style={{ maxWidth: '640px', margin: '30px auto', width: '100%' }}>
      <div className="glass-card">
        {/* Cabeçalho */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div
            style={{
              width: '50px',
              height: '50px',
              borderRadius: '50%',
              background: 'rgba(26, 159, 255, 0.15)',
              border: '1px solid var(--border-active)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 12px auto',
            }}
          >
            <Server size={26} color="var(--steam-cyan)" />
          </div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', color: '#ffffff' }}>
            Diagnóstico do Sistema & Health Check
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Status de conectividade entre o Frontend (Vercel), Backend (Render) e Banco (Supabase)
          </p>
        </div>

        {/* Alerta se VITE_API_URL não estiver configurada */}
        {!apiUrl && (
          <div
            style={{
              background: 'rgba(245, 158, 11, 0.1)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              borderRadius: 'var(--radius-sm)',
              padding: '16px',
              marginBottom: '20px',
            }}
          >
            <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
              <AlertTriangle color="var(--color-warning)" size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <div style={{ fontWeight: 600, color: 'var(--color-warning)', fontSize: '0.9rem' }}>
                  Variável VITE_API_URL não detectada na Vercel!
                </div>
                <p style={{ fontSize: '0.82rem', color: '#fcd34d', marginTop: '6px', lineHeight: '1.5' }}>
                  O frontend está rodando na Vercel, mas não sabe o endereço do seu backend no Render.
                  Para corrigir: acesse o painel da <strong>Vercel</strong> &gt; <strong>Settings</strong> &gt;{' '}
                  <strong>Environment Variables</strong>, crie <code>VITE_API_URL</code> com a URL do Render (ex:{' '}
                  <code>https://seu-backend.onrender.com</code>) e faça um <strong>Redeploy</strong>.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Detalhes de Conectividade */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
          {/* Frontend */}
          <div
            style={{
              background: 'rgba(11, 14, 20, 0.6)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '14px 18px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Camada de Apresentação (Frontend)</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#ffffff' }}>Vercel Edge Network</div>
            </div>
            <span className="badge badge-success">
              <CheckCircle2 size={13} />
              Online
            </span>
          </div>

          {/* Backend */}
          <div
            style={{
              background: 'rgba(11, 14, 20, 0.6)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '14px 18px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Camada de API (Backend FastAPI)</div>
              <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#ffffff' }}>
                {apiUrl ? apiUrl : 'Não configurado (Usando domínio relativo)'}
              </div>
            </div>
            {isLoading ? (
              <Loader2 className="spin" size={18} color="var(--steam-cyan)" />
            ) : healthData?.status === 'ok' ? (
              <span className="badge badge-success">
                <CheckCircle2 size={13} />
                Online ({healthData.app_env})
              </span>
            ) : (
              <span className="badge badge-error">
                <XCircle size={13} />
                Offline
              </span>
            )}
          </div>

          {/* Supabase */}
          <div
            style={{
              background: 'rgba(11, 14, 20, 0.6)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '14px 18px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Banco de Dados Relacional</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#ffffff' }}>Supabase PostgreSQL</div>
            </div>
            {isLoading ? (
              <Loader2 className="spin" size={18} color="var(--steam-cyan)" />
            ) : readyData?.database === 'connected' ? (
              <span className="badge badge-success">
                <CheckCircle2 size={13} />
                Conectado
              </span>
            ) : (
              <span className="badge badge-warning">
                <AlertTriangle size={13} />
                Desconectado
              </span>
            )}
          </div>
        </div>

        {/* Detalhes de Erro se houver */}
        {error && (
          <div
            style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: 'var(--radius-sm)',
              padding: '14px',
              marginBottom: '20px',
              fontSize: '0.82rem',
              color: '#fca5a5',
            }}
          >
            <div style={{ fontWeight: 600, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertTriangle size={15} color="var(--color-error)" /> Motivo da Falha:
            </div>
            <div>{error}</div>
            <div style={{ marginTop: '8px', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
              Dica: Certifique-se de que a variável CORS_ORIGINS no Render está exatamente sem barra no final: <code>https://s-a-g-e-kappa.vercel.app</code>
            </div>
          </div>
        )}

        {/* Botão de Teste */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
          <button onClick={checkStatus} disabled={isLoading} className="btn-primary" style={{ padding: '10px 20px' }}>
            {isLoading ? <Loader2 className="spin" size={16} /> : <ShieldCheck size={16} />}
            Testar Conexão Novamente
          </button>
          <button onClick={() => navigate('/')} className="btn-secondary" style={{ padding: '10px 20px' }}>
            Voltar para o Início
          </button>
        </div>
      </div>
    </div>
  );
};

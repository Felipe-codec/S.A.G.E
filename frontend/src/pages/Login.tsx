import React, { useState } from 'react';
import { Lock, Mail, Loader2, AlertCircle, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { Seller } from '../types';

interface LoginProps {
  onLoginSuccess: (seller: Seller) => void;
  navigate: (route: string) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess, navigate }) => {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);
    setIsLoading(true);

    try {
      if (isRegisterMode) {
        await api.auth.register(email, password);
        setSuccessMsg('Conta criada com sucesso! Realizando login automático...');
        const res = await api.auth.login(email, password);
        onLoginSuccess(res.seller);
        navigate('/dashboard');
      } else {
        const res = await api.auth.login(email, password);
        onLoginSuccess(res.seller);
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Falha na autenticação. Verifique os dados inseridos.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '420px', margin: '40px auto', width: '100%' }}>
      <div className="glass-card">
        {/* Cabeçalho */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              background: 'rgba(26, 159, 255, 0.15)',
              border: '1px solid var(--border-active)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 12px auto',
            }}
          >
            <ShieldCheck size={26} color="var(--steam-cyan)" />
          </div>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.5rem',
              fontWeight: 700,
              color: '#ffffff',
            }}
          >
            {isRegisterMode ? 'Cadastro de Revendedor' : 'Painel do Revendedor'}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            Gerenciamento de contas Steam, tokens e servidores IMAP
          </p>
        </div>

        {/* Mensagens de Sucesso e Erro */}
        {error && (
          <div
            style={{
              background: 'var(--color-error-bg)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: 'var(--radius-sm)',
              padding: '12px',
              display: 'flex',
              gap: '8px',
              alignItems: 'center',
              marginBottom: '16px',
            }}
          >
            <AlertCircle color="var(--color-error)" size={16} style={{ flexShrink: 0 }} />
            <div style={{ fontSize: '0.82rem', color: '#fca5a5' }}>{error}</div>
          </div>
        )}

        {successMsg && (
          <div
            style={{
              background: 'var(--color-success-bg)',
              border: '1px solid rgba(34, 197, 94, 0.3)',
              borderRadius: 'var(--radius-sm)',
              padding: '12px',
              fontSize: '0.82rem',
              color: 'var(--color-success)',
              marginBottom: '16px',
            }}
          >
            {successMsg}
          </div>
        )}

        {/* Formulário */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '0.82rem',
                color: 'var(--text-muted)',
                marginBottom: '6px',
              }}
            >
              E-mail Comercial
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value.trim())}
                placeholder="revendedor@email.com"
                style={{ width: '100%', paddingLeft: '38px' }}
              />
              <Mail
                size={16}
                color="var(--text-dark)"
                style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
              />
            </div>
          </div>

          <div>
            <label
              style={{
                display: 'block',
                fontSize: '0.82rem',
                color: 'var(--text-muted)',
                marginBottom: '6px',
              }}
            >
              Senha de Acesso
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                style={{ width: '100%', paddingLeft: '38px' }}
              />
              <Lock
                size={16}
                color="var(--text-dark)"
                style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary"
            style={{ width: '100%', padding: '12px', marginTop: '8px' }}
          >
            {isLoading ? (
              <Loader2 className="spin" size={18} />
            ) : isRegisterMode ? (
              'Criar Conta de Revendedor'
            ) : (
              'Entrar no Painel'
            )}
          </button>
        </form>

        {/* Alternar Cadastro / Login */}
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <button
            type="button"
            onClick={() => {
              setIsRegisterMode(!isRegisterMode);
              setError(null);
              setSuccessMsg(null);
            }}
            style={{
              background: 'transparent',
              color: 'var(--steam-cyan)',
              fontSize: '0.82rem',
              textDecoration: 'underline',
            }}
          >
            {isRegisterMode
              ? 'Já possui uma conta? Faça login'
              : 'Não tem conta? Cadastre-se como revendedor'}
          </button>
        </div>
      </div>
    </div>
  );
};

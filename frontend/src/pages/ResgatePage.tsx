import React, { useState, useEffect } from 'react';
import {
  Shield,
  KeyRound,
  Loader2,
  AlertCircle,
  Gamepad2,
  CheckCircle2,
  HelpCircle,
} from 'lucide-react';
import { api } from '../services/api';
import { CodeCountdown } from '../components/CodeCountdown';
import { RedemptionInfo } from '../types';

interface ResgatePageProps {
  initialToken?: string;
}

export const ResgatePage: React.FC<ResgatePageProps> = ({ initialToken = '' }) => {
  const [tokenInput, setTokenInput] = useState(initialToken);
  const [activeToken, setActiveToken] = useState(initialToken);
  const [info, setInfo] = useState<RedemptionInfo | null>(null);
  const [isLoadingInfo, setIsLoadingInfo] = useState(false);
  const [infoError, setInfoError] = useState<string | null>(null);

  // Estados de busca do código
  const [isFetchingCode, setIsFetchingCode] = useState(false);
  const [codeResult, setCodeResult] = useState<string | null>(null);
  const [codeMessage, setCodeMessage] = useState<string | null>(null);
  const [codeError, setCodeError] = useState<string | null>(null);
  const [pollingStep, setPollingStep] = useState<string>('');

  // Carrega informações do token quando o token ativo mudar
  useEffect(() => {
    if (!activeToken) return;

    setIsLoadingInfo(true);
    setInfoError(null);
    setCodeResult(null);

    api.redemption
      .getInfo(activeToken)
      .then((data) => {
        setInfo(data);
      })
      .catch((err) => {
        setInfoError(err.message || 'Link de resgate inválido ou expirado.');
        setInfo(null);
      })
      .finally(() => {
        setIsLoadingInfo(false);
      });
  }, [activeToken]);

  const handleFetchCode = async () => {
    if (!activeToken) return;

    setIsFetchingCode(true);
    setCodeError(null);
    setCodeMessage(null);
    setCodeResult(null);

    setPollingStep('Conectando de forma segura ao servidor IMAP...');

    try {
      // Simula progresso visual durante a chamada real
      const timer1 = setTimeout(() => {
        setPollingStep('Sincronizando caixa de entrada da Steam...');
      }, 2500);

      const timer2 = setTimeout(() => {
        setPollingStep('Localizando mensagem recente da Valve...');
      }, 5500);

      const res = await api.redemption.requestCode(activeToken);

      clearTimeout(timer1);
      clearTimeout(timer2);

      if (res.success && res.code) {
        setCodeResult(res.code);
        setCodeMessage(res.message);
        // Atualiza usos restantes
        if (info) {
          setInfo({ ...info, remaining_uses: Math.max(0, info.remaining_uses - 1) });
        }
      } else {
        setCodeError(res.message);
      }
    } catch (err: any) {
      setCodeError(err.message || 'Falha ao buscar código. Tente novamente.');
    } finally {
      setIsFetchingCode(false);
      setPollingStep('');
    }
  };

  return (
    <div style={{ maxWidth: '680px', margin: '20px auto', width: '100%' }}>
      {/* Card Principal */}
      <div className="glass-card" style={{ position: 'relative', overflow: 'hidden' }}>
        {/* Glow Superior */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '3px',
            background: 'linear-gradient(90deg, #1a9fff, #66c0f4, #1a9fff)',
          }}
        />

        {/* Cabeçalho */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'rgba(26, 159, 255, 0.12)',
              border: '1px solid var(--border-active)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px auto',
              boxShadow: '0 0 20px rgba(26, 159, 255, 0.3)',
            }}
          >
            <Shield size={28} color="var(--steam-cyan)" />
          </div>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.8rem',
              fontWeight: 700,
              color: '#ffffff',
              marginBottom: '6px',
            }}
          >
            Resgate Steam Guard
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
            Obtenha o código de 5 dígitos para acessar sua conta Steam em tempo real
          </p>
        </div>

        {/* Input manual de token caso não venha na URL */}
        {!activeToken && (
          <div style={{ marginBottom: '24px' }}>
            <label
              style={{
                display: 'block',
                fontSize: '0.85rem',
                color: 'var(--text-muted)',
                marginBottom: '8px',
              }}
            >
              Cole o Token ou Código de Resgate fornecido pelo vendedor:
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                value={tokenInput}
                onChange={(e) => setTokenInput(e.target.value.trim())}
                placeholder="Ex: dHZXc2FtcGxl..."
                style={{ flex: 1 }}
              />
              <button
                onClick={() => setActiveToken(tokenInput)}
                disabled={!tokenInput}
                className="btn-primary"
              >
                <KeyRound size={16} />
                Acessar
              </button>
            </div>
          </div>
        )}

        {/* Loading inicial do token */}
        {isLoadingInfo && (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Loader2 className="spin" size={32} color="var(--steam-cyan)" style={{ margin: '0 auto 12px' }} />
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Validando credenciais do resgate...</p>
          </div>
        )}

        {/* Erro no Token */}
        {infoError && (
          <div
            style={{
              background: 'var(--color-error-bg)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: 'var(--radius-sm)',
              padding: '16px',
              display: 'flex',
              gap: '12px',
              alignItems: 'flex-start',
              marginBottom: '20px',
            }}
          >
            <AlertCircle color="var(--color-error)" size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontWeight: 600, color: 'var(--color-error)', fontSize: '0.92rem' }}>
                Não foi possível validar este resgate
              </div>
              <div style={{ color: '#fca5a5', fontSize: '0.85rem', marginTop: '4px' }}>{infoError}</div>
              <button
                onClick={() => {
                  setActiveToken('');
                  setTokenInput('');
                  setInfoError(null);
                }}
                className="btn-secondary"
                style={{ marginTop: '12px', fontSize: '0.8rem', padding: '6px 12px' }}
              >
                Tentar outro link
              </button>
            </div>
          </div>
        )}

        {/* Dados da Conta e Ação de Resgate */}
        {info && (
          <div>
            {/* Box Informativo da Conta Steam */}
            <div
              style={{
                background: 'rgba(11, 14, 20, 0.6)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '16px 20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '24px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Gamepad2 size={24} color="var(--steam-cyan)" />
                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Conta Steam Vinculada</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 600, color: '#ffffff' }}>
                    {info.steam_username}
                  </div>
                  {info.display_name && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dark)' }}>{info.display_name}</div>
                  )}
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Resgates Restantes</div>
                <div
                  style={{
                    fontSize: '1rem',
                    fontWeight: 700,
                    color: info.remaining_uses > 0 ? 'var(--color-success)' : 'var(--color-error)',
                  }}
                >
                  {info.remaining_uses}
                </div>
              </div>
            </div>

            {/* Código Exibido */}
            {codeResult && (
              <div style={{ marginBottom: '28px' }}>
                <CodeCountdown
                  code={codeResult}
                  initialSeconds={60}
                  onExpire={() => setCodeMessage('O código expirou. Solicite um novo código se necessário.')}
                />
                {codeMessage && (
                  <p
                    style={{
                      textAlign: 'center',
                      color: 'var(--color-success)',
                      fontSize: '0.85rem',
                      marginTop: '12px',
                    }}
                  >
                    {codeMessage}
                  </p>
                )}
              </div>
            )}

            {/* Erro de busca do código */}
            {codeError && (
              <div
                style={{
                  background: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '14px',
                  display: 'flex',
                  gap: '10px',
                  alignItems: 'center',
                  marginBottom: '20px',
                }}
              >
                <AlertCircle color="var(--color-warning)" size={18} style={{ flexShrink: 0 }} />
                <div style={{ fontSize: '0.85rem', color: '#fcd34d' }}>{codeError}</div>
              </div>
            )}

            {/* Botão de Solicitação */}
            <div style={{ textAlign: 'center' }}>
              <button
                onClick={handleFetchCode}
                disabled={isFetchingCode || info.remaining_uses <= 0}
                className="btn-primary"
                style={{ width: '100%', padding: '16px', fontSize: '1.05rem' }}
              >
                {isFetchingCode ? (
                  <>
                    <Loader2 className="spin" size={20} />
                    <span>{pollingStep || 'Buscando código Steam Guard...'}</span>
                  </>
                ) : (
                  <>
                    <KeyRound size={20} />
                    <span>{codeResult ? 'Gerar Outro Código' : 'Obter Código Steam Guard'}</span>
                  </>
                )}
              </button>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  marginTop: '12px',
                  fontSize: '0.78rem',
                  color: 'var(--text-muted)',
                }}
              >
                <CheckCircle2 size={13} color="var(--color-success)" />
                Conexão criptografada ponta a ponta (TLS :993)
              </div>
            </div>

            {/* Passo a Passo para o Comprador */}
            <div
              style={{
                marginTop: '32px',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: '20px',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  color: '#ffffff',
                  marginBottom: '12px',
                }}
              >
                <HelpCircle size={15} color="var(--steam-cyan)" />
                Como utilizar o código de acesso:
              </div>
              <ol
                style={{
                  paddingLeft: '20px',
                  fontSize: '0.82rem',
                  color: 'var(--text-muted)',
                  lineHeight: '1.6',
                }}
              >
                <li>Inicie o aplicativo Steam no computador ou no navegador.</li>
                <li>Digite o usuário e senha da conta adquirida.</li>
                <li>
                  Quando a tela solicitar o <strong>Steam Guard</strong>, clique no botão azul acima.
                </li>
                <li>Copie os 5 caracteres gerados e cole na janela da Steam.</li>
              </ol>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

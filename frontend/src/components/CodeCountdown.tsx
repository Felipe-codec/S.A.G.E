import React, { useState, useEffect } from 'react';
import { Copy, Check, Clock, AlertTriangle } from 'lucide-react';

interface CodeCountdownProps {
  code: string;
  initialSeconds?: number;
  onExpire?: () => void;
}

export const CodeCountdown: React.FC<CodeCountdownProps> = ({
  code,
  initialSeconds = 60,
  onExpire,
}) => {
  const [timeLeft, setTimeLeft] = useState(initialSeconds);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setTimeLeft(initialSeconds);
  }, [code, initialSeconds]);

  useEffect(() => {
    if (timeLeft <= 0) {
      if (onExpire) onExpire();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, onExpire]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback manual caso permissão da clipboard falhe
      const textArea = document.createElement('textarea');
      textArea.value = code;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const percentage = Math.max(0, (timeLeft / initialSeconds) * 100);
  const isExpiringSoon = timeLeft <= 15;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '20px',
        width: '100%',
        maxWidth: '450px',
        margin: '0 auto',
      }}
    >
      {/* Bloco do Código Monospaçado */}
      <div style={{ textAlign: 'center', width: '100%' }}>
        <div className="steam-code-display">{code}</div>
      </div>

      {/* Botão de Cópia Rápida */}
      <button
        onClick={handleCopy}
        className="btn-primary"
        style={{
          width: '100%',
          padding: '14px',
          fontSize: '1rem',
          background: copied
            ? 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)'
            : undefined,
        }}
      >
        {copied ? (
          <>
            <Check size={18} />
            Código Copiado com Sucesso!
          </>
        ) : (
          <>
            <Copy size={18} />
            Copiar Código de Acesso
          </>
        )}
      </button>

      {/* Barra de Progresso de Expiração */}
      <div style={{ width: '100%' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '6px',
            fontSize: '0.82rem',
            color: isExpiringSoon ? 'var(--color-warning)' : 'var(--text-muted)',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            {isExpiringSoon ? <AlertTriangle size={14} /> : <Clock size={14} />}
            Válido por mais:
          </span>
          <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
            {timeLeft}s
          </span>
        </div>

        <div
          style={{
            width: '100%',
            height: '6px',
            background: 'rgba(255, 255, 255, 0.08)',
            borderRadius: '999px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${percentage}%`,
              background: isExpiringSoon
                ? 'var(--color-warning)'
                : 'linear-gradient(90deg, #1a9fff, #66c0f4)',
              transition: 'width 1s linear, background-color 0.3s ease',
            }}
          />
        </div>
      </div>
    </div>
  );
};

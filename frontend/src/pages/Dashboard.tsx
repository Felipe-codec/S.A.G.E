import React, { useState, useEffect } from 'react';
import {
  Gamepad2,
  Mail,
  KeyRound,
  ShieldCheck,
  Plus,
  Trash2,
  Copy,
  Check,
  Radio,
  Loader2,
  AlertCircle,
  Clock,
} from 'lucide-react';
import { api } from '../services/api';
import {
  ImapConfig,
  ImapTestResponse,
  Seller,
  SteamAccount,
  TokenGenerateResponse,
  TokenRecord,
} from '../types';

interface DashboardProps {
  seller: Seller;
  navigate: (route: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ seller, navigate }) => {
  const [activeTab, setActiveTab] = useState<'generator' | 'accounts' | 'imap' | 'tokens'>('generator');

  // Estados de dados
  const [accounts, setAccounts] = useState<SteamAccount[]>([]);
  const [tokens, setTokens] = useState<TokenRecord[]>([]);
  const [imapConfig, setImapConfig] = useState<ImapConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Formulário: Adicionar Conta
  const [newAccountUsername, setNewAccountUsername] = useState('');
  const [newAccountDisplayName, setNewAccountDisplayName] = useState('');
  const [isAddingAccount, setIsAddingAccount] = useState(false);

  // Formulário: Gerar Token
  const [selectedAccountId, setSelectedAccountId] = useState<number | ''>('');
  const [tokenExpiresSeconds, setTokenExpiresSeconds] = useState(3600);
  const [tokenMaxUses, setTokenMaxUses] = useState(1);
  const [isGeneratingToken, setIsGeneratingToken] = useState(false);
  const [generatedTokenResult, setGeneratedTokenResult] = useState<TokenGenerateResponse | null>(null);
  const [tokenCopied, setTokenCopied] = useState(false);

  // Formulário: IMAP
  const [imapHost, setImapHost] = useState('imap.gmail.com');
  const [imapPort, setImapPort] = useState(993);
  const [imapUsername, setImapUsername] = useState('');
  const [imapPassword, setImapPassword] = useState('');
  const [imapUseSsl, setImapUseSsl] = useState(true);
  const [isSavingImap, setIsSavingImap] = useState(false);
  const [isTestingImap, setIsTestingImap] = useState(false);
  const [imapTestResult, setImapTestResult] = useState<ImapTestResponse | null>(null);
  const [imapMessage, setImapMessage] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [accs, toks] = await Promise.all([
        api.steamAccounts.list(),
        api.tokens.list(),
      ]);
      setAccounts(accs);
      setTokens(toks);
      if (accs.length > 0 && selectedAccountId === '') {
        setSelectedAccountId(accs[0].id);
      }

      // Tenta buscar config IMAP existente
      try {
        const imap = await api.imap.get();
        setImapConfig(imap);
        setImapHost(imap.host);
        setImapPort(imap.port);
        setImapUsername(imap.username);
        setImapUseSsl(imap.use_ssl);
      } catch {
        // Sem config cadastrada ainda
      }
    } catch (err) {
      console.error('Erro ao carregar dados do dashboard:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Handlers Contas
  const handleAddAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAccountUsername.trim()) return;
    setIsAddingAccount(true);
    try {
      const created = await api.steamAccounts.create(newAccountUsername.trim(), newAccountDisplayName.trim() || undefined);
      setAccounts([created, ...accounts]);
      setNewAccountUsername('');
      setNewAccountDisplayName('');
      if (selectedAccountId === '') setSelectedAccountId(created.id);
    } catch (err: any) {
      alert(err.message || 'Erro ao adicionar conta');
    } finally {
      setIsAddingAccount(false);
    }
  };

  const handleDeleteAccount = async (id: number) => {
    if (!confirm('Deseja realmente excluir esta conta Steam? Todos os tokens associados serão revogados.')) return;
    try {
      await api.steamAccounts.delete(id);
      setAccounts(accounts.filter((a) => a.id !== id));
      if (selectedAccountId === id) setSelectedAccountId('');
    } catch (err: any) {
      alert(err.message || 'Erro ao excluir conta');
    }
  };

  // Handlers Token
  const handleGenerateToken = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAccountId) {
      alert('Selecione uma conta Steam.');
      return;
    }
    setIsGeneratingToken(true);
    setGeneratedTokenResult(null);
    try {
      const res = await api.tokens.generate(Number(selectedAccountId), tokenExpiresSeconds, tokenMaxUses);
      setGeneratedTokenResult(res);
      const updatedTokens = await api.tokens.list();
      setTokens(updatedTokens);
    } catch (err: any) {
      alert(err.message || 'Erro ao gerar token');
    } finally {
      setIsGeneratingToken(false);
    }
  };

  const handleCopyLink = () => {
    if (!generatedTokenResult) return;
    navigator.clipboard.writeText(generatedTokenResult.token_url);
    setTokenCopied(true);
    setTimeout(() => setTokenCopied(false), 2500);
  };

  // Handlers IMAP
  const handleSaveImap = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!imapPassword) {
      alert('Preencha a senha ou App Password do servidor IMAP.');
      return;
    }
    setIsSavingImap(true);
    setImapMessage(null);
    try {
      const res = await api.imap.save({
        host: imapHost.trim(),
        port: Number(imapPort),
        username: imapUsername.trim(),
        password: imapPassword,
        use_ssl: imapUseSsl,
      });
      setImapConfig(res);
      setImapPassword('');
      setImapMessage('Configurações salvas e criptografadas com chave Fernet com sucesso!');
    } catch (err: any) {
      alert(err.message || 'Erro ao salvar configurações IMAP');
    } finally {
      setIsSavingImap(false);
    }
  };

  const handleTestImap = async () => {
    setIsTestingImap(true);
    setImapTestResult(null);
    try {
      const res = await api.imap.test({
        host: imapHost.trim(),
        port: Number(imapPort),
        username: imapUsername.trim(),
        password: imapPassword || undefined,
        use_ssl: imapUseSsl,
      });
      setImapTestResult(res);
    } catch (err: any) {
      setImapTestResult({
        success: false,
        message: err.message || 'Falha ao testar conexão',
        response_time_ms: 0,
      });
    } finally {
      setIsTestingImap(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Resumo / Estatísticas Rápidas */}
      <div className="grid-3">
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: '8px',
                background: 'rgba(26, 159, 255, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Gamepad2 size={22} color="var(--steam-cyan)" />
            </div>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Contas Cadastradas</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ffffff' }}>{accounts.length}</div>
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: '8px',
                background: 'rgba(34, 197, 94, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <KeyRound size={22} color="var(--color-success)" />
            </div>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Tokens Gerados</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ffffff' }}>{tokens.length}</div>
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: '8px',
                background: imapConfig ? 'rgba(34, 197, 94, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Mail size={22} color={imapConfig ? 'var(--color-success)' : 'var(--color-warning)'} />
            </div>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Serviço IMAP</div>
              <div
                style={{
                  fontSize: '0.95rem',
                  fontWeight: 600,
                  color: imapConfig ? 'var(--color-success)' : 'var(--color-warning)',
                }}
              >
                {imapConfig ? 'Conectado (TLS)' : 'Configuração Pendente'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navegação por Abas */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid var(--border-subtle)',
          paddingBottom: '12px',
          overflowX: 'auto',
        }}
      >
        <button
          onClick={() => setActiveTab('generator')}
          className={activeTab === 'generator' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          <KeyRound size={15} />
          Gerador de Resgates
        </button>
        <button
          onClick={() => setActiveTab('accounts')}
          className={activeTab === 'accounts' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          <Gamepad2 size={15} />
          Contas Steam ({accounts.length})
        </button>
        <button
          onClick={() => setActiveTab('imap')}
          className={activeTab === 'imap' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          <Mail size={15} />
          Servidor IMAP
        </button>
        <button
          onClick={() => setActiveTab('tokens')}
          className={activeTab === 'tokens' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          <Radio size={15} />
          Histórico & Auditoria
        </button>
      </div>

      {/* ABA 1: GERADOR DE TOKENS */}
      {activeTab === 'generator' && (
        <div className="glass-card">
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '6px', color: '#ffffff' }}>
            Gerar Link de Resgate Seguro
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Crie um link temporário para enviar ao comprador da conta Steam.
          </p>

          {accounts.length === 0 ? (
            <div
              style={{
                textAlign: 'center',
                padding: '30px',
                background: 'rgba(0,0,0,0.2)',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              <Gamepad2 size={32} color="var(--text-dark)" style={{ margin: '0 auto 10px' }} />
              <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                Nenhuma conta Steam cadastrada ainda.
              </div>
              <button onClick={() => setActiveTab('accounts')} className="btn-primary" style={{ fontSize: '0.85rem' }}>
                <Plus size={15} />
                Cadastrar Primeira Conta
              </button>
            </div>
          ) : (
            <form onSubmit={handleGenerateToken} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="grid-2">
                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Selecione a Conta Steam:
                  </label>
                  <select
                    value={selectedAccountId}
                    onChange={(e) => setSelectedAccountId(Number(e.target.value))}
                    required
                    style={{ width: '100%' }}
                  >
                    {accounts.map((acc) => (
                      <option key={acc.id} value={acc.id}>
                        {acc.username} {acc.display_name ? `(${acc.display_name})` : ''}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Tempo de Expiração do Link:
                  </label>
                  <select
                    value={tokenExpiresSeconds}
                    onChange={(e) => setTokenExpiresSeconds(Number(e.target.value))}
                    style={{ width: '100%' }}
                  >
                    <option value={1800}>30 minutos</option>
                    <option value={3600}>1 hora (Padrão)</option>
                    <option value={86400}>24 horas</option>
                    <option value={604800}>7 dias</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Quantidade Máxima de Resgates Permitidos:
                </label>
                <select
                  value={tokenMaxUses}
                  onChange={(e) => setTokenMaxUses(Number(e.target.value))}
                  style={{ width: '100%', maxWidth: '280px' }}
                >
                  <option value={1}>1 Resgate (Recomendado)</option>
                  <option value={2}>2 Resgates</option>
                  <option value={5}>5 Resgates</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={isGeneratingToken}
                className="btn-primary"
                style={{ width: 'fit-content', padding: '12px 28px', marginTop: '8px' }}
              >
                {isGeneratingToken ? <Loader2 className="spin" size={16} /> : <KeyRound size={16} />}
                Gerar Link para o Cliente
              </button>
            </form>
          )}

          {/* Resultado do Token Gerado */}
          {generatedTokenResult && (
            <div
              style={{
                marginTop: '28px',
                background: 'rgba(26, 159, 255, 0.08)',
                border: '1px solid var(--border-active)',
                borderRadius: 'var(--radius-sm)',
                padding: '20px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--steam-cyan)', fontWeight: 600, marginBottom: '8px' }}>
                <Check size={18} />
                Link de Resgate Gerado com Sucesso!
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
                Repasse este link para o comprador. Ao acessar, ele poderá resgatar o código de 5 dígitos sem precisar de suporte manual:
              </p>

              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <input
                  type="text"
                  readOnly
                  value={generatedTokenResult.token_url}
                  style={{ flex: 1, minWidth: '280px', fontFamily: 'var(--font-mono)', fontSize: '0.88rem' }}
                />
                <button onClick={handleCopyLink} className="btn-primary" style={{ padding: '10px 18px' }}>
                  {tokenCopied ? <Check size={16} /> : <Copy size={16} />}
                  {tokenCopied ? 'Link Copiado!' : 'Copiar Link'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ABA 2: CONTAS STEAM */}
      {activeTab === 'accounts' && (
        <div className="glass-card">
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '6px', color: '#ffffff' }}>
            Contas Steam Gerenciadas
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Cadastre os logins das contas Steam que você comercializa.
          </p>

          <form onSubmit={handleAddAccount} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '24px' }}>
            <input
              type="text"
              required
              value={newAccountUsername}
              onChange={(e) => setNewAccountUsername(e.target.value)}
              placeholder="Login da Conta Steam (ex: cs2_vendedor_01)"
              style={{ flex: 1, minWidth: '220px' }}
            />
            <input
              type="text"
              value={newAccountDisplayName}
              onChange={(e) => setNewAccountDisplayName(e.target.value)}
              placeholder="Apelido / Descrição (opcional)"
              style={{ flex: 1, minWidth: '200px' }}
            />
            <button type="submit" disabled={isAddingAccount} className="btn-primary" style={{ padding: '10px 20px' }}>
              {isAddingAccount ? <Loader2 className="spin" size={16} /> : <Plus size={16} />}
              Adicionar Conta
            </button>
          </form>

          {/* Lista de Contas */}
          {accounts.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Nenhuma conta cadastrada.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '10px' }}>ID</th>
                    <th style={{ padding: '10px' }}>Login Steam</th>
                    <th style={{ padding: '10px' }}>Descrição</th>
                    <th style={{ padding: '10px' }}>Status</th>
                    <th style={{ padding: '10px', textAlign: 'right' }}>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {accounts.map((acc) => (
                    <tr key={acc.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '12px 10px', color: 'var(--text-dark)' }}>#{acc.id}</td>
                      <td style={{ padding: '12px 10px', fontWeight: 600, color: '#ffffff' }}>{acc.username}</td>
                      <td style={{ padding: '12px 10px', color: 'var(--text-muted)' }}>{acc.display_name || '-'}</td>
                      <td style={{ padding: '12px 10px' }}>
                        <span className="badge badge-success">Ativa</span>
                      </td>
                      <td style={{ padding: '12px 10px', textAlign: 'right' }}>
                        <button
                          onClick={() => handleDeleteAccount(acc.id)}
                          className="btn-secondary"
                          style={{ padding: '6px 10px', color: 'var(--color-error)' }}
                          title="Remover conta"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ABA 3: SERVIDOR IMAP */}
      {activeTab === 'imap' && (
        <div className="glass-card">
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '6px', color: '#ffffff' }}>
            Configurações de E-mail IMAP
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
            O backend conecta a este servidor de e-mail via TLS seguro (Porta 993) para capturar os códigos Steam Guard.
            Sua senha é criptografada com a chave Fernet em repouso.
          </p>

          <form onSubmit={handleSaveImap} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="grid-2">
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Servidor IMAP (Host):
                </label>
                <input
                  type="text"
                  required
                  value={imapHost}
                  onChange={(e) => setImapHost(e.target.value)}
                  placeholder="imap.gmail.com"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Porta TCP:
                </label>
                <input
                  type="number"
                  required
                  value={imapPort}
                  onChange={(e) => setImapPort(Number(e.target.value))}
                  placeholder="993"
                  style={{ width: '100%' }}
                />
              </div>
            </div>

            <div className="grid-2">
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  E-mail do Revendedor (Username):
                </label>
                <input
                  type="email"
                  required
                  value={imapUsername}
                  onChange={(e) => setImapUsername(e.target.value)}
                  placeholder="seu-email@gmail.com"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Senha de Aplicativo (App Password):
                </label>
                <input
                  type="password"
                  value={imapPassword}
                  onChange={(e) => setImapPassword(e.target.value)}
                  placeholder={imapConfig ? '•••••••••••• (Criptografada no banco)' : 'Digite a senha do e-mail'}
                  style={{ width: '100%' }}
                />
              </div>
            </div>

            {/* Teste e Feedback */}
            {imapTestResult && (
              <div
                style={{
                  background: imapTestResult.success ? 'var(--color-success-bg)' : 'var(--color-error-bg)',
                  border: `1px solid ${imapTestResult.success ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                  borderRadius: 'var(--radius-sm)',
                  padding: '12px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  fontSize: '0.85rem',
                  color: imapTestResult.success ? 'var(--color-success)' : 'var(--color-error)',
                }}
              >
                {imapTestResult.success ? <Check size={18} /> : <AlertCircle size={18} />}
                <span>
                  {imapTestResult.message} ({imapTestResult.response_time_ms}ms)
                </span>
              </div>
            )}

            {imapMessage && (
              <div
                style={{
                  background: 'var(--color-success-bg)',
                  border: '1px solid rgba(34, 197, 94, 0.3)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '12px 16px',
                  fontSize: '0.85rem',
                  color: 'var(--color-success)',
                }}
              >
                {imapMessage}
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '10px' }}>
              <button
                type="button"
                onClick={handleTestImap}
                disabled={isTestingImap}
                className="btn-secondary"
                style={{ padding: '10px 20px' }}
              >
                {isTestingImap ? <Loader2 className="spin" size={15} /> : <ShieldCheck size={15} />}
                Testar Conexão IMAP
              </button>

              <button
                type="submit"
                disabled={isSavingImap}
                className="btn-primary"
                style={{ padding: '10px 24px' }}
              >
                {isSavingImap ? <Loader2 className="spin" size={15} /> : <Mail size={15} />}
                Salvar Credenciais Criptografadas
              </button>
            </div>
          </form>
        </div>
      )}

      {/* ABA 4: HISTÓRICO & AUDITORIA */}
      {activeTab === 'tokens' && (
        <div className="glass-card">
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '6px', color: '#ffffff' }}>
            Tokens de Resgate Emitidos
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Rastreabilidade completa de tokens e auditoria com hashes seguros.
          </p>

          {tokens.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Nenhum token gerado até o momento.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '10px' }}>ID</th>
                    <th style={{ padding: '10px' }}>Hash do Token</th>
                    <th style={{ padding: '10px' }}>Conta</th>
                    <th style={{ padding: '10px' }}>Usos</th>
                    <th style={{ padding: '10px' }}>Status</th>
                    <th style={{ padding: '10px' }}>Expiração</th>
                    <th style={{ padding: '10px', textAlign: 'right' }}>Ação</th>
                  </tr>
                </thead>
                <tbody>
                  {tokens.map((t) => {
                    const isExpired = new Date(t.expires_at) < new Date();
                    return (
                      <tr key={t.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                        <td style={{ padding: '12px 10px', color: 'var(--text-dark)' }}>#{t.id}</td>
                        <td style={{ padding: '12px 10px', fontFamily: 'var(--font-mono)' }}>{t.token_hash_masked}</td>
                        <td style={{ padding: '12px 10px', color: 'var(--text-muted)' }}>Conta #{t.steam_account_id}</td>
                        <td style={{ padding: '12px 10px' }}>
                          {t.current_uses} / {t.max_uses}
                        </td>
                        <td style={{ padding: '12px 10px' }}>
                          {!t.is_active ? (
                            <span className="badge badge-error">Revogado</span>
                          ) : isExpired ? (
                            <span className="badge badge-warning">Expirado</span>
                          ) : (
                            <span className="badge badge-success">Ativo</span>
                          )}
                        </td>
                        <td style={{ padding: '12px 10px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                          {new Date(t.expires_at).toLocaleString('pt-BR')}
                        </td>
                        <td style={{ padding: '12px 10px', textAlign: 'right' }}>
                          {t.is_active && !isExpired && (
                            <button
                              onClick={async () => {
                                await api.tokens.revoke(t.id);
                                const updated = await api.tokens.list();
                                setTokens(updated);
                              }}
                              className="btn-secondary"
                              style={{ padding: '4px 8px', fontSize: '0.75rem', color: 'var(--color-error)' }}
                            >
                              Revogar
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

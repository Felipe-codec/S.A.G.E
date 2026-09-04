import {
  CodeResponse,
  ImapConfig,
  ImapTestResponse,
  RedemptionInfo,
  Seller,
  SteamAccount,
  TokenGenerateResponse,
  TokenRecord,
} from '../types';

// URL base da API configurada no ambiente (Vercel ou local)
const BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('steam_guard_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include', // Envia cookies seguros se configurados
  });

  if (!response.ok) {
    let errorMessage = `Erro HTTP ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // Falha ao parsear JSON
    }
    throw new Error(errorMessage);
  }

  // 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  // Autenticação
  auth: {
    login: async (email: string, password: string) => {
      const data = await request<{ access_token: string; seller: Seller }>(
        '/api/v1/auth/login',
        {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        }
      );
      if (data.access_token) {
        localStorage.setItem('steam_guard_token', data.access_token);
      }
      return data;
    },
    register: (email: string, password: string) =>
      request<Seller>('/api/v1/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    me: () => request<Seller>('/api/v1/auth/me'),
    logout: async () => {
      try {
        await request('/api/v1/auth/logout', { method: 'POST' });
      } finally {
        localStorage.removeItem('steam_guard_token');
      }
    },
  },

  // Contas Steam
  steamAccounts: {
    list: () => request<SteamAccount[]>('/api/v1/steam-accounts'),
    create: (username: string, displayName?: string) =>
      request<SteamAccount>('/api/v1/steam-accounts', {
        method: 'POST',
        body: JSON.stringify({ username, display_name: displayName }),
      }),
    update: (id: number, displayName?: string, isActive?: boolean) =>
      request<SteamAccount>(`/api/v1/steam-accounts/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ display_name: displayName, is_active: isActive }),
      }),
    delete: (id: number) =>
      request<void>(`/api/v1/steam-accounts/${id}`, { method: 'DELETE' }),
  },

  // Configurações IMAP
  imap: {
    get: () => request<ImapConfig>('/api/v1/imap-configs'),
    save: (config: {
      host: string;
      port: number;
      username: string;
      password: string;
      use_ssl: boolean;
    }) =>
      request<ImapConfig>('/api/v1/imap-configs', {
        method: 'POST',
        body: JSON.stringify(config),
      }),
    test: (config: {
      host: string;
      port: number;
      username: string;
      password?: string;
      use_ssl: boolean;
    }) =>
      request<ImapTestResponse>('/api/v1/imap-configs/test', {
        method: 'POST',
        body: JSON.stringify(config),
      }),
  },

  // Tokens
  tokens: {
    list: () => request<TokenRecord[]>('/api/v1/tokens'),
    generate: (steamAccountId: number, expiresInSeconds?: number, maxUses?: number) =>
      request<TokenGenerateResponse>('/api/v1/tokens/generate', {
        method: 'POST',
        body: JSON.stringify({
          steam_account_id: steamAccountId,
          expires_in_seconds: expiresInSeconds,
          max_uses: maxUses,
        }),
      }),
    revoke: (id: number) =>
      request<{ message: string }>(`/api/v1/tokens/${id}/revoke`, {
        method: 'POST',
      }),
  },

  // Resgate Público
  redemption: {
    getInfo: (rawToken: string) =>
      request<RedemptionInfo>(`/resgate/${rawToken}/info`),
    requestCode: (rawToken: string) =>
      request<CodeResponse>(`/resgate/${rawToken}/code`, {
        method: 'POST',
        body: JSON.stringify({}),
      }),
  },

  // Health
  health: {
    check: () => request<{ status: string; app_env: string }>('/health'),
    ready: () =>
      request<{ status: string; database: string; redis: string }>('/health/ready'),
  },
};

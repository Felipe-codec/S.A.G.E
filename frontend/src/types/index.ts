export interface Seller {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface SteamAccount {
  id: number;
  seller_id: number;
  username: string;
  display_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ImapConfig {
  id: number;
  seller_id: number;
  host: string;
  port: number;
  username: string;
  use_ssl: boolean;
  created_at: string;
  updated_at: string;
}

export interface ImapTestResponse {
  success: boolean;
  message: string;
  response_time_ms: number;
}

export interface TokenRecord {
  id: number;
  steam_account_id: number;
  token_hash_masked: string;
  max_uses: number;
  current_uses: number;
  expires_at: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenGenerateResponse {
  id: number;
  token: string;
  token_url: string;
  steam_account_id: number;
  steam_username: string;
  expires_at: string;
  max_uses: number;
}

export interface RedemptionInfo {
  valid: boolean;
  steam_username: string;
  display_name: string | null;
  expires_at: string;
  remaining_uses: number;
  message?: string;
}

export interface CodeResponse {
  success: boolean;
  code: string | null;
  message: string;
  expires_in_seconds: number;
  search_duration_ms: number;
}

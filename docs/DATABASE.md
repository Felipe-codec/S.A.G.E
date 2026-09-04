# Modelo de Dados e Banco de Dados (PostgreSQL / Supabase)

Este documento documenta o esquema relacional, estratégia de indexação, configuração de pooling de conexões no Supabase e procedimentos de backup/recuperação do sistema.

---

## 1. Diagrama Entidade-Relacionamento (ERD)

```mermaid
erDiagram
    SELLERS ||--o{ IMAP_CONFIGS : possui
    SELLERS ||--o{ STEAM_ACCOUNTS : cadastra
    SELLERS ||--o{ REDEMPTION_TOKENS : emite
    SELLERS ||--o{ ACCESS_LOGS : audita

    STEAM_ACCOUNTS ||--o{ REDEMPTION_TOKENS : vincula
    STEAM_ACCOUNTS ||--o{ CODE_REQUESTS : registra

    REDEMPTION_TOKENS ||--o{ REDEMPTION_SESSIONS : inicia
    REDEMPTION_TOKENS ||--o{ CODE_REQUESTS : gera

    SELLERS {
        int id PK
        string email UK
        string hashed_password
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    IMAP_CONFIGS {
        int id PK
        int seller_id FK
        string host
        int port
        string username
        text encrypted_password
        boolean use_ssl
        timestamp created_at
        timestamp updated_at
    }

    STEAM_ACCOUNTS {
        int id PK
        int seller_id FK
        string username
        string display_name
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    REDEMPTION_TOKENS {
        int id PK
        int steam_account_id FK
        int seller_id FK
        string token_hash UK
        int max_uses
        int current_uses
        timestamp expires_at
        boolean is_active
        timestamp created_at
    }

    REDEMPTION_SESSIONS {
        int id PK
        int token_id FK
        string session_identifier_hash
        string ip_address_masked
        string user_agent
        timestamp created_at
        timestamp expires_at
    }

    CODE_REQUESTS {
        int id PK
        int steam_account_id FK
        int token_id FK
        timestamp requested_at
        string status
        string code_found_masked
        int search_duration_ms
        text error_message
    }

    ACCESS_LOGS {
        int id PK
        int seller_id FK
        string request_id
        string endpoint
        string method
        string ip_masked
        int status_code
        int duration_ms
        timestamp created_at
    }
```

---

## 2. Estratégia de Índices e Performance

Todos os índices foram criados na migração inicial do Alembic para evitar consultas com full table scan durante picos de resgate:

1. **`steam_accounts.seller_id` & `steam_accounts.username`**:
   - Índice composto `ix_steam_accounts_seller_username` (`seller_id`, `username`) para consultas rápidas na verificação de unicidade por revendedor.
2. **`redemption_tokens.token_hash`**:
   - Índice único `ix_redemption_tokens_token_hash` garantindo busca O(1) de links públicos através do hash SHA-256.
3. **`redemption_tokens.steam_account_id` & `redemption_tokens.expires_at`**:
   - Índice composto `ix_redemption_tokens_account_expires` para validação ultra-rápida de vigência de links de resgate.
4. **`redemption_sessions.token_id`**:
   - Índice `ix_redemption_sessions_token_id` para correlacionar sessões ativas com o token correspondente.
5. **`code_requests.steam_account_id` & `code_requests.requested_at`**:
   - Índice composto `ix_code_requests_account_requested` para gráficos e estatísticas cronológicas de resgates por conta.
6. **`access_logs.seller_id` & `access_logs.created_at`**:
   - Índices para auditoria e relatórios de segurança do revendedor.

---

## 3. Configuração de Conexão no Supabase (Connection Pooling)

O Supabase oferece conexões diretas e conexões gerenciadas por Pooler (PgBouncer/Supavisor).

### Modos Disponíveis:
1. **Transaction Mode (Porta 6543) — RECOMENDADO PARA CLOUD**:
   - Permite que centenas de requisições compartilhem um pool restrito de conexões PostgreSQL reais.
   - Suporta IPv4 em todas as regiões.
   - Formato da URL:
     ```
     postgresql://postgres.[REF]:[SENHA]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
     ```
2. **Session Mode (Porta 5432)**:
   - Mantém a conexão aberta enquanto durar a sessão do cliente.
3. **Direct Connection (Porta 5432)**:
   - Conexão direta com a instância do PostgreSQL. Em algumas redes cloud gratuitas (como Render), conexões IPv6 puras podem falhar; por isso o Pooler IPv4 na porta 6543 é a opção mais segura e estável.

### Parâmetros no SQLAlchemy Engine:
No arquivo `backend/app/db/session.py`:
- `pool_pre_ping=True`: Testa a conexão antes de cada consulta (`SELECT 1`), descartando sockets que o Supabase possa ter fechado por inatividade.
- `pool_recycle=300`: Recicla as conexões a cada 5 minutos.
- `connect_timeout=10`: Limita o tempo de espera caso haja instabilidade passageira na rede.

---

## 4. Procedimentos de Backup e Restauração

A aplicação não armazena dados em volumes locais efêmeros do Docker. Todo o estado reside no Supabase PostgreSQL.

### 1. Backup Automático do Supabase
- O Supabase realiza backups diários automáticos retidos conforme o plano do projeto.

### 2. Exportação Manual com `pg_dump`
Para exportar uma cópia completa de segurança:
```bash
pg_dump "postgresql://postgres.[REF]:[SENHA]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require" \
  --format=custom \
  --no-owner \
  --file=backup_steam_guard_$(date +%Y%m%d_%H%M%S).dump
```

### 3. Restauração com `pg_restore`
Para restaurar a base de dados em um novo servidor ou instância local:
```bash
pg_restore --clean --if-exists --no-owner \
  --dbname="postgresql://novo_usuario:nova_senha@host:5432/nova_base" \
  backup_steam_guard.dump
```

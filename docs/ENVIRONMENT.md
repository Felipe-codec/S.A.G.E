# Dicionário de Variáveis de Ambiente

Este documento cataloga todas as variáveis de ambiente utilizadas pelo **Steam Guard Resgate**, especificando tipo, valores padrão, sensibilidade e regras por ambiente.

---

## Tabela Geral de Variáveis

| Variável | Tipo | Padrão (Dev) | Sensibilidade | Onde Configurar | Descrição |
|---|---|---|---|---|---|
| `APP_ENV` | String | `development` | Baixa | Render / Docker | Ambiente: `development`, `production` ou `test`. |
| `PORT` | Inteiro | `8000` | Baixa | Render / Docker | Porta TCP de escuta do Uvicorn (0.0.0.0:$PORT). |
| `DATABASE_URL` | String (URI) | `postgresql://...` | **Crítica** | Render (Secrets) / Local | URL de conexão PostgreSQL (Supabase ou Local). |
| `JWT_SECRET` | String (Hex) | Dev string | **Crítica** | Render (Secrets) | Chave secreta de assinatura dos tokens JWT (mínimo 32 caracteres). |
| `MASTER_ENCRYPTION_KEY` | String (Base64) | Sample Fernet | **Crítica** | Render (Secrets) | Chave Fernet de 32 bytes para criptografia simétrica de senhas IMAP. |
| `CORS_ORIGINS` | String (CSV/JSON)| `http://localhost:5173` | Alta | Render | Lista de URLs do frontend autorizadas para requisições cross-origin com cookies. |
| `FRONTEND_URL` | String (URL) | `http://localhost:5173` | Média | Render | URL base pública do Frontend usada na montagem dos links de resgate. |
| `IMAP_TIMEOUT` | Inteiro | `5` | Baixa | Render / Docker | Timeout máximo em segundos para conexão com servidores IMAP. |
| `CODE_POLL_INTERVAL` | Inteiro | `2` | Baixa | Render / Docker | Intervalo em segundos entre verificações da caixa de entrada. |
| `CODE_POLL_TIMEOUT` | Inteiro | `15` | Baixa | Render / Docker | Tempo máximo total de espera pelo e-mail da Steam. |
| `RATE_LIMIT` | String | `60/minute` | Média | Render / Docker | Taxa limite global padrão da API. |
| `TOKEN_DEFAULT_EXPIRATION`| Inteiro | `3600` | Baixa | Render / Docker | Duração padrão dos links de resgate em segundos (3600 = 1h). |
| `REDIS_URL` | String (URI) | `""` (vazio) | Alta | Render (opcional) | Connection string do Redis (Upstash). Se vazio, utiliza memória RAM. |
| `VITE_API_URL` | String (URL) | `http://localhost:8000`| Baixa (Pública) | Vercel (Environment) | URL base da API do backend consumida pelo navegador. |

---

## Regras Específicas por Ambiente

### 1. Ambiente `development`
- As variáveis utilizam padrões tolerantes definidos no `.env.example`.
- `DATABASE_URL` pode apontar para o PostgreSQL local do Docker Compose (`localhost:5432`).
- Chaves de teste locais são permitidas.

### 2. Ambiente `production`
- **Validação Estrita de Inicialização**: Se `APP_ENV=production`, o backend recusa iniciar se:
  - `JWT_SECRET` possuir menos de 32 caracteres ou contiver a palavra `dev`.
  - `MASTER_ENCRYPTION_KEY` contiver o termo de exemplo `sample`.
  - `CORS_ORIGINS` contiver o caractere curinga `*`.
  - `DATABASE_URL` apontar para `localhost` ou `127.0.0.1`.

### 3. Ambiente `test`
- Configurado automaticamente pelo `conftest.py`.
- Utiliza SQLite em memória (`sqlite:///:memory:`) para garantir execução rápida e determinística sem dependência externa.

---

## Como Gerar Segredos Seguros

### 1. Gerar `JWT_SECRET`
Execute no terminal:
```bash
openssl rand -hex 32
```

### 2. Gerar `MASTER_ENCRYPTION_KEY`
Execute no terminal Python:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Exemplo de saída: `VZaokCbhHYZg5M6sslHozPjTZijU5bGgm74kVXE7JB8=`

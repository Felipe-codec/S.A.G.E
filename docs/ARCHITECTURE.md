# Arquitetura do Sistema — Steam Guard Resgate

Este documento detalha o desenho arquitetural do **Steam Guard Resgate**, cobrindo o fluxo de dados, padrões de resiliência, modelo de abstração para Redis e diretrizes para expansão de infraestrutura.

---

## 1. Diagrama de Topologia de Rede

```mermaid
flowchart TD
    subgraph Cliente [Ambiente do Comprador]
        BrowserUser[Navegador Web do Cliente]
        SteamClient[Cliente Desktop / Web da Steam]
    end

    subgraph Revendedor [Ambiente do Vendedor]
        BrowserAdmin[Painel do Revendedor]
        EmailProvider[Servidor de E-mail do Revendedor\n(Gmail/Outlook/Zoho IMAP)]
    end

    subgraph CloudFree [Infraestrutura Cloud Inicial (R$ 0)]
        Vercel[Vercel Edge Network\nFrontend React/Vite (SPA)]
        Render[Render Web Service\nBackend FastAPI (Docker Container)]
        Supabase[(Supabase\nPostgreSQL 16 Gerenciado)]
        RedisCache[(Upstash Redis\nOpcional / Futuro)]
    end

    BrowserUser -->|HTTPS| Vercel
    BrowserAdmin -->|HTTPS| Vercel
    Vercel -->|REST API HTTPS / CORS| Render

    Render -->|SQLAlchemy 2.0 / SSL :6543| Supabase
    Render -.->|Leitura e Escrita de Cache / Rate Limit| RedisCache
    Render -->|IMAPS :993 / TLS Seguro| EmailProvider

    SteamClient -->|Dispara envio de e-mail com código| EmailProvider
```

---

## 2. Fluxos Principais de Execução

### Fluxo A: Geração de Token pelo Revendedor
1. O Revendedor se autentica no painel através de `POST /api/v1/auth/login`.
2. O Backend emite cookie seguro `SameSite=None; Secure=True` e token JWT.
3. O Revendedor seleciona a conta Steam e clica em **Gerar Link de Resgate**.
4. O Backend gera um token criptográfico URL-safe de 32 bytes (`secrets.token_urlsafe(32)`).
5. O Backend calcula o hash SHA-256 do token e persiste na tabela `redemption_tokens`. O token em texto plano nunca é salvo no banco.
6. A URL pública `https://app.vercel.app/resgate/<token>` é retornada ao revendedor para repasse ao comprador.

### Fluxo B: Resgate do Código Steam Guard pelo Comprador
1. O Comprador acessa o link de resgate no navegador.
2. O Frontend consulta `GET /resgate/{token}/info`:
   - O Backend calcula o hash SHA-256 do token da URL e valida expiração, status ativo e quantidade de usos restantes.
   - Retorna o login da conta Steam (sem expor senhas ou dados do revendedor).
3. O Comprador tenta logar na Steam com os dados recebidos. A Valve envia o código para a caixa de entrada do revendedor.
4. O Comprador clica em **"Obter Código Steam Guard"** (`POST /resgate/{token}/code`):
   - **Rate Limiting**: O backend aplica limite estrito (ex: máximo de 5 requisições por minuto por IP/sessão) através da camada de RateLimit.
   - **Descriptografia sob Demanda**: O backend busca a configuração IMAP do revendedor e descriptografa a senha em memória com a `MASTER_ENCRYPTION_KEY` (Fernet).
   - **Polling IMAP**: O backend abre conexão TLS na porta 993 com timeout rigoroso (5s), busca as mensagens recentes da Valve e extrai o código de 5 dígitos alfanuméricos via regex.
   - **Fechamento Seguro**: A conexão IMAP é garantidamente fechada no bloco `finally`.
   - **Auditoria**: O código é registrado no banco de dados e nos logs em versão mascarada (ex: `***7G`).
   - O código completo é retornado ao comprador na resposta HTTP, acompanhado de um timer de expiração de 60 segundos.

---

## 3. Abstração de Cache e Rate Limiting (Redis vs Memória)

A aplicação foi desenvolvida seguindo o princípio da inversão de dependência (DIP). Toda manipulação de cache e rate limiting é realizada através de contratos abstratos:

- `AbstractCacheService` -> `MemoryCacheService` / `RedisCacheService`
- `AbstractRateLimitService` -> `MemoryRateLimitService` / `RedisRateLimitService`
- `AbstractLockService` -> `MemoryLockService` / `RedisLockService`

### Comportamento em Tempo de Execução:
- **`REDIS_URL` não configurada**: A aplicação utiliza automaticamente as implementações em memória RAM (Sliding Window thread-safe). O MVP funciona sem dependências adicionais.
- **`REDIS_URL` configurada**: A aplicação se conecta ao Redis (Upstash Redis, Redis Cloud ou Redis local) e passa a executar operações distribuídas e atômicas usando comandos ZSET e chaves com TTL automático.
- **Resiliência a Falhas (Fail-open)**: Caso o Redis caia ou enfrente problemas de rede temporários, o `RateLimitService` efetua fallback inteligente para evitar interrupção no fluxo de resgates.

---

## 4. Estratégia de Migração Futura (Sem Retrabalho)

A arquitetura não possui amarras com provedores específicos. Para escalar:

| Componente Atual | Próximo Nível (Médio Porte) | Nível Enterprise | Alteração no Código Necessária |
|---|---|---|---|
| **Render (Free)** | Render Team / VPS Hetzner / DigitalOcean | AWS ECS Fargate / Kubernetes | **Nenhuma**. Basta rodar o mesmo Dockerfile. |
| **Supabase (Free)** | Supabase Pro / RDS PostgreSQL | AWS Aurora PostgreSQL Multi-AZ | **Nenhuma**. Apenas atualizar a `DATABASE_URL`. |
| **In-Memory Cache** | Upstash Redis Serverless | Redis Cluster Dedicado | **Nenhuma**. Apenas configurar `REDIS_URL`. |
| **Vercel (Hobby)** | Vercel Pro | Cloudflare Pages / AWS CloudFront + S3 | **Nenhuma**. Build padrão estático Vite (`dist`). |
| **Domínios Padrão** | Domínios personalizados (`app.suaempresa.com.br`) | Domínios personalizados com CDN Cloudflare | **Nenhuma**. Atualizar `CORS_ORIGINS` e `VITE_API_URL`. |

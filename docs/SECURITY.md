# Modelo de Segurança e Proteção de Dados

Este documento descreve as políticas criptográficas, arquitetura de segredos e controles de proteção contra ameaças implementados no sistema **Steam Guard Resgate**.

---

## 1. Criptografia Simétrica de Senhas IMAP (`MASTER_ENCRYPTION_KEY`)

As senhas dos e-mails dos revendedores são dados altamente críticos. O sistema adota as seguintes regras inegociáveis:

1. **Criptografia em Repouso**: Nenhuma credencial IMAP é salva em texto plano no banco de dados. Elas são criptografadas com **Fernet** (baseado em AES-128-CBC com HMAC-SHA256 para autenticação de integridade).
2. **Descriptografia Exclusiva em Memória**: A senha é descriptografada em memória RAM apenas no exato milissegundo em que a conexão TLS com o servidor IMAP é aberta, sendo descartada imediatamente após o encerramento do bloco.
3. **Isolamento de Segredos**: A `MASTER_ENCRYPTION_KEY` existe **estritamente no backend**. Ela nunca é compartilhada com o frontend, nunca é exposta em variáveis `VITE_*` e nunca é enviada ao navegador.
4. **Suporte a Rotação de Chaves**: A classe `CryptoManager` utiliza `MultiFernet`, permitindo injetar uma chave primária nova e chaves antigas de fallback, descriptografando credenciais anteriores e efetuando a re-encriptação sem downtime.

---

## 2. Mascaramento e Sanitização de Logs

Para impedir vazamento acidental de segredos em agregadores de log (como Render Logs, Datadog ou CloudWatch):

- **Filtro de Regex de Sanitização**: O formatador `StructuredJsonFormatter` inspeciona todas as mensagens emitidas.
- **Códigos Steam Guard**: São registrados exclusivamente de forma mascarada (ex: `***7G`).
- **Tokens de Resgate**: São registrados em formato truncado (ex: `a1b2...9z8y`).
- **Senhas e JWTs**: Substituídos automaticamente por `[REDACTED]` e `[REDACTED_JWT]`.
- **IPs de Clientes**: Mascarados em conformidade com LGPD/GDPR (ex: `187.54.***.***`).
- **DATABASE_URL**: Oculta a senha em caso de exibição em logs.

---

## 3. Autenticação Administrativa e Cookies

A aplicação atende à particularidade de ambientes cloud onde o frontend está na Vercel (`*.vercel.app`) e o backend está no Render (`*.onrender.com`):

- **Cookies HttpOnly e Secure**: Em produção, os cookies de autenticação possuem as flags:
  - `HttpOnly = True` (impede leitura via JavaScript no navegador).
  - `Secure = True` (transmitido exclusivamente via HTTPS).
  - `SameSite = "None"` (permite envio cross-site legítimo entre Vercel e Render).
- **Autenticação Dual (Bearer Fallback)**: Como navegadores modernos (Safari ITP, Firefox ETP, Chrome Privacy Sandbox) podem bloquear cookies de terceiros por padrão, o backend aceita o token de autenticação tanto pelo cookie quanto pelo cabeçalho HTTP:
  ```
  Authorization: Bearer <token_jwt>
  ```
  Isso garante que revendedores consigam usar o painel em qualquer dispositivo ou navegador sem falhas de login.

---

## 4. Rate Limiting e Prevenção de Abuso

Para proteger os servidores IMAP contra bloqueios por excesso de requisições:

1. **Endpoint Público `POST /resgate/{token}/code`**:
   - Limite específico de **5 requisições por minuto** por combinação de IP e Token.
   - Retorna HTTP 429 com cabeçalho `Retry-After`.
2. **Endpoint de Autenticação `POST /api/v1/auth/login`**:
   - Limite restrito para mitigação de ataques de força bruta contra senhas de revendedores.
3. **Persistência do Rate Limit**:
   - No MVP: In-memory sliding window.
   - Com Redis: Chaves distribuídas atômicas (Sorted Sets) permitindo escalabilidade horizontal em múltiplos containers.

---

## 5. Cabeçalhos de Segurança HTTP (OWASP)

O middleware `SecurityHeadersMiddleware` injeta em todas as respostas:
- `X-Content-Type-Options: nosniff` (impede sniffing de MIME types).
- `X-Frame-Options: DENY` (bloqueia incorporação em iframes para prevenir clickjacking).
- `X-XSS-Protection: 1; mode=block` (proteção contra cross-site scripting legado).
- `Referrer-Policy: strict-origin-when-cross-origin` (previne vazamento de URLs internas em referrers).
- `Strict-Transport-Security (HSTS)`: Ativado automaticamente em `production` com duração de 1 ano (`max-age=31536000`).

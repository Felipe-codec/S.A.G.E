# Guia Completo de Deploy — Steam Guard Resgate (R$ 0/mês)

Este guia orienta o deploy completo do sistema **Steam Guard Resgate** em serviços gratuitos na nuvem (Supabase + Render + Vercel). A arquitetura é 100% expansível para VPS ou nuvens dedicadas sem retrabalho.

---

## Índice
1. [Passo 1: Repositório GitHub](#passo-1-repositório-github)
2. [Passo 2: Banco de Dados Supabase (PostgreSQL)](#passo-2-banco-de-dados-supabase-postgresql)
3. [Passo 3: Geração de Chaves Criptográficas](#passo-3-geração-de-chaves-criptográficas)
4. [Passo 4: Deploy do Backend no Render](#passo-4-deploy-do-backend-no-render)
5. [Passo 5: Deploy do Frontend na Vercel](#passo-5-deploy-do-frontend-na-vercel)
6. [Passo 6: Conexão Cruzada (CORS e URLs)](#passo-6-conexão-cruzada-cors-e-urls)
7. [Passo 7: Verificação e Teste de Ponta a Ponta](#passo-7-verificação-e-teste-de-ponta-a-ponta)

---

## Passo 1: Repositório GitHub

1. Inicialize o repositório git localmente:
   ```bash
   git init
   git add .
   git commit -m "feat: initial release steam guard resgate infrastructure"
   ```
2. Crie um novo repositório privado ou público no [GitHub](https://github.com/new).
3. Conecte o remoto e faça o push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   git push -u origin main
   ```

---

## Passo 2: Banco de Dados Supabase (PostgreSQL)

O Supabase oferece 500 MB de PostgreSQL gerenciado gratuitamente no plano Free.

1. Acesse [supabase.com](https://supabase.com) e crie uma conta gratuita.
2. Clique em **"New project"**:
   - Nome: `steam-guard-db`
   - Database Password: Crie uma senha forte (anote-a!).
   - Region: Escolha a região mais próxima (ex: `South America (São Paulo)` ou `East US`).
3. Obtenha a connection string para o Render:
   - Vá em **Project Settings** (ícone de engrenagem) > **Database**.
   - Na seção **Connection string**, selecione a aba **URI**.
   - Alterne o modo para **Transaction** (Porta `6543`) ou **Session** (Porta `5432`).
     *Recomendado para Render/Cloud*: **Transaction Pooler (Porta 6543)** com IPv4.
   - O formato será:
     ```
     postgresql://postgres.[PROJECT-REF]:[SUA-SENHA]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
     ```
   - Substitua `[SUA-SENHA]` pela senha definida.

---

## Passo 3: Geração de Chaves Criptográficas

Antes de configurar o Render, gere localmente duas chaves criptograficamente fortes:

1. **`JWT_SECRET`** (mínimo 32 caracteres):
   ```bash
   openssl rand -hex 32
   ```
2. **`MASTER_ENCRYPTION_KEY`** (chave Fernet de 32 bytes URL-safe base64):
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
   *Guarde a `MASTER_ENCRYPTION_KEY` em local seguro. Ela nunca deve ser compartilhada nem enviada ao frontend!*

---

## Passo 4: Deploy do Backend no Render

1. Acesse [render.com](https://render.com) e faça login com sua conta do GitHub.
2. Você pode realizar o deploy via **Blueprint** (automático com `render.yaml`) ou manualmente:

### Opção A: Deploy Automático via Blueprint
- No painel do Render, clique em **"New +"** > **"Blueprint"**.
- Selecione o repositório `regaste-codigo-steam`.
- O Render detectará automaticamente o arquivo `render.yaml`.
- Preencha as variáveis de ambiente solicitadas (`DATABASE_URL`, `MASTER_ENCRYPTION_KEY`).
- Clique em **"Apply"**.

### Opção B: Deploy Manual (Web Service)
- Clique em **"New +"** > **"Web Service"**.
- Conecte o repositório do GitHub.
- Configurações:
  - **Name**: `steam-guard-backend`
  - **Language**: `Docker`
  - **Dockerfile Path**: `./backend/Dockerfile`
  - **Docker Context**: `./backend`
  - **Instance Type**: `Free`
  - **Health Check Path**: `/health`
- Em **Environment Variables**, adicione:
  - `APP_ENV`: `production`
  - `DATABASE_URL`: `postgresql://postgres.[REF]:[SENHA]@...:6543/postgres?sslmode=require`
  - `JWT_SECRET`: *(chave gerada no passo 3)*
  - `MASTER_ENCRYPTION_KEY`: *(chave Fernet gerada no passo 3)*
  - `CORS_ORIGINS`: `https://seu-projeto.vercel.app` *(atualizaremos após criar a Vercel)*
  - `FRONTEND_URL`: `https://seu-projeto.vercel.app`
  - `IMAP_TIMEOUT`: `5`
  - `CODE_POLL_INTERVAL`: `2`
  - `CODE_POLL_TIMEOUT`: `15`
  - `RATE_LIMIT`: `60/minute`
  - `TOKEN_DEFAULT_EXPIRATION`: `3600`
- Clique em **"Deploy Web Service"**.

> O `entrypoint.sh` do container executa automaticamente `alembic upgrade head` na inicialização, aplicando as migrations e criando todas as tabelas no Supabase antes de abrir as portas da API.

---

## Passo 5: Deploy do Frontend na Vercel

1. Acesse [vercel.com](https://vercel.com) e conecte sua conta do GitHub.
2. Clique em **"Add New..."** > **"Project"**.
3. Importe o repositório `regaste-codigo-steam`.
4. Configurações de Build:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Clique em *Edit* e selecione a pasta `frontend`.
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Em **Environment Variables**:
   - Adicione `VITE_API_URL`: Insira a URL fornecida pelo Render (ex: `https://steam-guard-backend.onrender.com`).
6. Clique em **"Deploy"**.

---

## Passo 6: Conexão Cruzada (CORS e URLs)

Após a Vercel gerar o domínio do frontend (ex: `https://steam-guard-resgate.vercel.app`):

1. Acesse o dashboard do **Render** no serviço `steam-guard-backend`.
2. Vá em **Environment**:
   - Atualize `CORS_ORIGINS` para: `https://steam-guard-resgate.vercel.app`
   - Atualize `FRONTEND_URL` para: `https://steam-guard-resgate.vercel.app`
3. Salve as alterações. O Render fará o redeploy em segundos.

---

## Passo 7: Verificação e Teste de Ponta a Ponta

### 1. Testar Health Check da API
Abra no navegador ou via curl:
```bash
curl https://steam-guard-backend.onrender.com/health
# Resposta esperada: {"status":"ok","app_env":"production"}

curl https://steam-guard-backend.onrender.com/health/ready
# Resposta esperada: {"status":"ready","database":"connected","redis":"disabled (in-memory fallback)"}
```

### 2. Cadastrar Revendedor e Configurar IMAP
1. Acesse o frontend na Vercel: `https://seu-app.vercel.app/login`
2. Clique em *"Cadastre-se como revendedor"*.
3. Insira seu e-mail e crie uma senha forte.
4. No Dashboard, vá na aba **Servidor IMAP**:
   - Host: `imap.gmail.com`
   - Porta: `993`
   - Usuário: `seu-email@gmail.com`
   - Senha: Use uma **Senha de Aplicativo (App Password)** de 16 letras gerada na Conta Google (Segurança > Verificação em duas etapas > Senhas de app).
   - Clique em **"Testar Conexão IMAP"** -> Verifique o status verde de sucesso.
   - Clique em **"Salvar Credenciais Criptografadas"**.

### 3. Cadastrar Conta e Gerar Link de Resgate
1. Vá na aba **Contas Steam** e cadastre o login da conta (ex: `vendedor_vip_01`).
2. Vá na aba **Gerador de Resgates**:
   - Selecione a conta.
   - Escolha o tempo de expiração.
   - Clique em **"Gerar Link para o Cliente"**.
3. Copie o link gerado: `https://seu-app.vercel.app/resgate/TOKEN_SECRETO`.
4. Abra o link em uma aba anônima (como se fosse o comprador):
   - A página exibirá o login da conta Steam.
   - Inicie o login na Steam com a conta.
   - Quando a Steam enviar o código de acesso, clique em **"Obter Código Steam Guard"**.
   - O backend se conectará via IMAP, capturará o código em tempo real e exibirá o código de 5 dígitos na tela com o contador de 60 segundos!

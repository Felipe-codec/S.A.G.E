# Steam Guard Resgate — Infraestrutura Cloud & Deploy

Plataforma de alta disponibilidade para revendedores de contas Steam gerarem links temporários e permitirem aos compradores resgatarem códigos **Steam Guard** (5 dígitos) de forma instantânea e autônoma via IMAP seguro.

Projetada com arquitetura cloud escalável para operar com **custo inicial de R$ 0/mês** (Vercel + Render + Supabase) e capacidade de expansão contínua para VPS ou nuvens dedicadas sem necessidade de refatoração.

---

## Principais Recursos

- 🚀 **Backend Moderno**: FastAPI (Python 3.12+) com tipagem estrita, Pydantic Settings, SQLAlchemy 2.0 e Uvicorn em container Docker otimizado.
- 🎨 **Frontend Steam Dark**: React 18 + TypeScript + Vite com estética Valve/Steam, glassmorphism, responsividade e contagem regressiva em tempo real.
- 🗄️ **Banco Relacional**: PostgreSQL gerenciado (compatível com Supabase e instâncias locais), controlado via migrações estritas com **Alembic**.
- ✉️ **Conexão IMAP Resiliente**: Leitura sob TLS (porta 993) com timeouts seguros, context managers e regex especializada para códigos Steam Guard.
- 🔐 **Segurança e Criptografia**: Senhas de e-mail IMAP criptografadas em repouso com **Fernet (AES-128-CBC + HMAC-SHA256)**; suporte a rotação de chaves.
- 🛡️ **Sanitização de Logs**: Filtros automáticos que impedem o vazamento de senhas, tokens, JWTs e códigos Steam Guard em logs stdout/stderr.
- ⚡ **Abstração de Cache e Rate Limit**: Funciona de imediato com rate limiting em memória RAM e chaveia automaticamente para **Redis** quando `REDIS_URL` for informada.
- ☁️ **Zero Vendor Lock-in**: Código baseado em padrões abertos, pronto para migração para AWS, GCP, Azure ou VPS própria.

---

## Arquitetura Cloud

```
GitHub (Repositório Central)
 │
 ├── Frontend React/TypeScript  ──►  Vercel Edge Network
 │
 └── Backend FastAPI + Docker   ──►  Render Web Service
      │
      ├── PostgreSQL Gerenciado ──►  Supabase (Porta 6543 IPv4 Pooler)
      │
      ├── IMAPS Porta 993 (TLS) ──►  Servidor de E-mail do Revendedor
      │
      └── Redis (Opcional)      ──►  Upstash / Redis Dedicado
```

---

## Estrutura do Projeto

```
regaste-codigo-steam/
├── backend/                  # API FastAPI, Dockerfile e Testes
│   ├── app/
│   │   ├── api/              # Rotas, Middlewares e Injeção de Dependências
│   │   ├── core/             # Configurações, Criptografia Fernet, JWT e Logs
│   │   ├── db/               # Engine SQLAlchemy e Sessão
│   │   ├── models/           # Modelos com índices otimizados
│   │   ├── schemas/          # Schemas Pydantic v2
│   │   └── services/         # IMAP, Cache, Lock e Rate Limiting
│   ├── migrations/           # Migrações do Alembic (001_initial_schema)
│   ├── tests/                # Suíte de testes automatizados com pytest
│   ├── Dockerfile            # Container de produção Python 3.12 (non-root)
│   ├── entrypoint.sh         # Executa 'alembic upgrade head' e inicia uvicorn
│   └── requirements.txt      # Dependências de produção
│
├── frontend/                 # Aplicação React 18 + TypeScript + Vite
│   ├── src/
│   │   ├── components/       # Navbar, Temporizador de Código, etc.
│   │   ├── pages/            # Resgate, Login, Dashboard, NotFound
│   │   ├── services/         # Cliente HTTP da API (VITE_API_URL)
│   │   └── index.css         # Design system Steam Dark em Vanilla CSS
│   ├── Dockerfile            # Multi-stage com Node e Nginx Alpine
│   ├── vercel.json           # Roteamento SPA na Vercel
│   └── package.json
│
├── docs/                     # Documentação Técnica Completa
│   ├── ARCHITECTURE.md       # Fluxos detalhados e caminhos de migração
│   ├── DATABASE.md           # ERD, dicionário de dados e Supabase pooling
│   ├── DEPLOY.md             # Tutorial passo a passo para Vercel, Render e Supabase
│   ├── ENVIRONMENT.md        # Dicionário de variáveis de ambiente
│   ├── SECURITY.md           # Modelo criptográfico e proteção de segredos
│   └── TROUBLESHOOTING.md    # Resolução de problemas frequentes
│
├── docker-compose.yml        # Orquestração local (Backend, Frontend, Postgres, Redis)
├── render.yaml               # Blueprint de deploy automatizado no Render
├── .env.example              # Exemplo documentado de variáveis de ambiente
├── .gitignore                # Regras rigorosas de proteção de segredos
└── README.md
```

---

## Como Executar Localmente

### Opção 1: Via Docker Compose (Recomendado)
Para subir o ambiente completo com PostgreSQL, Backend e Frontend:
```bash
docker compose up --build
```
> Para incluir o Redis no ambiente local:
> ```bash
> docker compose --profile redis up --build
> ```

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Documentação Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### Opção 2: Sem Docker (Desenvolvimento Nativo)

#### 1. Configurar o Backend
```bash
# Crie e ative o ambiente virtual
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate

# Instale as dependências
pip install -r backend/requirements.txt -r backend/requirements-dev.txt

# Copie o arquivo de variáveis de ambiente
cp .env.example .env

# Execute as migrações do banco
cd backend
alembic upgrade head

# Inicie o servidor de desenvolvimento
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Configurar o Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Executando os Testes Automatizados

### Testes do Backend (Pytest)
A suíte verifica criptografia Fernet, rotação de chaves, integridade de rate limit, sanitização de logs, health checks e tratamento de erros do serviço IMAP:
```bash
.venv\Scripts\pytest backend/tests -v
```

### Validação de Build do Frontend
```bash
cd frontend
npm run build
```

---

## Deploy em Produção (Custo R$ 0)

Consulte o passo a passo completo e detalhado no documento:
👉 **[Guia Completo de Deploy (docs/DEPLOY.md)](docs/DEPLOY.md)**

1. **Banco de Dados**: Crie o PostgreSQL gratuito no [Supabase](https://supabase.com) e obtenha a connection string Transaction Pooler (Porta 6543).
2. **Backend**: Conecte o repositório no [Render](https://render.com) utilizando o blueprint `render.yaml` ou Web Service Docker.
3. **Frontend**: Conecte a pasta `frontend` na [Vercel](https://vercel.com) e configure a variável `VITE_API_URL` apontando para o Render.
4. **CORS**: Configure `CORS_ORIGINS` no Render com a URL gerada pela Vercel.

---

## Documentação Técnica
- [Arquitetura e Fluxos do Sistema](docs/ARCHITECTURE.md)
- [Banco de Dados e Índices](docs/DATABASE.md)
- [Guia de Deploy Passo a Passo](docs/DEPLOY.md)
- [Dicionário de Variáveis de Ambiente](docs/ENVIRONMENT.md)
- [Diretrizes de Segurança e Criptografia](docs/SECURITY.md)
- [Diagnósticos e Resolução de Problemas](docs/TROUBLESHOOTING.md)

---

## Licença e Isenção de Responsabilidade
Este projeto foi desenvolvido com finalidade de intermediação de acesso autônomo para revendedores. **Steam** e o logotipo **Steam** são marcas registradas da **Valve Corporation**. Este projeto não possui afiliação, vínculo ou endosso oficial por parte da Valve Corporation.

# Guia de Resolução de Problemas (Troubleshooting)

Este guia reúne diagnósticos e soluções para os cenários de erro mais comuns em desenvolvimento local e ambientes de produção no Render, Supabase e Vercel.

---

## 1. O Backend demora para responder na primeira requisição (Render Sleep)

### Causa:
No plano Free do Render, os Web Services entram em modo "sleep" (hibernação) após 15 minutos sem receber requisições HTTP. Quando uma nova requisição chega, o container leva entre 30 a 50 segundos para inicializar.

### Solução:
- O frontend possui estados de carregamento claros com indicadores visuais para o usuário aguardar a inicialização.
- Para manter o container sempre acordado sem custo, utilize um serviço de monitoramento gratuito (como [UptimeRobot](https://uptimerobot.com) ou [Better Uptime]) disparando um ping a cada 10 minutos no endpoint:
  ```
  GET https://seu-backend.onrender.com/health
  ```

---

## 2. Erro de Conexão com o Supabase (`SSL connection has been closed unexpectedly` ou IPv6)

### Causa:
Alguns ambientes de hospedagem (como nós compartilhados do Render) não possuem suporte completo a rotas IPv6 diretas para o PostgreSQL do Supabase, ou o Supabase encerrou conexões ociosas.

### Solução:
1. Certifique-se de que a `DATABASE_URL` utiliza a porta **6543** (Transaction Pooler com suporte a IPv4):
   ```
   postgresql://postgres.[REF]:[SENHA]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
   ```
2. O engine SQLAlchemy do projeto já vem configurado com `pool_pre_ping=True` e `pool_recycle=300`, prevenindo erros de conexões derrubadas.

---

## 3. Erro de CORS no Navegador (`Blocked by CORS policy`)

### Causa:
O domínio da Vercel que originou a chamada não está cadastrado na lista permitida do backend.

### Solução:
1. Verifique qual a URL exata do seu frontend (ex: `https://steam-guard-resgate.vercel.app`).
2. Acesse o painel do **Render** > seu serviço > **Environment**.
3. Certifique-se de que a variável `CORS_ORIGINS` contém exatamente essa URL sem barra no final:
   ```
   CORS_ORIGINS=https://steam-guard-resgate.vercel.app
   ```
4. Salve para aplicar o reinício automático do backend.

---

## 4. Falha de Autenticação IMAP (`IMAPAuthenticationError`)

### Causa:
Provedores como Gmail, Outlook e Yahoo exigem Senhas de Aplicativo específicas em contas com autenticação em duas etapas (2FA) ativada.

### Solução para o Gmail:
1. Acesse sua Conta Google > **Segurança**.
2. Ative a **Verificação em duas etapas** (se ainda não estiver ativada).
3. Pesquise por **"Senhas de app"** (App passwords).
4. Crie uma nova senha de aplicativo (ex: nomeie como "Steam Guard Resgate").
5. O Google gerará um código de 16 letras (ex: `abcd efgh ijkl mnop`).
6. Copie esse código sem espaços e cadastre na aba **Servidor IMAP** do painel do revendedor.

---

## 5. Código Steam Guard Não Encontrado (`Timeout / Não Detectado`)

### Causa:
A Valve pode demorar alguns segundos para disparar o e-mail de verificação após a tentativa de login na Steam, ou o e-mail caiu na pasta de Spam/Lixeira.

### Solução:
1. Garanta que o comprador realmente clicou em "Iniciar Sessão" na Steam e a tela do Steam Guard está aberta aguardando o código.
2. Certifique-se de que a conta Steam configurada no painel recebe as mensagens na mesma caixa de entrada IMAP cadastrada.
3. Se necessário, clique novamente no botão **"Obter Código Steam Guard"** para disparar uma nova rodada de busca.

---

## 6. Erro ao Executar Migrações do Alembic

### Causa:
A URL do banco de dados informada está inacessível ou o esquema está em conflito.

### Solução:
Para inspecionar o status das migrações manualmente via terminal:
```bash
# Ative o ambiente virtual
.venv\Scripts\activate

# Verifique o histórico de revisões
alembic history

# Force a atualização para o topo
alembic upgrade head
```

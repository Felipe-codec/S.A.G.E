#!/usr/bin/env bash
set -e

echo "[STARTUP] Iniciando Steam Guard Resgate Backend..."
echo "[STARTUP] Ambiente: ${APP_ENV:-production}"
echo "[STARTUP] Porta configurada: ${PORT:-8000}"

# Validação estrita para ambiente de produção
if [ "$APP_ENV" = "production" ]; then
    if [ -z "$DATABASE_URL" ]; then
        echo "================================================================================"
        echo "[CONFIG ERROR] A variável DATABASE_URL não está configurada no Render!"
        echo "Para que o backend funcione, você deve configurar a variável DATABASE_URL com a"
        echo "connection string do Supabase no painel do Render (Environment Variables)."
        echo "Exemplo: postgresql://postgres.[REF]:[SENHA]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require"
        echo "================================================================================"
        exit 1
    elif [[ "$DATABASE_URL" == *"localhost"* ]] || [[ "$DATABASE_URL" == *"127.0.0.1"* ]]; then
        echo "================================================================================"
        echo "[CONFIG ERROR] DATABASE_URL aponta para localhost em ambiente de produção!"
        echo "O container no Render não possui PostgreSQL local. Configure a DATABASE_URL do"
        echo "Supabase no painel do Render (Environment Variables)."
        echo "Exemplo: postgresql://postgres.[REF]:[SENHA]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require"
        echo "================================================================================"
        exit 1
    fi
fi

# Executa as migrações do banco de dados antes de iniciar o servidor
if [ -n "$DATABASE_URL" ]; then
    echo "[MIGRATIONS] Executando alembic upgrade head..."
    alembic upgrade head || {
        echo "================================================================================"
        echo "[MIGRATIONS ERROR] Falha ao executar migrações do Alembic."
        echo "Verifique se o banco no Supabase está ativo e se a DATABASE_URL está correta."
        echo "================================================================================"
        exit 1
    }
    echo "[MIGRATIONS] Migrações concluídas com sucesso."
else
    echo "[WARNING] DATABASE_URL não definida! Pulando migrações."
fi

# Inicia o servidor Uvicorn escutando em 0.0.0.0:$PORT
echo "[SERVER] Iniciando Uvicorn em 0.0.0.0:${PORT:-8000}..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-1}" \
    --proxy-headers \
    --forwarded-allow-ips "*"

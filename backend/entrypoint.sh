#!/usr/bin/env bash
set -e

echo "[STARTUP] Iniciando Steam Guard Resgate Backend..."
echo "[STARTUP] Ambiente: ${APP_ENV:-production}"
echo "[STARTUP] Porta configurada: ${PORT:-8000}"

# Executa as migrações do banco de dados antes de iniciar o servidor
if [ -n "$DATABASE_URL" ]; then
    echo "[MIGRATIONS] Executando alembic upgrade head..."
    alembic upgrade head || {
        echo "[MIGRATIONS ERROR] Falha ao executar migrações do Alembic. Verifique a conexão com o PostgreSQL."
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

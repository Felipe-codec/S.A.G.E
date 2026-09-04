FROM python:3.12-slim

# Metadados da imagem
LABEL maintainer="Steam Guard Resgate Team"
LABEL description="Backend FastAPI para o sistema Steam Guard Resgate"

# Previne geração de bytecode .pyc e força stdout/stderr sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_ENV=production

# Instala curl para o HEALTHCHECK e dependências mínimas do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root para execução segura do container
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m -s /bin/bash appuser

WORKDIR /app

# Instala dependências Python com cache isolado
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação e scripts
COPY . .

# Garante permissões de execução para o entrypoint e usuário appuser
RUN chmod +x /app/entrypoint.sh && \
    chown -R appuser:appuser /app

# Chaveia para usuário não-root
USER appuser

# Healthcheck do container
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f "http://127.0.0.1:${PORT}/health" || exit 1

# Expõe a porta dinâmica
EXPOSE 8000

# Executa o entrypoint que roda migrations e inicia o uvicorn
ENTRYPOINT ["/app/entrypoint.sh"]

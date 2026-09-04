from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.middlewares.logging_middleware import StructuredLoggingMiddleware
from app.api.middlewares.security_middleware import SecurityHeadersMiddleware
from app.api.routes import (
    auth_router,
    health_router,
    imap_router,
    redemption_router,
    steam_router,
    tokens_router,
)
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.db.session import check_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação FastAPI."""
    setup_logging()
    logger.info(f"[LIFESPAN] Iniciando Steam Guard Resgate em modo: {settings.APP_ENV}")
    logger.info(f"[LIFESPAN] Origens CORS permitidas: {settings.CORS_ORIGINS}")

    # Checagem não-bloqueante de conectividade na inicialização
    db_connected = check_db_connection()
    if db_connected:
        logger.info("[LIFESPAN] Conexão com o banco de dados PostgreSQL validada com sucesso.")
    else:
        logger.warning(
            "[LIFESPAN] Falha inicial ao conectar ao PostgreSQL. Verifique DATABASE_URL e o status do Supabase/banco."
        )

    yield

    logger.info("[LIFESPAN] Encerrando aplicação e liberando recursos...")


def create_application() -> FastAPI:
    """Fábrica da aplicação FastAPI com middlewares e rotas configuradas."""
    app = FastAPI(
        title="Steam Guard Resgate API",
        description="Infraestrutura cloud para resgate seguro de códigos Steam Guard via IMAP",
        version="1.0.0",
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if settings.APP_ENV != "production" else None,
        lifespan=lifespan,
    )

    # 1. Middlewares customizados
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(StructuredLoggingMiddleware)

    # 2. Configuração de CORS para comunicação segura com Vercel
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # 3. Registro dos roteadores da API
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(imap_router)
    app.include_router(steam_router)
    app.include_router(tokens_router)
    app.include_router(redemption_router)

    return app


app = create_application()

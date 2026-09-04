from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.session import check_db_connection

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check simples para verificar se o processo FastAPI está ativo.
    Utilizado por Docker HEALTHCHECK, Render e orquestradores de container.
    """
    return {
        "status": "ok",
        "app_env": settings.APP_ENV,
    }


@router.get("/health/ready")
def readiness_check():
    """
    Readiness check para verificar dependências essenciais (PostgreSQL).
    NUNCA executa consultas IMAP.
    Retorna 200 OK se todas as dependências críticas estiverem operacionais, ou 503 se houver falha.
    """
    db_ok = check_db_connection()
    if not db_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "database": "disconnected",
                "message": "Falha na conexão com o banco de dados PostgreSQL.",
            },
        )

    return {
        "status": "ready",
        "database": "connected",
        "redis": "connected" if settings.REDIS_URL else "disabled (in-memory fallback)",
    }

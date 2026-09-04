from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Aplica cabeçalhos padrão de segurança recomendados pela OWASP."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Previne MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Previne clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Proteção contra XSS legado
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Referrer Policy seguro
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS (Strict-Transport-Security) em produção
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response

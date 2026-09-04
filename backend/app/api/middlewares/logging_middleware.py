import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import logger
from app.core.security import mask_ip_address


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Extrai ou gera o identificador X-Request-ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        masked_ip = mask_ip_address(client_ip)

        try:
            response = await call_next(request)
            duration_ms = int((time.time() - start_time) * 1000)

            # Injeta X-Request-ID no header da resposta HTTP
            response.headers["X-Request-ID"] = request_id

            # Registra log estruturado via logger
            extra_data = {
                "request_id": request_id,
                "endpoint": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": masked_ip,
            }
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
                extra=extra_data,
            )
            return response

        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            extra_data = {
                "request_id": request_id,
                "endpoint": request.url.path,
                "method": request.method,
                "status_code": 500,
                "duration_ms": duration_ms,
                "client_ip": masked_ip,
            }
            logger.error(
                f"Exceção não tratada em {request.method} {request.url.path}: {str(exc)}",
                extra=extra_data,
                exc_info=True,
            )
            raise exc

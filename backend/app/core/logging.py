import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict


# Padrões regex para detecção e sanitização automática de segredos em logs
SENSITIVE_PATTERNS = [
    (re.compile(r'(?i)("?password"?\s*[:=]\s*["\'])([^"\']+)(["\'])'), r'\1[REDACTED]\3'),
    (re.compile(r'(?i)("?secret"?\s*[:=]\s*["\'])([^"\']+)(["\'])'), r'\1[REDACTED]\3'),
    (re.compile(r'(?i)("?token"?\s*[:=]\s*["\'])([a-zA-Z0-9_\-\.]{15,})(["\'])'), r'\1[REDACTED_TOKEN]\3'),
    (re.compile(r'(?i)(bearer\s+)([a-zA-Z0-9_\-\.]+)'), r'\1[REDACTED_JWT]'),
    (re.compile(r'(?i)(postgres(?:ql)?://)([^:]+):([^@]+)@'), r'\1\2:***@'),
    (re.compile(r'(?i)(c[oó]digo\s+steam\s*(?:guard)?\s*[:=]?\s*)([a-zA-Z0-9]{5})'), r'\1***\2'),
]


def sanitize_log_message(message: str) -> str:
    """Aplica filtros de regex para mascarar dados sensíveis em mensagens de texto."""
    if not isinstance(message, str):
        message = str(message)
    for pattern, replacement in SENSITIVE_PATTERNS:
        message = pattern.sub(replacement, message)
    return message


class StructuredJsonFormatter(logging.Formatter):
    """
    Formatador JSON estruturado para logs de produção.
    Garante sanitização de dados sensíveis e conformidade com agregadores de log.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": sanitize_log_message(record.getMessage()),
        }

        # Extrai metadados adicionais se fornecidos no LogRecord
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "endpoint"):
            log_obj["endpoint"] = record.endpoint
        if hasattr(record, "method"):
            log_obj["method"] = record.method
        if hasattr(record, "status_code"):
            log_obj["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if hasattr(record, "client_ip"):
            log_obj["client_ip"] = record.client_ip

        if record.exc_info:
            log_obj["exception"] = sanitize_log_message(self.formatException(record.exc_info))

        return json.dumps(log_obj, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configura o logger raiz da aplicação direcionando JSON estruturado para stdout."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove handlers antigos para evitar duplicação
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(StructuredJsonFormatter())
    root_logger.addHandler(stream_handler)

    # Suprime logs excessivamente verbosos de bibliotecas de terceiros
    logging.getLogger("uvicorn.access").handlers = [stream_handler]
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger = logging.getLogger("steam_guard_app")
    logger.info("Sistema de logs estruturados e sanitizados inicializado com sucesso.")
    return logger


logger = logging.getLogger("steam_guard_app")

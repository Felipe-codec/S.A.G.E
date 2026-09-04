import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    """Gera hash seguro de senha utilizando bcrypt com salt dinâmico."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha em texto plano coincide com o hash bcrypt."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Gera um JWT assinado com expiração configurada."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {"sub": str(subject), "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica e valida o JWT, retornando os claims ou None se inválido/expirado."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except (jwt.PyJWTError, Exception):
        return None


def hash_token(raw_token: str) -> str:
    """Calcula o hash SHA-256 de um token de resgate para busca rápida e segura no banco."""
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()


def mask_steam_code(code: str) -> str:
    """Mascara o código Steam Guard de 5 caracteres para logs e auditoria (ex: '***7G')."""
    if not code:
        return ""
    code = code.strip()
    if len(code) <= 2:
        return "***"
    return f"***{code[-2:]}"


def mask_token_string(token: str) -> str:
    """Mascara um token ou hash para exibição segura em logs (ex: 'a1b2...9z8y')."""
    if not token or len(token) < 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


def mask_ip_address(ip: Optional[str]) -> str:
    """Mascara o endereço IP do cliente para conformidade com privacidade (LGPD/GDPR)."""
    if not ip:
        return "unknown"
    ip = ip.strip()
    # IPv4
    if "." in ip:
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.***.***"
    # IPv6
    if ":" in ip:
        parts = ip.split(":")
        if len(parts) >= 2:
            return f"{parts[0]}:{parts[1]}:****:****"
    return "masked_ip"

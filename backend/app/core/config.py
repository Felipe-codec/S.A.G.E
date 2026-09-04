from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import sys


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # 1. Ambiente e Servidor
    APP_ENV: str = Field(default="development", description="development, production, test")
    PORT: int = Field(default=8000, description="Porta TCP do servidor")

    # 2. Banco de Dados
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/steam_guard_db",
        description="URL de conexão PostgreSQL",
    )

    # 3. Segurança e Criptografia
    JWT_SECRET: str = Field(
        default="dev-jwt-secret-key-replace-in-production-min-32-chars-long",
        description="Chave secreta para assinatura de JWT",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    MASTER_ENCRYPTION_KEY: str = Field(
        default="VZaokCbhHYZg5M6sslHozPjTZijU5bGgm74kVXE7JB8=",
        description="Chave Fernet de 32 bytes URL-safe base64 para criptografar senhas IMAP",
    )
    TOKEN_DEFAULT_EXPIRATION: int = Field(
        default=3600, description="Expiração padrão do token de resgate em segundos (1h)"
    )

    # 4. CORS e Frontend
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        description="Lista de origens permitidas para CORS",
    )
    FRONTEND_URL: str = Field(
        default="http://localhost:5173", description="URL pública base do frontend"
    )

    # 5. IMAP
    IMAP_TIMEOUT: int = Field(default=5, description="Timeout de conexão IMAP em segundos")
    CODE_POLL_INTERVAL: int = Field(
        default=2, description="Intervalo entre buscas de código em segundos"
    )
    CODE_POLL_TIMEOUT: int = Field(
        default=15, description="Timeout total de busca de código em segundos"
    )

    # 6. Rate Limiting
    RATE_LIMIT: str = Field(default="60/minute", description="Taxa de requisições padrão")
    REDEMPTION_RATE_LIMIT: str = Field(
        default="5/minute", description="Limite de requisições de código por sessão/IP"
    )

    # 7. Redis (Opcional)
    REDIS_URL: Optional[str] = Field(default=None, description="URL de conexão Redis")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql://", 1)
            # Codifica caracteres especiais como '@' na senha para evitar quebra no parser de host
            import re, urllib.parse
            match = re.match(r'^(postgresql(?:\+[a-z0-9]+)?://)([^:]+):(.*)@([^/@:]+(?::\d+)?(?:/.*)?)$', v)
            if match:
                scheme, user, raw_pwd, rest = match.groups()
                decoded_pwd = urllib.parse.unquote(raw_pwd)
                quoted_pwd = urllib.parse.quote(decoded_pwd, safe="")
                v = f"{scheme}{user}:{quoted_pwd}@{rest}"
        return v

    @field_validator("FRONTEND_URL", mode="after")
    @classmethod
    def clean_frontend_url(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().rstrip("/")
        return v

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        raw_list: List[str] = []
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    raw_list = [str(item).strip() for item in json.loads(v)]
                except Exception:
                    raw_list = [orig.strip() for orig in v.split(",") if orig.strip()]
            else:
                raw_list = [orig.strip() for orig in v.split(",") if orig.strip()]
        elif isinstance(v, list):
            raw_list = [str(item).strip() for item in v if str(item).strip()]
        else:
            return ["http://localhost:5173"]

        origins_set = set()
        for item in raw_list:
            clean = item.strip().strip("'\"").rstrip("/")
            if clean:
                origins_set.add(clean)
                origins_set.add(clean + "/")
        return list(origins_set) if origins_set else ["http://localhost:5173"]

    def validate_production_security(self) -> None:
        """Valida que configurações inseguras não sejam utilizadas em ambiente de produção."""
        if self.APP_ENV == "production":
            errors = []
            if len(self.JWT_SECRET) < 32 or "dev" in self.JWT_SECRET.lower():
                errors.append("JWT_SECRET é muito fraco ou padrão de dev para ambiente de produção.")

            if "sample" in self.MASTER_ENCRYPTION_KEY.lower():
                errors.append("MASTER_ENCRYPTION_KEY é a chave de exemplo pública. Gere uma nova chave Fernet.")

            if "*" in self.CORS_ORIGINS:
                errors.append("CORS_ORIGINS não pode conter '*' em produção (risco de segurança com cookies).")

            if "localhost" in self.DATABASE_URL or "127.0.0.1" in self.DATABASE_URL:
                errors.append("DATABASE_URL não pode apontar para localhost em produção.")

            if errors:
                raise ValueError(
                    f"ERRO DE SEGURANÇA EM PRODUÇÃO:\n" + "\n".join(f"- {err}" for err in errors)
                )


settings = Settings()
try:
    settings.validate_production_security()
except ValueError as e:
    # Se estiver rodando pytest ou em ambiente de desenvolvimento, apenas loga warning se não for produção
    if settings.APP_ENV == "production":
        raise
    else:
        sys.stderr.write(f"[CONFIG WARNING] {e}\n")

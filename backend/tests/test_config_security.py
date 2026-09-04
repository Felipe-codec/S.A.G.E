import pytest
from pydantic import ValidationError
from app.core.config import Settings


def test_production_environment_rejects_weak_secrets():
    """Garante que a aplicação recuse iniciar em produção com credenciais inseguras."""
    # 1. JWT fraco
    settings_insecure = Settings(
        APP_ENV="production",
        JWT_SECRET="dev-weak-key",
        MASTER_ENCRYPTION_KEY="dGhpcy1pcy1hLXNhbXBsZS1mZXJuZXQta2V5LTEyMzQ1Njc4OTA=",
        DATABASE_URL="postgresql://user:pass@remote-host:5432/db",
        CORS_ORIGINS=["https://meu-app.vercel.app"],
    )
    with pytest.raises(ValueError) as exc:
        settings_insecure.validate_production_security()
    assert "JWT_SECRET" in str(exc.value)


def test_production_environment_rejects_wildcard_cors():
    """Garante que CORS_ORIGINS não permita '*' em produção."""
    settings_cors_wildcard = Settings(
        APP_ENV="production",
        JWT_SECRET="super-strong-production-jwt-key-with-over-32-chars-long",
        MASTER_ENCRYPTION_KEY="VZaokCbhHYZg5M6sslHozPjTZijU5bGgm74kVXE7JB8=",
        DATABASE_URL="postgresql://user:pass@remote-host:5432/db",
        CORS_ORIGINS=["*"],
    )
    with pytest.raises(ValueError) as exc:
        settings_cors_wildcard.validate_production_security()
    assert "CORS_ORIGINS" in str(exc.value)


def test_production_environment_rejects_localhost_db():
    """Garante que DATABASE_URL não aponte para localhost em produção."""
    settings_local_db = Settings(
        APP_ENV="production",
        JWT_SECRET="super-strong-production-jwt-key-with-over-32-chars-long",
        MASTER_ENCRYPTION_KEY="VZaokCbhHYZg5M6sslHozPjTZijU5bGgm74kVXE7JB8=",
        DATABASE_URL="postgresql://user:pass@localhost:5432/db",
        CORS_ORIGINS=["https://meu-app.vercel.app"],
    )
    with pytest.raises(ValueError) as exc:
        settings_local_db.validate_production_security()
    assert "DATABASE_URL" in str(exc.value)

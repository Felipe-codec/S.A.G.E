from app.core.logging import sanitize_log_message
from app.core.security import mask_ip_address, mask_steam_code, mask_token_string


def test_sanitize_passwords_and_tokens():
    """Garante que segredos e senhas não sejam impressos nos logs."""
    raw_log = 'Tentativa de login com password: "SuperSecretPassword123" e token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"'
    sanitized = sanitize_log_message(raw_log)

    assert "SuperSecretPassword123" not in sanitized
    assert "[REDACTED]" in sanitized


def test_sanitize_bearer_jwt():
    """Garante que JWTs em headers de autorização sejam mascarados."""
    raw_log = "Header recebido: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature"
    sanitized = sanitize_log_message(raw_log)

    assert "Bearer [REDACTED_JWT]" in sanitized
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in sanitized


def test_mask_steam_code():
    """Garante que códigos Steam Guard nunca sejam expostos por completo."""
    assert mask_steam_code("C78N4") == "***N4"
    assert mask_steam_code("99M2K") == "***2K"
    assert mask_steam_code("") == ""


def test_mask_ip_address():
    """Valida anonimização de IPs de acordo com princípios de privacidade."""
    assert mask_ip_address("187.54.120.45") == "187.54.***.***"
    assert mask_ip_address("2804:14d:5c82:8390:1::1") == "2804:14d:****:****"


def test_mask_token_string():
    """Valida mascaramento de tokens de resgate."""
    raw_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    masked = mask_token_string(raw_hash)
    assert masked.startswith("e3b0...")
    assert masked.endswith("b855")

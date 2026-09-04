import time
from app.services.cache_service import MemoryCacheService
from app.services.rate_limit_service import MemoryRateLimitService


def test_memory_rate_limiter():
    limiter = MemoryRateLimitService()
    key = "user_test_ip_123"

    # Permite 3 requisições
    is_limited, _ = limiter.check_rate_limit(key, max_requests=3, window_seconds=2)
    assert is_limited is False

    is_limited, _ = limiter.check_rate_limit(key, max_requests=3, window_seconds=2)
    assert is_limited is False

    is_limited, _ = limiter.check_rate_limit(key, max_requests=3, window_seconds=2)
    assert is_limited is False

    # 4ª requisição excede o limite
    is_limited, retry_after = limiter.check_rate_limit(key, max_requests=3, window_seconds=2)
    assert is_limited is True
    assert retry_after > 0


def test_memory_cache_service():
    cache = MemoryCacheService()

    # Teste de escrita e leitura
    cache.set("chave_teste", "valor123", ttl_seconds=2)
    assert cache.get("chave_teste") == "valor123"
    assert cache.exists("chave_teste") is True

    # Teste de delete
    cache.delete("chave_teste")
    assert cache.get("chave_teste") is None
    assert cache.exists("chave_teste") is False

    # Teste de expiração TTL
    cache.set("chave_expira", "temp_val", ttl_seconds=1)
    time.sleep(1.1)
    assert cache.get("chave_expira") is None

from abc import ABC, abstractmethod
import time
from typing import Dict, List, Optional, Tuple
from app.core.config import settings
from app.core.logging import logger


class AbstractRateLimitService(ABC):
    @abstractmethod
    def check_rate_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> Tuple[bool, int]:
        """
        Verifica se a chave excedeu o limite.
        Retorna (is_limited, retry_after_seconds).
        """
        pass


class MemoryRateLimitService(AbstractRateLimitService):
    """Implementação em memória com algoritmo Sliding Window para rate limiting local."""

    def __init__(self):
        # key -> lista de timestamps das requisições
        self._history: Dict[str, List[float]] = {}

    def check_rate_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - window_seconds

        if key not in self._history:
            self._history[key] = [now]
            return False, 0

        # Filtra requisições fora da janela atual
        valid_requests = [t for t in self._history[key] if t > window_start]
        self._history[key] = valid_requests

        if len(valid_requests) >= max_requests:
            oldest_request = valid_requests[0]
            retry_after = int(max(1, (oldest_request + window_seconds) - now))
            return True, retry_after

        self._history[key].append(now)
        return False, 0


class RedisRateLimitService(AbstractRateLimitService):
    """Implementação distribuída com Sliding Window utilizando Redis Sorted Sets (ZSET)."""

    def __init__(self, redis_url: str):
        import redis
        self._client = redis.from_url(redis_url, decode_responses=True)

    def check_rate_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> Tuple[bool, int]:
        try:
            now = time.time()
            window_start = now - window_seconds
            zset_key = f"rate_limit:{key}"

            pipe = self._client.pipeline()
            # Remove eventos antigos
            pipe.zremrangebyscore(zset_key, 0, window_start)
            # Conta requisições na janela atual
            pipe.zcard(zset_key)
            # Adiciona a requisição atual
            pipe.zadd(zset_key, {str(now): now})
            # Define expiração para limpeza automática da chave
            pipe.expire(zset_key, window_seconds + 1)
            results = pipe.execute()

            current_count = results[1]
            if current_count >= max_requests:
                return True, window_seconds

            return False, 0
        except Exception as e:
            logger.error(f"Erro ao verificar rate limit no Redis para chave {key}: {e}")
            # Em caso de falha de conexão do Redis, permite a requisição (fail-open) com log
            return False, 0


_rate_limit_instance: Optional[AbstractRateLimitService] = None


def get_rate_limit_service() -> AbstractRateLimitService:
    global _rate_limit_instance
    if _rate_limit_instance is None:
        if settings.REDIS_URL:
            try:
                _rate_limit_instance = RedisRateLimitService(settings.REDIS_URL)
                logger.info("RateLimitService inicializado utilizando REDIS.")
            except Exception as e:
                logger.warning(f"Falha ao conectar Redis para rate limit ({e}). Utilizando memória.")
                _rate_limit_instance = MemoryRateLimitService()
        else:
            _rate_limit_instance = MemoryRateLimitService()
    return _rate_limit_instance

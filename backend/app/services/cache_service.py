from abc import ABC, abstractmethod
import time
from typing import Dict, Optional, Tuple
from app.core.config import settings
from app.core.logging import logger


class AbstractCacheService(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass


class MemoryCacheService(AbstractCacheService):
    """Implementação em memória thread/asyncio-safe para MVP sem dependência de Redis."""

    def __init__(self):
        # key -> (value, expiry_timestamp)
        self._store: Dict[str, Tuple[str, Optional[float]]] = {}

    def get(self, key: str) -> Optional[str]:
        if key not in self._store:
            return None
        value, expiry = self._store[key]
        if expiry and time.time() > expiry:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        expiry = time.time() + ttl_seconds if ttl_seconds else None
        self._store[key] = (value, expiry)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        return self.get(key) is not None


class RedisCacheService(AbstractCacheService):
    """Implementação baseada em Redis para cache distribuído quando REDIS_URL está configurado."""

    def __init__(self, redis_url: str):
        import redis
        self._client = redis.from_url(redis_url, decode_responses=True)

    def get(self, key: str) -> Optional[str]:
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error(f"Erro ao ler chave {key} do Redis: {e}")
            return None

    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        try:
            self._client.set(key, value, ex=ttl_seconds)
        except Exception as e:
            logger.error(f"Erro ao salvar chave {key} no Redis: {e}")

    def delete(self, key: str) -> None:
        try:
            self._client.delete(key)
        except Exception as e:
            logger.error(f"Erro ao deletar chave {key} do Redis: {e}")

    def exists(self, key: str) -> bool:
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"Erro ao verificar existência da chave {key} no Redis: {e}")
            return False


# Singleton do CacheService com fallback inteligente
_cache_instance: Optional[AbstractCacheService] = None


def get_cache_service() -> AbstractCacheService:
    global _cache_instance
    if _cache_instance is None:
        if settings.REDIS_URL:
            try:
                _cache_instance = RedisCacheService(settings.REDIS_URL)
                logger.info("CacheService inicializado utilizando REDIS.")
            except Exception as e:
                logger.warning(f"Falha ao conectar no Redis ({e}). Utilizando MemoryCacheService como fallback.")
                _cache_instance = MemoryCacheService()
        else:
            logger.info("REDIS_URL não informada. Utilizando MemoryCacheService (In-Memory).")
            _cache_instance = MemoryCacheService()
    return _cache_instance

from abc import ABC, abstractmethod
import time
from typing import Dict, Optional
from app.core.config import settings
from app.core.logging import logger


class AbstractLockService(ABC):
    @abstractmethod
    def acquire(self, key: str, timeout_seconds: int = 10) -> bool:
        pass

    @abstractmethod
    def release(self, key: str) -> None:
        pass


class MemoryLockService(AbstractLockService):
    def __init__(self):
        self._locks: Dict[str, float] = {}

    def acquire(self, key: str, timeout_seconds: int = 10) -> bool:
        now = time.time()
        # Se o lock expirou, remove
        if key in self._locks and now > self._locks[key]:
            del self._locks[key]

        if key in self._locks:
            return False  # Já bloqueado

        self._locks[key] = now + timeout_seconds
        return True

    def release(self, key: str) -> None:
        self._locks.pop(key, None)


class RedisLockService(AbstractLockService):
    def __init__(self, redis_url: str):
        import redis
        self._client = redis.from_url(redis_url, decode_responses=True)

    def acquire(self, key: str, timeout_seconds: int = 10) -> bool:
        try:
            lock_key = f"lock:{key}"
            # SET NX EX
            return bool(self._client.set(lock_key, "1", nx=True, ex=timeout_seconds))
        except Exception as e:
            logger.error(f"Erro ao adquirir lock no Redis para {key}: {e}")
            return True  # Fail-open para não travar o fluxo

    def release(self, key: str) -> None:
        try:
            self._client.delete(f"lock:{key}")
        except Exception as e:
            logger.error(f"Erro ao liberar lock no Redis para {key}: {e}")


_lock_instance: Optional[AbstractLockService] = None


def get_lock_service() -> AbstractLockService:
    global _lock_instance
    if _lock_instance is None:
        if settings.REDIS_URL:
            try:
                _lock_instance = RedisLockService(settings.REDIS_URL)
            except Exception:
                _lock_instance = MemoryLockService()
        else:
            _lock_instance = MemoryLockService()
    return _lock_instance

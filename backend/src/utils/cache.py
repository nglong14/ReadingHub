import os
import redis
import hashlib
import json
import logging
import numpy as np
from typing import Optional, List

logger = logging.getLogger(__name__)

# Read Redis config from environment (for Cloud deployment)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


class EmbeddingCache:

    def __init__(self, host=None, port=None, ttl=86400):
        host = host or REDIS_HOST
        port = port or REDIS_PORT
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=False)
        self.ttl = ttl

    def is_healthy(self) -> bool:
        """Return True if Redis is reachable."""
        try:
            return self.redis_client.ping()
        except Exception:
            return False

    def _generate_key(self, text: str) -> str:
        """Generate unique cache key from text."""
        return f"emb:{hashlib.md5(text.encode()).hexdigest()}"

    def get(self, text: str) -> Optional[List[float]]:
        """Retrieve cached embedding for text. Returns None if Redis is unavailable."""
        key = self._generate_key(text)
        try:
            cached = self.redis_client.get(key)
            if cached:
                return np.frombuffer(cached, dtype=np.float32).tolist()
        except Exception as e:
            logger.warning("EmbeddingCache.get failed (Redis unavailable): %s", e)
        return None

    def set(self, text: str, embedding: List[float]):
        """Store embedding in cache. Silently skips if Redis is unavailable."""
        key = self._generate_key(text)
        try:
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
            self.redis_client.setex(key, self.ttl, embedding_bytes)
        except Exception as e:
            logger.warning("EmbeddingCache.set failed (Redis unavailable): %s", e)

    def clear(self):
        """Clear all embedding cache."""
        for key in self.redis_client.scan_iter(b"emb:*"):
            self.redis_client.delete(key)


class CachedSearch:

    def __init__(self, host=None, port=None, ttl=3600):
        host = host or REDIS_HOST
        port = port or REDIS_PORT
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.ttl = ttl

    def is_healthy(self) -> bool:
        """Return True if Redis is reachable."""
        try:
            return self.redis_client.ping()
        except Exception:
            return False

    def _generate_key(self, query: str, params: dict) -> str:
        cache_data = f"{query}:{json.dumps(params, sort_keys=True)}"
        return f"rec:{hashlib.md5(cache_data.encode()).hexdigest()}"

    def get(self, query: str, params: dict) -> Optional[List]:
        """Retrieve cached recommendations. Returns None if Redis is unavailable."""
        key = self._generate_key(query, params)
        try:
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning("CachedSearch.get failed (Redis unavailable): %s", e)
        return None

    def set(self, query: str, params: dict, recommendations: List):
        """Store recommendations in cache. Silently skips if Redis is unavailable."""
        key = self._generate_key(query, params)
        try:
            self.redis_client.setex(key, self.ttl, json.dumps(recommendations))
        except Exception as e:
            logger.warning("CachedSearch.set failed (Redis unavailable): %s", e)

    def clear(self):
        """Clear all recommendations cache."""
        for key in self.redis_client.scan_iter("rec:*"):
            self.redis_client.delete(key)
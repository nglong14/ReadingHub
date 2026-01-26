import redis
import hashlib
import json
import numpy as np
from typing import Optional, List

class EmbeddingCache:
    
    def __init__(self, host='localhost', port=6379, ttl=86400):
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=False)
        self.ttl = ttl
    
    def _generate_key(self, text: str) -> str:
        """Generate unique cache key from text."""
        return f"emb:{hashlib.md5(text.encode()).hexdigest()}"
    
    def get(self, text: str) -> Optional[List[float]]:
        """Retrieve cached embedding for text."""
        key = self._generate_key(text)
        cached = self.redis_client.get(key)
        if cached:
            # Deserialize numpy array from bytes
            return np.frombuffer(cached, dtype=np.float32).tolist()
        return None
    
    def set(self, text: str, embedding: List[float]):
        """Store embedding in cache."""
        key = self._generate_key(text)
        # Serialize as numpy array for efficient storage
        embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
        self.redis_client.setex(key, self.ttl, embedding_bytes)
    
    def clear(self):
        """Clear all embedding cache."""
        for key in self.redis_client.scan_iter(b"emb:*"):
            self.redis_client.delete(key)


class CachedSearch():
    def __init__(self, host='localhost', port=6379, ttl=3600):
        #Initialize
        self.redis_client = redis.Redis(host = host, port = port, decode_responses=True)
        self.ttl = ttl
    
    def _generate_key(self, query: str, params: dict) -> str:
        #Generate unique cached key from query and parameters
        cache_data = f"{query}:{json.dumps(params, sort_keys=True)}"
        return f"rec:{hashlib.md5(cache_data.encode()).hexdigest()}"

    def get(self, query: str, params: dict) -> Optional[List]:
        #Retrieve cached recommendations
        key = self._generate_key(query, params)
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def set(self, query: str, params: dict, recommendations: List):
        #Store recommendations in cache
        key = self._generate_key(query, params)
        self.redis_client.setex(key, self.ttl, json.dumps(recommendations))

    def clear(self):
        #Clear all recommendations cache:
        for key in self.redis_client.scan_iter("rec:*"):
            self.redis_client.delete(key)
import redis
import hashlib
import json
from typing import Optional, List

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
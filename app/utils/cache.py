import redis
from app.config import REDIS_HOST, REDIS_PORT
import json

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def cache_set(key: str, value: any, ttl: int = 3600):
    """Кэширует данные в Redis с заданным временем жизни (TTL)."""
    redis_client.setex(key, ttl, json.dumps(value))

def cache_get(key: str):
    """Получает данные из Redis, если они есть в кэше."""
    cached_value = redis_client.get(key)
    if cached_value:
        return json.loads(cached_value)
    return None

def cache_delete(key: str):
    """Удаляет данные из Redis по ключу."""
    if redis_client.exists(key):
        redis_client.delete(key)

def cache_update(key: str, value: any, ttl: int = 3600):
    """Обновляет данные в Redis по ключу."""
    if redis_client.exists(key):
        cache_set(key, value, ttl)
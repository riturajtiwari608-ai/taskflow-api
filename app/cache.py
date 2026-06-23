import json
from typing import Optional, Any

import redis
from redis.exceptions import RedisError

from app.config import REDIS_URL, CACHE_EXPIRE_SECONDS


redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def set_cache(key: str, value: Any, expire_seconds: int = CACHE_EXPIRE_SECONDS):
    try:
        redis_client.setex(
            key,
            expire_seconds,
            json.dumps(value)
        )
    except RedisError:
        pass


def get_cache(key: str) -> Optional[Any]:
    try:
        cached_value = redis_client.get(key)

        if cached_value is None:
            return None

        return json.loads(cached_value)

    except RedisError:
        return None


def delete_cache(key: str):
    try:
        redis_client.delete(key)
    except RedisError:
        pass


def delete_cache_pattern(pattern: str):
    try:
        keys = redis_client.keys(pattern)

        if keys:
            redis_client.delete(*keys)

    except RedisError:
        pass
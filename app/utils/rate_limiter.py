from fastapi import APIRouter, Depends, HTTPException, status, Request
from redis.exceptions import RedisError

from app.cache import redis_client


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "unknown"


def rate_limit(
    request: Request,
    key_prefix: str,
    limit: int,
    window_seconds: int
):
    client_ip = get_client_ip(request)

    redis_key = f"rate_limit:{key_prefix}:{client_ip}"

    try:
        current_count = redis_client.incr(redis_key)

        if current_count == 1:
            redis_client.expire(redis_key, window_seconds)

        if current_count > limit:
            ttl = redis_client.ttl(redis_key)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Please try again after {ttl} seconds."
            )

    except RedisError:
        return

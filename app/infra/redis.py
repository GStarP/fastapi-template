from redis import asyncio as aioredis

from .settings import SETTINGS

# TODO: test concurrency
# TODO: connection pool config
REDIS: aioredis.Redis = aioredis.from_url(
    url=SETTINGS.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
    retry_on_timeout=True,
)


def build_redis_key(key: str) -> str:
    return f"{SETTINGS.SERVICE_NAME}:{key}"

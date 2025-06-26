import logging

from redis import asyncio as aioredis

from .settings import settings

logger = logging.getLogger(__name__)

# TODO: test concurrency
# TODO: connection pool config
redis: aioredis.Redis = aioredis.from_url(
    url=settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
    retry_on_timeout=True,
)
logger.info(f"redis init")


def redis_prefix(key: str) -> str:
    return f"{settings.SERVICE_NAME}:{key}"
